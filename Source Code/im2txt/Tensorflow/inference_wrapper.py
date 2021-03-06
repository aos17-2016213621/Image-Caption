from __future__ import absolute_import
from __future__ import division
from __future__ import print_function



import show_and_tell_model
import tensorflow as tf

class InferenceWrapper(object):
  """Model wrapper class for performing inference with a ShowAndTellModel."""

  def __init__(self):
    pass

  def build_model(self, model_config):
    model = show_and_tell_model.ShowAndTellModel(model_config, mode="inference")
    model.build()
    return model

  def _create_restore_fn(self, checkpoint_path, saver):
      """Creates a function that restores a model from checkpoint.
      Args:
        checkpoint_path: Checkpoint file or a directory containing a checkpoint
          file.
        saver: Saver for restoring variables from the checkpoint file.
      Returns:
        restore_fn: A function such that restore_fn(sess) loads model variables
          from the checkpoint file.
      Raises:
        ValueError: If checkpoint_path does not refer to a checkpoint file or a
          directory containing a checkpoint file.
      """
      if tf.gfile.IsDirectory(checkpoint_path):
          checkpoint_path = tf.train.latest_checkpoint(checkpoint_path)
          if not checkpoint_path:
              raise ValueError("No checkpoint file found in: %s" % checkpoint_path)

      def _restore_fn(sess):
          #tf.logging.info("Loading model from checkpoint: %s", checkpoint_path)
          saver.restore(sess, checkpoint_path)
          #tf.logging.info("Successfully loaded checkpoint: %s",
          #                os.path.basename(checkpoint_path))

      return _restore_fn

  def build_graph_from_config(self, model_config, checkpoint_path):
      """Builds the inference graph from a configuration object.
      Args:
        model_config: Object containing configuration for building the model.
        checkpoint_path: Checkpoint file or a directory containing a checkpoint
          file.
      Returns:
        restore_fn: A function such that restore_fn(sess) loads model variables
          from the checkpoint file.
      """
      tf.logging.info("Building model.")
      self.build_model(model_config)
      saver = tf.train.Saver()

      return self._create_restore_fn(checkpoint_path, saver)

  def feed_image(self, sess, encoded_image):
    initial_state = sess.run(fetches="lstm/initial_state:0",
                             feed_dict={"image_feed:0": encoded_image})
    return initial_state

  def inference_step(self, sess, input_feed, state_feed):
    softmax_output, state_output = sess.run(
        fetches=["softmax:0", "lstm/state:0"],
        feed_dict={
            "input_feed:0": input_feed,
            "lstm/state_feed:0": state_feed,
        })
    return softmax_output, state_output, None