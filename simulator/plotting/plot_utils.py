import os
import numpy as np
import matplotlib.pyplot as plt


def find_sim_file(netlist_path: str):
    base = os.path.splitext(netlist_path)[0]
    sim_path = base + ".sim"
    return sim_path if os.path.exists(sim_path) else None


def load_sim_file(path: str):
    print(f"[DEBUG] Lendo arquivo .sim: {path}")
    try:
        # Força ignorar header textual caso exista
        data = np.loadtxt(path, comments="*", skiprows=1)
    except Exception as e:
        raise RuntimeError(f"[ERRO] Não consegui ler .sim: {e}")

    if data.ndim == 1:
        data = data.reshape(-1, 1)

    t = data[:, 0]
    vars_sim = {
        f"var_{i}": data[:, i]
        for i in range(1, data.shape[1])
    }
    return t, vars_sim


def plot_simulation(py_time: np.ndarray, py_out: np.ndarray, netlist_path: str):
    sim_path = find_sim_file(netlist_path)
    
    time_sim = None
    vars_sim = None
    if sim_path:
        time_sim, vars_sim = load_sim_file(sim_path)

    # criar 2 figuras lado a lado
    fig = plt.figure(figsize=(14, 6))
    ax_py, ax_sim = fig.subplots(1, 2)

    # Plot Python
    for i, values in enumerate(py_out):
        ax_py.plot(py_time, values, label=f"node_{i+1}")
    ax_py.set_title("Saída - Python")
    ax_py.set_xlabel("Tempo (s)")
    ax_py.set_ylabel("Valor")
    ax_py.grid(True)
    ax_py.legend()

    # Plot .SIM (referência)
    if vars_sim:
        for name, values in vars_sim.items():
            ax_sim.plot(time_sim, values, "--", label=name)

        ax_sim.set_title("Saída - .SIM (referência)")
        ax_sim.set_xlabel("Tempo (s)")
        ax_sim.grid(True)
        ax_sim.legend()

    else:
        ax_sim.set_title("Nenhum .SIM encontrado")
        ax_sim.set_axis_off()

    plt.tight_layout()
    plt.show()


def plot_from_netlist(netlist_path: str):
    from parser.netlist_parser import NetlistParser
    from core.mna_solver import MNASolver
    
    parser = NetlistParser(netlist_path)
    elementos, nodemap = parser.parse()
    solver = MNASolver(elementos, nodemap)

    py_time, A, b = solver.solve_dc()
    print("DC OK, rodando transitória...")

    h = 1e-6
    state = {}
    points = []
    for i in range(3):
        x, _, _ = solver.solve_transient(h, state)
        points.append(x)
        state = solver.next_state(x, h, state)

    py_out = np.array(points).T
    plot_simulation(py_time, py_out, netlist_path)
