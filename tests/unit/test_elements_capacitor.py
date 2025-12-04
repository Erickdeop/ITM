import numpy as np, pytest
from simulator.elements.capacitor import Capacitor
from simulator.elements.base import TimeMethod

def test_capacitor_be_stamp():
    G = np.zeros((3,3)); I = np.zeros(3)
    c = Capacitor("C1", 1, 2, 1e-6)
    G2, I2, _ = c.stamp_transient(G.copy(), I.copy(), {}, t=0.0, dt=1e-3, method=TimeMethod.BACKWARD_EULER)
    Gc = 1e-6/1e-3
    assert G2[1,1] == pytest.approx(Gc)
    assert G2[2,2] == pytest.approx(Gc)
    assert G2[1,2] == pytest.approx(-Gc)
    assert G2[2,1] == pytest.approx(-Gc)

def test_capacitor_trap_stamp():
    G = np.zeros((3,3)); I = np.zeros(3)
    c = Capacitor("C1", 1, 2, 1e-6)
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

def test_capacitor_be_initial_condition_voltage():
    """
    Tests if the capacitor correctly uses the initial condition (Vc)
    when the state starts empty in Backward Euler method.
    """
    G = np.zeros((3, 3))
    I = np.zeros(3)

    c = Capacitor("C1", 1, 2, 1e-6, v0=5.0)

    G2, I2, _ = c.stamp_transient(
        G.copy(),
        I.copy(),
        {},  # empty state
        t=0.0,
        dt=1e-3,
        method=TimeMethod.BACKWARD_EULER,
    )

    Gc = 1e-6 / 1e-3  # C/dt

    import pytest
    assert G2[1, 1] == pytest.approx(Gc)
    assert G2[2, 2] == pytest.approx(Gc)
    assert G2[1, 2] == pytest.approx(-Gc)
    assert G2[2, 1] == pytest.approx(-Gc)

    # Initial conditions should appear as current sources
    assert I2[1] == pytest.approx(Gc * 5.0)   # +5e-3 A
    assert I2[2] == pytest.approx(-Gc * 5.0)  # -5e-3 A

