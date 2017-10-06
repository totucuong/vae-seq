"""Modules for encoding and decoding observations."""

import tensorflow as tf

from vaeseq import batch_distribution
from vaeseq import codec
from vaeseq import dist_module
from vaeseq import util


ObsEncoder = codec.MLPObsEncoder


class ObsDecoder(dist_module.DistModule):
    """Inputs -> Bernoulli activations."""

    def __init__(self, hparams, name=None):
        super(ObsDecoder, self).__init__(name=name)
        self._hparams = hparams

    @property
    def event_dtype(self):
        return tf.bool

    def dist(self, logits, name=None):
        """Constructs a Distribution from the output of the module."""
        name_prefix = name or self.module_name
        note_dist = tf.distributions.Bernoulli(
            logits=logits,
            dtype=self.event_dtype,
            name=name_prefix + "_note_dist")
        return batch_distribution.BatchDistribution(
            note_dist,
            ndims=1,
            name=name_prefix+"_scale_dist")

    def _build(self, *inputs):
        hparams = self._hparams
        layers = hparams.obs_decoder_fc_hidden_layers + hparams.obs_shape
        mlp = util.make_mlp(hparams, layers)
        return mlp(util.concat_features(inputs))