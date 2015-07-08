import unittest

import numpy

import chainer
from chainer import cuda
from chainer import functions
from chainer import gradient_check
from chainer.testing import attr
from chainer.testing import condition


if cuda.available:
    cuda.init()


class TestSplitAxis0(unittest.TestCase):

    def setUp(self):
        self.x = numpy.arange(42, dtype=numpy.float32).reshape(2, 7, 3)
        self.ys = [self.x[:, :2], self.x[:, 2:5], self.x[:, 5:]]
        self.ys_section = [2, 5]
        self.axis = 1

    def check_forward(self, x_data, ys_data, indices_or_sections, axis):
        x = chainer.Variable(x_data)
        ys = functions.split_axis(x, indices_or_sections, axis)
        for yd, y in zip(ys_data, ys):
            gradient_check.assert_allclose(yd, y.data, atol=0, rtol=0)

    @condition.retry(3)
    def test_forward_cpu(self):
        self.check_forward(self.x, self.ys, self.ys_section, self.axis)

    @attr.gpu
    @condition.retry(3)
    def test_forward_gpu(self):
        self.check_forward(
            cuda.to_gpu(self.x),
            [cuda.to_gpu(y.copy()) for y in self.ys],
            self.ys_section, axis=self.axis)

    def check_backward(self, x_data, indices_or_sections, axis):
        x = chainer.Variable(x_data)
        ys = functions.split_axis(x, indices_or_sections, axis)
        for y in ys:
            y.grad = y.data
        ys[0].backward()

        gradient_check.assert_allclose(x.data, x.grad, atol=0, rtol=0)

    @condition.retry(3)
    def test_backward_cpu(self):
        self.check_backward(self.x, self.ys_section, axis=self.axis)

    @attr.gpu
    @condition.retry(3)
    def test_backward_gpu(self):
        self.check_backward(
            cuda.to_gpu(self.x), self.ys_section, axis=self.axis)


class TestSplitAxis1(TestSplitAxis0):

    def setUp(self):
        self.x = numpy.arange(21, dtype=numpy.float32).reshape(7, 3)
        self.ys = [self.x[:2], self.x[2:5], self.x[5:]]
        self.ys_section = [2, 5]
        self.axis = 0


class TestSplitAxis2(TestSplitAxis0):

    def setUp(self):
        self.x = numpy.arange(54, dtype=numpy.float32).reshape(2, 9, 3)
        self.ys = [self.x[:, :3], self.x[:, 3:6], self.x[:, 6:]]
        self.ys_section = 3
        self.axis = 1
