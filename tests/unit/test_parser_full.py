from simulator.parser import parse_netlist

def test_parser_reads_all_supported_elements(tmp_path):
    net = tmp_path / "full_test.net"
    net.write_text("""
2                   
R1 1 2 1000
C1 2 0 1e-6
L1 1 0 1e-3
I1 1 0 DC 2.0
V1 2 0 AC 1.0 1000 0
""")

    data = parse_netlist(str(net))

    assert len(data.elements) == 5
    assert data.max_node == 2
