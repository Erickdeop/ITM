import numpy as np, pytest
from simulator.elements.capacitor import Capacitor
from simulator.elements.base import TimeMethod

def test_capacitor_be_stamp():
    G = np.zeros((3,3)); I = np.zeros(3)
    c = Capacitor(1, 2, 1e-6)
    G2, I2, _ = c.stamp_transient(G.copy(), I.copy(), {}, t=0.0, dt=1e-3, method=TimeMethod.BACKWARD_EULER)
    Gc = 1e-6/1e-3
    assert G2[1,1] == pytest.approx(Gc)
    assert G2[2,2] == pytest.approx(Gc)
    assert G2[1,2] == pytest.approx(-Gc)
    assert G2[2,1] == pytest.approx(-Gc)

def test_capacitor_trap_stamp():
    G = np.zeros((3,3)); I = np.zeros(3)
    c = Capacitor(1, 2, 1e-6)
    state = {'v_prev': 0.25, 'i_prev': 1e-3}
    G2, I2, _ = c.stamp_transient(G.copy(), I.copy(), state, t=0.0, dt=1e-3, method=TimeMethod.TRAPEZOIDAL)
    Gc = 2*1e-6/1e-3
    import pytest
    assert G2[1,1] == pytest.approx(Gc)
    assert G2[2,2] == pytest.approx(Gc)
    assert G2[1,2] == pytest.approx(-Gc)
    assert G2[2,1] == pytest.approx(-Gc)
    assert I2[1] == pytest.approx(Gc*0.25 + 1e-3)
    assert I2[2] == pytest.approx(-Gc*0.25 - 1e-3)
