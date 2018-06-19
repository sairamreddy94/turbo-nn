"""Train a neural decoder"""
import argparse
import tensorflow as tf
from deepcom.decoder import convolutional_neural_decoder

# SEED here

def parse_args():
  """Parse Arguments for training Neural-RSC.
    NOTE: Default hyper-parameters are from suggested the original paper.
  """
  args = argparse.ArgumentParser(description='Train a Neural Decoder')
  args.add_argument('--batch_size', type=int, default=200)
  args.add_argument('--block_length', type=int, default=100)
  args.add_argument('--num_examples', type=int, default=12000)
  args.add_argument('--learning_rate', type=float, default=1e-3)
  return args.parse_args()


def main(args):
  print("Nahh")


def input_fn(inputs, labels, batch_size):
  """Data generator for neural decoder"""
  dataset = tf.data.Dataset.from_tensor_slices((inputs, labels))
  dataset = dataset.shuffle(1000).repeat().batch(batch_size)
  return dataset


def model_fn(inputs, labels, mode, params):
  """Define Training Pipeline for Neural Decoder"""
  is_training = (mode == tf.estimator.ModeKeys.TRAIN)
  decoded_signals = convolutional_neural_decoder(inputs, is_training)

  # Compute Loss
  loss = (decoded_signals - inputs)**2

  # TODO
  raise NotImplementedError



if __name__ == '__main__':
  arguments = parse_args()
  main(arguments)
