"""This script generates synthetic data for training Neural 
Decoder. 

Given a ground truth message bits Y, we simulates input signal
passing through a Simple Modulation ( 0 --> 0, 1 --> 1 ) and 
Additive White Gaussian Noise (AWGN) Channel to become X, input
to the RNN (Neural) Decoder.

Usage:
-------
>>python generate_synthetic_dataset.py \
--num_training_sequences 1000 \
--num_testing_sequences  1000  \
--snr_test 0 1 2 3 4 5 6 \
--block_length 100 \
--num_cpu_cores 4 \
--training_seed 2018 \
--testing_seed 1111 \

"""
import pickle
import argparse
import random
import numpy as np
import commpy as cp
import multiprocessing as mp
from commpy.channelcoding import Trellis

from deepcom.utils import generate_message_bits, corrupt_signal

def parse_args():
  """Parse Arguments for training Neural-RSC."""
  args = argparse.ArgumentParser(description='Generate sythetic data for training neural decoder')
  args.add_argument('--block_length', type=int, default=100)
  args.add_argument('--num_cpu_cores', type=int, default=4)
  args.add_argument('--num_training_sequences', type=int, default=0)
  args.add_argument('--num_testing_sequences', type=int, default=0)
  args.add_argument('--training_seed', type=int, default=2018)
  args.add_argument('--testing_seed', type=int, default=1111)
  args.add_argument('--snr_test', type=float,  nargs="*", default=[0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0])
  return args.parse_args()


def run(args):
  #  Generator Matrix (octal representation)
  G = np.array([[0o7, 0o5]]) 
  M = np.array([3 - 1])
  trellis = Trellis(M, G, feedback=0o7, code_type='rsc')

  # ####################################
  # Generate Dataset for training/eval
  # ####################################
  snr_train = min(min(args.snr_test), 1)

  print('Generating training data...\n')
  X_train, Y_train = create_dataset(
      num_sequences=args.num_training_sequences,
      block_length=args.block_length,
      trellis=trellis,
      snr=snr_train,
      seed=args.training_seed,
      num_cpus=args.num_cpu_cores)

  print('Generating testing data....\n')
  X_test, Y_test = create_dataset(
      num_sequences=args.num_testing_sequences,
      block_length=args.block_length,
      trellis=trellis,
      snr=args.snr_test,
      seed=args.testing_seed,
      num_cpus=args.num_cpu_cores)

  print('Number of training sequences {}'.format(len(X_train)))
  print('Number of testing sequences {}\n'.format(len(X_test)))

  # ####################################
  # Save data into pickle object
  # ####################################    
  filename = 'rnn_bl{}_snr{}.dataset'.format(args.block_length, snr_train)
  with open(filename, 'wb') as f:
    pickle.dump([X_train, Y_train, X_test, Y_test], f)
    
  print('Dataset is saved to %s' % filename)

def create_dataset(num_sequences, block_length, trellis, snr, seed, num_cpus=4):
    # Init seed
    np.random.seed(seed)
    snr = snr + 10 * np.log10(1./2.)
    sigma = np.sqrt(1. / (2. * 10 **(snr / 10.)))

    with mp.Pool(processes=num_cpus) as pool:
      X, Y = zip(*pool.starmap(func, 
        [(block_length,trellis, sigma) for _ in range(num_sequences)]))

    np.random.seed()
    X = np.reshape(X, (-1, block_length, 2))
    Y = np.reshape(Y, (-1, block_length, 1))
    return X, Y


def func(block_length, trellis, sigma):
    """Function to help generate a pair of (input, label)
    for training Neural Decoder.
    """
    if type(sigma) is np.ndarray:
        sigma = np.random.choice(sigma)

    ground_truth = generate_message_bits(block_length)
    # Simulates data sent over AWGN channel
    coded_bits = cp.channelcoding.conv_encode(ground_truth, trellis)
    noisy_bits = corrupt_signal(coded_bits, noise_type='awgn', sigma=sigma)
    
    # Ignore the last 4 bits        
    input_signal = noisy_bits[: 2*block_length]
    return input_signal, ground_truth


if __name__ == '__main__':
    args = parse_args()
    run(args)