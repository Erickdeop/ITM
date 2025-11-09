from simulator.parser import parse_netlist

def test_parser_builds_elements():
    data = parse_netlist('circuits/example_tran.net')
    types = {e.__class__.__name__ for e in data.elements}
    assert 'Resistor' in types
    assert 'Capacitor' in types
    assert 'VoltageSource' in types
    assert data.max_node >= 1
