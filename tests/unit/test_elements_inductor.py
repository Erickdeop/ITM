import numpy as np
from simulator.elements.inductor import Inductor
from simulator.elements.base import TimeMethod
import pytest
def test_inductor_stamp_transient_backward_euler():
    L = Inductor(1, 0, 1e-3)
    G = np.zeros((2,2))
    I = np.zeros(2)

    state = {"i_prev": 0.01, "v_prev": 0.0}

    G2, I2, st2 = L.stamp_transient(
        G, I, state, t=0.001, dt=1e-5, method=TimeMethod.BACKWARD_EULER
    )

    # novo ramo => matriz cresce para 3x3
    assert G2.shape == (3,3)
    assert I2.shape == (3,)

    # R = L/dt = 1e-3 / 1e-5 = 100 ohms (equivalente)
    assert G2[2,2] == pytest.approx(100.0, rel=1e-3)
    assert I2[2] == pytest.approx(100.0 * 0.01, rel=1e-3)
