import itertools
import six

from chainer import cuda
from chainer import function
from chainer.utils import type_check


def _tile_indices(reps, shape):
    """Return tile indices from reps and shape of input array."""
    tile_indices = []
    ranges = [six.moves.range(x) for x in reps]
    for index in itertools.product(*ranges):
        tile_index = tuple(slice(i * d, (i + 1) * d)
                           for i, d in zip(index, shape))
        tile_indices.append(tile_index)
    return tile_indices


class Tile(function.Function):
    """Tiling of an array."""

    def __init__(self, reps):
        if isinstance(reps, six.integer_types):
            self.reps = (reps,)
        elif isinstance(reps, tuple) and all(
                isinstance(x, six.integer_types) for x in reps):
            self.reps = reps
        else:
            raise TypeError('reps must be int or tuple of ints')

        if not all(x >= 0 for x in self.reps):
            raise ValueError('all elements in reps must be zero or larger')

    def check_type_forward(self, in_types):
        type_check.expect(in_types.size() == 1)

    def forward(self, inputs):
        xp = cuda.get_array_module(*inputs)
        return xp.tile(inputs[0], self.reps),

    def backward(self, inputs, grads):
        xp = cuda.get_array_module(*inputs)
        x = inputs[0]
        reps = self.reps

        # Ensure input and reps have the same length.
        if x.ndim > len(reps):
            reps = (1,) * (x.ndim - len(reps)) + reps
        elif x.ndim < len(reps):
            x = x.reshape((1,) * (len(reps) - x.ndim) + x.shape)

        gy = xp.zeros(x.shape).astype(x.dtype, copy=False)
        for index in _tile_indices(reps, x.shape):
            gy += grads[0][index]

        if inputs[0].ndim < len(reps):
            return gy.reshape(inputs[0].shape),
        else:
            return gy,


def tile(x, reps):
    """Construct an array by tiling a given array.

    Args:
        x (chainer.Variable or :class:`numpy.ndarray` or cupy.ndarray):
            Input data.
        reps (int or tuple of ints): The number of times for each axis with
            which x is replicated.

    Returns:
        ~chainer.Variable: Variable tiled the given array.
    """
    return Tile(reps)(x)