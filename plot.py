import argparse
import os
import numpy as np
from io import StringIO

import matplotlib.pyplot as plt
from simulator.circuit import Circuit
from simulator.elements.base import TimeMethod
from typing import Tuple, Optional, List, Dict, Any

# ------------------------------------------------------------
# 1) Detectar arquivo .sim referente ao arquivo .net
# ------------------------------------------------------------
def find_sim_file(netlist_path: str):
    abs_net = os.path.abspath(netlist_path)
    base, _ = os.path.splitext(abs_net)
    sim_path = base + ".sim"
    return sim_path if os.path.exists(sim_path) else None

# ------------------------------------------------------------
# 2) Ler arquivo .sim de forma robusta (ignorando header textual)
# ------------------------------------------------------------
def load_sim_file(path: str):
    print(f"[DEBUG] Lendo arquivo .sim: {path}")

    numeric_lines = []
    with open(path, "r") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue

            parts = line.split()
            try:
                float(parts[0])  # mantém apenas se começar com número
            except ValueError:
                continue

            numeric_lines.append(line)

    if not numeric_lines:
        print("[DEBUG] Nenhum dado numérico detectado no .sim")
        return None, None

    buffer = StringIO("\n".join(numeric_lines))

    try:
        data = np.loadtxt(buffer)
    except Exception as e:
        print(f"[DEBUG] Falha na leitura numérica do .sim: {e}")
        return None, None

    if data.ndim == 1:
        data = data.reshape(-1, 1)

    time = data[:, 0]
    vars_dict = {
        f"SIM_col_{i}": data[:, i] for i in range(1, data.shape[1])
    }

    print(f"[DEBUG] {len(time)} pontos carregados do .sim")
    return time, vars_dict

# ------------------------------------------------------------
# 3) Plotar lado a lado: Simulação atual (Python) vs referência (.SIM)
# ------------------------------------------------------------
def plot_all(py_time: np.ndarray, py_vars: Dict[str, np.ndarray],
             sim_time: Optional[np.ndarray] = None,
             sim_vars: Optional[Dict[str, np.ndarray]] = None):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5), sharey=True)

    # Plot da simulação Python
    for name, values in py_vars.items():
        ax1.plot(py_time, values, label=name)
    ax1.set_title("Simulação Atual (Python)")
    ax1.set_xlabel("Tempo (s)")
    ax1.set_ylabel("Tensão / Valor")
    ax1.grid(True)
    ax1.legend()

    # Plot da referência .SIM se existir
    if sim_time is not None and sim_vars is not None:
        for name, values in sim_vars.items():
            ax2.plot(sim_time, values, linestyle="--", label=name)
        ax2.set_title("Referência (.SIM)")
        ax2.set_xlabel("Tempo (s)")
        ax2.grid(True)
        ax2.legend()
    else:
        ax2.set_title("Nenhum .SIM disponível")
        ax2.set_axis_off()

    plt.tight_layout()
    plt.show()

# ------------------------------------------------------------
# 4) CLI MAIN - chamadas de análise e plot limpas e compatíveis
# ------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Plot results of circuit simulation")
    parser.add_argument("--net", required=True, help="Caminho da netlist (.net)")
    parser.add_argument("--tran", required=True, nargs=2, metavar=("TSTOP", "DT"),
                        help="Executa análise transiente: tempo_stop dt")
    parser.add_argument("--method", choices=["BE", "FE", "TRAP"], default="BE",
                        help="Método de integração")
    parser.add_argument("--nodes", nargs="+", type=int, default=[1],
                        help="Nós a serem plotados")

    args = parser.parse_args()

    abs_path = os.path.abspath(args.net)
    print(f"[DEBUG] Lendo netlist: {abs_path}")

    # Carregar e executar transient com parâmetros válidos
    ckt = Circuit(abs_path)
    total_time = float(args.tran[0])
    dt = float(args.tran[1])

    method_map = {
        "BE": TimeMethod.BACKWARD_EULER,
        "FE": TimeMethod.FORWARD_EULER,
        "TRAP": TimeMethod.TRAPEZOIDAL,
    }
    method = method_map[args.method]

    # Chamando a análise transient apenas com args aceitos pela classe Circuit
    py_time, py_out = ckt.run_tran(
        desired_nodes=args.nodes,
        nr_tol=1e-8,        # tolerância do Newton, já validada
        v0_vector=None      # usa default interno se None
    )

    # Montar dict do resultado Python para plot
    py_vars = {
        f"Node_{node}": py_out[i] for i, node in enumerate(args.nodes)
    }

    # Localizar e carregar .SIM se houver
    sim_file = find_sim_file(abs_path)
    sim_time, sim_vars = None, None

    if sim_file:
        print(f"[DEBUG] Comparando com: {sim_file}")
        sim_time, sim_vars = load_sim_file(sim_file)

    # Plotar lado a lado
    plot_all(py_time, py_vars, sim_time, sim_vars)


if __name__ == "__main__":
    main()
