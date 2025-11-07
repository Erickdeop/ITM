from parser.netlist_parser import NetlistParser
from core.mna_solver import MNASolver

if __name__ == "__main__":
    parser = NetlistParser("examples/exemplo_rlc.txt")
    elementos, nodemap = parser.parse()

    solver = MNASolver(elementos, nodemap)

    # DC (apenas resistores)
    x, A, b = solver.solve_dc()
    print("Solução DC:")
    print("x =", x)

    # Simulação transitória (3 passos)
    h = 1e-6
    state = {}
    for i in range(3):
        x, _, _ = solver.solve_transient(h, state)
        print(f"\nPasso {i}:", x)
        state = solver.next_state(x, h, state)
