import pytest
import numpy as np
from simulator.parser import parse_netlist
from simulator.engine import solve_dc


def test_vcvs_voltage_amplifier():
    netlist = parse_netlist("circuits/example_vcvs.net")
    v0 = np.zeros(netlist.max_node + 1)
    result = solve_dc(netlist, nr_tol=1e-6, v0_vector=v0, desired_nodes=None)
    
    # E1 amplifies by 10x, so node 2 should be 10V
    assert abs(result[1] - 1.0) < 1e-6
    assert abs(result[2] - 10.0) < 1e-6


def test_cccs_current_mirror():
    netlist = parse_netlist("circuits/example_cccs.net")
    v0 = np.zeros(netlist.max_node + 1)
    result = solve_dc(netlist, nr_tol=1e-6, v0_vector=v0, desired_nodes=None)
    
    # Circuit: V1=1V, R1=1k (node 1 to 2), CCCS gain=5 (measures current at node 2), R2=1k at node 3
    # i_control = 1mA, i_output = 5mA, V3 = 5V
    assert abs(result[1] - 1.0) < 1e-6
    assert abs(result[2] - 0.0) < 1e-6  # Short circuit for current measurement
    assert abs(result[3] - 5.0) < 1e-6


def test_vccs_transconductance():
    """Test VCCS circuit - transconductance amplifier"""
    netlist = parse_netlist("circuits/example_vccs.net")
    v0 = np.zeros(netlist.max_node + 1)
    result = solve_dc(netlist, nr_tol=1e-6, v0_vector=v0, desired_nodes=None)
    
    # V2 = I2 * R2 = 0.01 * 1000 = 10V
    assert abs(result[1] - 1.0) < 1e-6
    assert abs(result[2] - 10.0) < 1e-6


def test_ccvs_transresistance():
    """Test CCVS circuit - transresistance amplifier"""
    netlist = parse_netlist("circuits/example_ccvs.net")
    v0 = np.zeros(netlist.max_node + 1)
    result = solve_dc(netlist, nr_tol=1e-6, v0_vector=v0, desired_nodes=None)
    
    # Circuit: V1=1V, R1=1k (node 1 to 2), CCVS rm=1k (measures current at node 2, outputs to node 3)
    # i_control = 1mA, V_out = rm * i_control = 1V
    assert abs(result[1] - 1.0) < 1e-6
    assert abs(result[2] - 0.0) < 1e-6  # Short circuit for current measurement
    assert abs(result[3] - 1.0) < 1e-6


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
