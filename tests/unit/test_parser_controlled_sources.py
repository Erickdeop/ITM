import pytest
from simulator.parser import parse_netlist
from simulator.elements.controlled_sources import VCVS, CCCS, VCCS, CCVS


def test_parser_reads_vcvs():
    netlist = parse_netlist("circuits/example_vcvs.net")
    vcvs = next((e for e in netlist.elements if isinstance(e, VCVS)), None)
    
    assert vcvs is not None
    assert vcvs.gain == 10.0


def test_parser_reads_cccs():
    netlist = parse_netlist("circuits/example_cccs.net")
    cccs = next((e for e in netlist.elements if isinstance(e, CCCS)), None)
    
    assert cccs is not None
    assert cccs.gain == 5.0


def test_parser_reads_vccs():
    netlist = parse_netlist("circuits/example_vccs.net")
    vccs = next((e for e in netlist.elements if isinstance(e, VCCS)), None)
    
    assert vccs is not None
    assert vccs.gm == 0.01


def test_parser_reads_ccvs():
    netlist = parse_netlist("circuits/example_ccvs.net")
    ccvs = next((e for e in netlist.elements if isinstance(e, CCVS)), None)
    
    assert ccvs is not None
    assert ccvs.rm == 1000.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
