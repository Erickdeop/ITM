from simulator.parser import parse_netlist
def test_parse_example_dc():
    d = parse_netlist('circuits/example_dc.net')
    assert d.max_node >= 1
    assert len(d.elements) >= 2
