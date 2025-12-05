import pytest
import numpy as np
from simulator.parser import parse_netlist
from simulator.engine import solve_tran
from simulator.elements.base import TimeMethod


def create_netlist_file(tmp_path, content):
    p = tmp_path / "test.net"
    p.write_text(content, encoding="utf-8")
    return str(p)


def test_current_source_sin_oscillation(tmp_path):
    netlist = """
    * SIN current source
    1
    I1 0 1 SIN 0 0.001 1000 0 0 0
    R1 1 0 1000
    .TRAN 0.005 1e-6 BE 0
    """
    path = create_netlist_file(tmp_path, netlist)
    data = parse_netlist(path)
    times, outputs, _ = solve_tran(data, 0.005, 1e-6, 1e-6, None, [1], TimeMethod.BACKWARD_EULER)
    
    assert np.max(outputs[0, :]) > 0.1
    assert np.min(outputs[0, :]) < -0.1


def test_current_source_pulse_levels(tmp_path):
    netlist = """
    * PULSE current source
    1
    I1 0 1 PULSE 0 0.01 0.001 0.0001 0.0001 0.002 0.01
    R1 1 0 100
    .TRAN 0.025 1e-5 BE 0
    """
    path = create_netlist_file(tmp_path, netlist)
    data = parse_netlist(path)
    times, outputs, _ = solve_tran(data, 0.025, 1e-5, 1e-6, None, [1], TimeMethod.BACKWARD_EULER)
    
    idx_low = np.where(times < 0.0005)[0]
    idx_high = np.where((times > 0.002) & (times < 0.003))[0]
    
    assert np.max(np.abs(outputs[0, idx_low])) < 0.1
    assert np.mean(outputs[0, idx_high]) == pytest.approx(1.0, abs=0.1)


def test_parser_reads_sin_current(tmp_path):
    netlist = """
    * SIN current
    1
    I1 0 1 SIN 0.001 0.01 1000 0.002 10 45
    R1 1 0 100
    """
    path = create_netlist_file(tmp_path, netlist)
    data = parse_netlist(path)
    
    isrc = None
    for elem in data.elements:
        if elem.__class__.__name__ == "CurrentSource":
            isrc = elem
            break
    
    assert isrc is not None
    assert isrc.source_type == "SIN"
    assert isrc.sin_params["offset"] == pytest.approx(0.001)
    assert isrc.sin_params["amplitude"] == pytest.approx(0.01)


def test_parser_reads_pulse_current(tmp_path):
    netlist = """
    * PULSE current
    1
    I1 0 1 PULSE 0.001 0.010 0.002 0.0005 0.0003 0.003 0.010
    R1 1 0 50
    """
    path = create_netlist_file(tmp_path, netlist)
    data = parse_netlist(path)
    
    isrc = None
    for elem in data.elements:
        if elem.__class__.__name__ == "CurrentSource":
            isrc = elem
            break
    
    assert isrc is not None
    assert isrc.source_type == "PULSE"
    assert isrc.pulse_params["i1"] == pytest.approx(0.001)
    assert isrc.pulse_params["i2"] == pytest.approx(0.010)
