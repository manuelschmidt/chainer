import unittest

import numpy

from chainer import cuda
from chainer import functions
from chainer import gradient_check
from chainer import testing
from chainer.testing import attr
from chainer.utils import type_check


@testing.parameterize(*testing.product({
    'in_shape': [(), 2, (2, 3)],
    'reps': [(), 0, 2, (0, 0), (2, 2)],
#    'dtype': [numpy.float16, numpy.float32, numpy.float64],
    'dtype': [numpy.float32],
}))
class TestTile(unittest.TestCase):

    def setUp(self):
        self.x = numpy.random.uniform(-1, 1, self.in_shape).astype(self.dtype)
        out_shape = numpy.tile(self.x, self.reps).shape
        self.g = numpy.random.uniform(-1, 1, out_shape).astype(self.dtype)

    def check_forward(self, x_data):
        y = functions.tile(x_data, self.reps)
        y_expected = numpy.tile(self.x, self.reps)
        self.assertEqual(y.dtype, y_expected.dtype)
        testing.assert_allclose(y.data, y_expected)

    def test_forward_cpu(self):
        self.check_forward(self.x)

    @attr.gpu
    def test_forward_gpu(self):
        self.check_forward(cuda.to_gpu(self.x))

    def check_backward(self, x_data, g_data):
        gradient_check.check_backward(
            functions.Tile(self.reps), x_data, g_data)

    def test_backward_cpu(self):
        self.check_backward(self.x, self.g)

    @attr.gpu
    def test_backward_gpu(self):
        self.check_backward(cuda.to_gpu(self.x), cuda.to_gpu(self.g))


@testing.parameterize(*testing.product({
    'reps': [-1, (-1, -1)],
}))
class TestTileValueError(unittest.TestCase):

    def test_value_error(self):
        x = numpy.random.uniform(-1, 1, (2,)).astype(numpy.float32)
        with self.assertRaises(ValueError):
            functions.tile(x, self.reps)


class TestTileInvalidType(unittest.TestCase):

    def test_invalid_type(self):
        x = numpy.random.uniform(-1, 1, (2,)).astype(numpy.float32)
        with self.assertRaises(type_check.InvalidType):
            functions.Tile(2)(x, x)


class TestTileTypeError(unittest.TestCase):

    def test_type_error(self):
        x = numpy.random.uniform(-1, 1, (2,)).astype(numpy.float32)
        with self.assertRaises(TypeError):
            functions.tile(x, 'a')