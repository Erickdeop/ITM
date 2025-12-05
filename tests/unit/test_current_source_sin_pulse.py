import pytest
import numpy as np
from simulator.elements.current_source import CurrentSource


def test_current_source_sin_basic():
    sin_params = {
        "offset": 1.0,
        "amplitude": 2.0,
        "freq": 100.0,
        "delay": 0.0,
        "damping": 0.0,
        "phase": 0.0
    }
    isrc = CurrentSource(a=1, b=0, dc=1.0, source_type="SIN", sin_params=sin_params)
    
    assert isrc.get_value_at(0.0) == pytest.approx(1.0)
    assert isrc.get_value_at(0.0025) == pytest.approx(3.0, abs=1e-6)
    assert isrc.get_value_at(0.0075) == pytest.approx(-1.0, abs=1e-6)


def test_current_source_sin_with_delay():
    sin_params = {
        "offset": 2.0,
        "amplitude": 3.0,
        "freq": 100.0,
        "delay": 0.01,
        "damping": 0.0,
        "phase": 0.0
    }
    isrc = CurrentSource(a=1, b=0, dc=2.0, source_type="SIN", sin_params=sin_params)
    
    assert isrc.get_value_at(0.005) == pytest.approx(2.0, abs=1e-6)
    assert isrc.get_value_at(0.0125) == pytest.approx(5.0, abs=1e-6)


def test_current_source_sin_with_damping():
    sin_params = {
        "offset": 0.0,
        "amplitude": 10.0,
        "freq": 100.0,
        "delay": 0.0,
        "damping": 100.0,
        "phase": 0.0
    }
    isrc = CurrentSource(a=1, b=0, dc=0.0, source_type="SIN", sin_params=sin_params)
    
    val_early = abs(isrc.get_value_at(0.0025))
    val_late = abs(isrc.get_value_at(0.020))
    assert val_late < val_early


def test_current_source_pulse_states():
    pulse_params = {
        "i1": 1.0,
        "i2": 5.0,
        "delay": 0.0,
        "rise_time": 0.001,
        "fall_time": 0.001,
        "pulse_width": 0.002,
        "period": 0.01
    }
    isrc = CurrentSource(a=1, b=0, dc=1.0, source_type="PULSE", pulse_params=pulse_params)
    
    assert isrc.get_value_at(0.0) == pytest.approx(1.0)
    assert isrc.get_value_at(0.0005) == pytest.approx(3.0, abs=1e-6)
    assert isrc.get_value_at(0.002) == pytest.approx(5.0)
    assert isrc.get_value_at(0.0035) == pytest.approx(3.0, abs=1e-6)


def test_current_source_pulse_periodicity():
    pulse_params = {
        "i1": 0.0,
        "i2": 5.0,
        "delay": 0.0,
        "rise_time": 0.001,
        "fall_time": 0.001,
        "pulse_width": 0.002,
        "period": 0.010
    }
    isrc = CurrentSource(a=1, b=0, dc=0.0, source_type="PULSE", pulse_params=pulse_params)
    
    assert isrc.get_value_at(0.0005) == pytest.approx(isrc.get_value_at(0.0105), abs=1e-6)


def test_current_source_stamp_dc():
    isrc = CurrentSource(a=2, b=1, dc=3.0, source_type="DC")
    G = np.zeros((3, 3))
    I = np.zeros(3)
    G_new, I_new = isrc.stamp_dc(G, I)
    
    assert I_new[2] == pytest.approx(-3.0)
    assert I_new[1] == pytest.approx(3.0)
    assert np.array_equal(G_new, G)
