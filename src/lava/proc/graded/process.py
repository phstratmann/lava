# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
# See: https://spdx.org/licenses/

import os
import numpy as np
import typing as ty
from typing import Any, Dict
from enum import IntEnum, unique

from lava.magma.core.process.process import AbstractProcess
from lava.magma.core.process.variable import Var
from lava.magma.core.process.ports.ports import InPort, OutPort

from lava.magma.core.sync.protocols.loihi_protocol import LoihiProtocol
from lava.magma.core.model.py.ports import PyInPort, PyOutPort
from lava.magma.core.model.py.type import LavaPyType
from lava.magma.core.resources import CPU
from lava.magma.core.decorator import implements, requires, tag
from lava.magma.core.model.py.model import PyLoihiProcessModel


def loihi2round(vv):
    """round values in numpy array the way loihi 2 performs rounding/truncation."""
    return np.fix(vv + (vv > 0) - 0.5).astype('int')


class GradedVec(AbstractProcess):
    """GradedVec
    Thresholded graded spike vector

    Parameters
    ----------
    shape: tuple(int)
        number and topology of neurons
    vth: int
        threshold for spiking
    exp: int
        fixed point base
    """

    def __init__(
            self,
            *,
            shape: ty.Tuple[int, ...],
            vth=1,
            exp=0) -> None:

        super().__init__(shape=shape)

        self.a_in = InPort(shape=shape)
        self.s_out = OutPort(shape=shape)

        self.v = Var(shape=shape, init=0)
        self.vth = Var(shape=(1,), init=vth)
        self.exp = Var(shape=(1,), init=exp)

    @property
    def shape(self) -> ty.Tuple[int, ...]:
        """Return shape of the Process."""
        return self.proc_params['shape']


class NormVecDelay(AbstractProcess):
    """NormVec
    Normalizable graded spike vector

    Parameters
    ----------
    shape: tuple(int)
        number and topology of neurons
    vth: int
        threshold for spiking
    exp: int
        fixed point base
    """

    def __init__(
            self,
            *,
            shape: ty.Tuple[int, ...],
            vth=1,
            exp=0) -> None:

        super().__init__(shape=shape)

        self.a_in1 = InPort(shape=shape)
        self.a_in2 = InPort(shape=shape)

        self.s_out = OutPort(shape=shape)
        self.s2_out = OutPort(shape=shape)

        self.vth = Var(shape=(1,), init=vth)
        self.exp = Var(shape=(1,), init=exp)

        self.v = Var(shape=shape, init=np.zeros(shape, 'int32'))
        self.v2 = Var(shape=shape, init=np.zeros(shape, 'int32'))

    @property
    def shape(self) -> ty.Tuple[int, ...]:
        """Return shape of the Process."""
        return self.proc_params['shape']


class InvSqrt(AbstractProcess):
    """InvSqrt
    Neuron model for computing inverse square root with 24-bit
    fixed point values.

    Parameters
    ----------
    fp_base : int
        Base of the fixed-point representation
    """

    def __init__(
            self,
            *,
            shape: ty.Tuple[int, ...],
            fp_base=12) -> None:
        super().__init__(shape=shape)

        # base of the decimal point
        self.fp_base = Var(shape=(1,), init=fp_base)
        self.a_in = InPort(shape=shape)
        self.s_out = OutPort(shape=shape)

    @property
    def shape(self) -> ty.Tuple[int, ...]:
        """Return shape of the Process."""
        return self.proc_params['shape']
