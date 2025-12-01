import pytest
import math
from simulator.parser import parse_netlist
from simulator.elements.voltage_source import VoltageSource


# Basic temporal behavior tests
def test_dc_source_constant_value():
    v = VoltageSource(a=1, b=0, dc=10.0, source_type="DC")

    assert v.get_value_at(0.0) == 10.0
    assert v.get_value_at(1.0) == 10.0


def test_ac_source_sin_value():
    v = VoltageSource(a=1, b=0, dc=0.0, amp=1.0, freq=1.0, 
                     phase_deg=0.0, is_ac=True, source_type="AC")
    
    assert abs(v.get_value_at(0.0) - 1.0) < 1e-10  # t=0: cos(0) = 1
    assert abs(v.get_value_at(0.5) + 1.0) < 1e-10  # t=0.5: cos(π) = -1


# SIN source tests
def test_sin_basic_waveform():
    sin_params = {"offset": 0.0, "amplitude": 1.0, "freq": 1.0, 
                  "delay": 0.0, "damping": 0.0, "phase": 0.0}
    
    v = VoltageSource(a=1, b=0, source_type="SIN", sin_params=sin_params)

    assert abs(v.get_value_at(0.0)) < 1e-10      # sin(0) = 0
    assert abs(v.get_value_at(0.25) - 1.0) < 1e-10  # sin(π/2) = 1


def test_sin_with_offset_and_phase():
    sin_params = {"offset": 5.0, "amplitude": 2.0, "freq": 1.0,
                  "delay": 0.0, "damping": 0.0, "phase": 90.0}
    
    v = VoltageSource(a=1, b=0, source_type="SIN", sin_params=sin_params)

    assert abs(v.get_value_at(0.0) - 7.0) < 1e-10  # 5 + 2*sin(90°) = 7


def test_sin_time_delay():
    sin_params = {"offset": 3.0, "amplitude": 1.0, "freq": 1.0,
                  "delay": 0.5, "damping": 0.0, "phase": 0.0}
    
    v = VoltageSource(a=1, b=0, source_type="SIN", sin_params=sin_params)

    assert v.get_value_at(0.0) == 3.0  # before delay: offset only
    assert abs(v.get_value_at(0.75) - 4.0) < 1e-10  # after delay: sin wave


def test_pulse_initial_value():
    pulse_params = {"v1": 0.0, "v2": 5.0, "delay": 1.0, "rise_time": 0.1,
                    "fall_time": 0.1, "pulse_width": 0.5, "period": 2.0}
    
    v = VoltageSource(a=1, b=0, source_type="PULSE", pulse_params=pulse_params)

    assert v.get_value_at(0.0) == 0.0


def test_pulse_rise_and_plateau():
    pulse_params = {"v1": 0.0, "v2": 10.0, "delay": 0.0, "rise_time": 1.0,
                    "fall_time": 0.1, "pulse_width": 1.0, "period": 3.0}
    
    v = VoltageSource(a=1, b=0, source_type="PULSE", pulse_params=pulse_params)

    assert abs(v.get_value_at(0.5) - 5.0) < 1e-10   # on rise
    assert abs(v.get_value_at(1.5) - 10.0) < 1e-10  # plateau


def test_pulse_periodicity():
    pulse_params = {"v1": 0.0, "v2": 5.0, "delay": 0.0, "rise_time": 0.1,
                    "fall_time": 0.1, "pulse_width": 0.3, "period": 1.0}
    
    v = VoltageSource(a=1, b=0, source_type="PULSE", pulse_params=pulse_params)

    v1 = v.get_value_at(0.25)
    v2 = v.get_value_at(1.25)  # one period later
    assert abs(v1 - v2) < 1e-10


# Parser integration tests
def test_parser_reads_sin_netlist():
    netlist = parse_netlist("circuits/sinusoidal.net")
    
    sin_source = _find_voltage_source_by_type(netlist.elements, "SIN")
    
    assert sin_source is not None
    assert sin_source.sin_params["amplitude"] == 5.0


def test_parser_reads_pulse_netlist():
    netlist = parse_netlist("circuits/pulse.net")
    
    pulse_source = _find_voltage_source_by_type(netlist.elements, "PULSE")
    
    assert pulse_source is not None
    assert pulse_source.pulse_params["v2"] == 5.0


def _find_voltage_source_by_type(elements, source_type):
    for element in elements:
        if not isinstance(element, VoltageSource):
            continue
        if element.source_type == source_type:
            return element
    return None


# Backward compatibility
def test_old_dc_and_ac_sources():
    dc = VoltageSource(a=1, b=0, dc=10.0, is_ac=False, source_type="DC")
    assert dc._value(0.0) == 10.0
    
    ac = VoltageSource(a=1, b=0, dc=0.0, amp=1.0, freq=1.0, 
                      phase_deg=0.0, is_ac=True, source_type="AC")
    assert abs(ac._value(0.0) - 1.0) < 1e-10
