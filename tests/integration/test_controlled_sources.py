import pytest
import numpy as np
from simulator.parser import parse_netlist
from simulator.engine import solve_dc


def test_vcvs_voltage_amplifier():
    netlist = parse_netlist("circuits/vcvs_test.net")
    v0 = np.zeros(netlist.max_node + 1)
    result = solve_dc(netlist, nr_tol=1e-6, v0_vector=v0, desired_nodes=None)
    
    # E1 amplifies by 10x, so node 2 should be 10V
    assert abs(result[1] - 1.0) < 1e-6
    assert abs(result[2] - 10.0) < 1e-6


def test_cccs_current_mirror():
    netlist = parse_netlist("circuits/cccs_test.net")
    v0 = np.zeros(netlist.max_node + 1)
    result = solve_dc(netlist, nr_tol=1e-6, v0_vector=v0, desired_nodes=None)
    
    # F1 receive gain 5, so current should be 5mA
    assert abs(result[1] - 1.0) < 1e-6
    assert abs(result[2] - 5.0) < 1e-6


def test_vccs_transconductance():
    """Test VCCS circuit - transconductance amplifier"""
    netlist = parse_netlist("circuits/vccs_test.net")
    v0 = np.zeros(netlist.max_node + 1)
    result = solve_dc(netlist, nr_tol=1e-6, v0_vector=v0, desired_nodes=None)
    
    # V2 = I2 * R2 = 0.01 * 1000 = 10V
    assert abs(result[1] - 1.0) < 1e-6
    assert abs(result[2] - 10.0) < 1e-6


def test_ccvs_transresistance():
    """Test CCVS circuit - transresistance amplifier"""
    netlist = parse_netlist("circuits/ccvs_test.net")
    v0 = np.zeros(netlist.max_node + 1)
    result = solve_dc(netlist, nr_tol=1e-6, v0_vector=v0, desired_nodes=None)
    
    # V1 should be close to 0 (short circuit for current measurement)
    assert abs(result[1]) < 1e-6  # Short circuit
    assert abs(result[2] - 1.0) < 1e-6


def test_vcvs_inverting():
    from simulator.elements.voltage_source import VoltageSource
    from simulator.elements.resistor import Resistor
    from simulator.elements.controlled_sources import VCVS
    from simulator.parser import NetlistOOP, TransientSettings
    
    elements = [
        VoltageSource(1, 0, dc=5.0, source_type="DC"),
        VCVS(2, 0, 1, 0, gain=-1.0),
        Resistor(1, 0, 1000.0),
        Resistor(2, 0, 1000.0)
    ]
    
    netlist = NetlistOOP(elements, 2, TransientSettings())
    v0 = np.zeros(netlist.max_node + 1)
    result = solve_dc(netlist, nr_tol=1e-6, v0_vector=v0, desired_nodes=None)
    
    assert abs(result[1] - 5.0) < 1e-6
    assert abs(result[2] + 5.0) < 1e-6  # Inverted


def test_vccs_zero_control():
    from simulator.elements.voltage_source import VoltageSource
    from simulator.elements.resistor import Resistor
    from simulator.elements.controlled_sources import VCCS
    from simulator.parser import NetlistOOP, TransientSettings
    
    elements = [
        VoltageSource(1, 0, dc=0.0, source_type="DC"),
        VCCS(2, 0, 1, 0, gm=0.01),
        Resistor(1, 0, 1000.0),
        Resistor(2, 0, 1000.0)
    ]
    
    netlist = NetlistOOP(elements, 2, TransientSettings())
    v0 = np.zeros(netlist.max_node + 1)
    result = solve_dc(netlist, nr_tol=1e-6, v0_vector=v0, desired_nodes=None)
    
    assert abs(result[1]) < 1e-6
    assert abs(result[2]) < 1e-6  # No current, no voltage


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
