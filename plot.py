import argparse
import os
import numpy as np
from io import StringIO

import matplotlib.pyplot as plt
from simulator.circuit import Circuit
from simulator.parser import parse_netlist
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
# 1b) Criar nomes significativos para nós baseado no circuito
# ------------------------------------------------------------
def get_node_labels(netlist_path: str, nodes: List[int]) -> Dict[int, str]:
    filename = os.path.basename(netlist_path).lower()
    
    # Mapeamentos específicos por circuito
    if "opamp_rectifier" in filename:
        labels = {1: "Vin", 2: "OpAmp1_in", 3: "OpAmp1_out", 
                 4: "Diode_mid", 5: "Diode_out", 6: "OpAmp2_in", 7: "Vout"}
    elif "oscilator" in filename or "oscillator" in filename:
        labels = {1: "Vout", 2: "RC1", 3: "RC2", 4: "OpAmp_out", 5: "Diode"}
    elif "lc" in filename:
        labels = {1: "LC1", 2: "LC2", 3: "LC3", 4: "V4", 5: "V5", 6: "Vout"}
    elif "chua" in filename:
        labels = {1: "V_L", 2: "V_C"}
    elif "dc_source" in filename:
        labels = {1: "Vin", 2: "Vout"}
    elif "pulse" in filename:
        labels = {1: "Vin", 2: "Vout"}
    elif "sinusoidal" in filename:
        labels = {1: "Vin", 2: "Vout"}
    else:
        # Padrão genérico
        labels = {i: f"Node_{i}" for i in nodes}
    
    # Retorna apenas os nós solicitados
    return {node: labels.get(node, f"Node_{node}") for node in nodes}

# ------------------------------------------------------------
# 2) Ler arquivo .sim de forma robusta (ignorando header textual)
# ------------------------------------------------------------
def load_sim_file(path: str):
    print(f"[DEBUG] Lendo arquivo .sim: {path}")

    # Read header to get node names
    header_line = None
    numeric_lines = []
    
    with open(path, "r") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue

            parts = line.split()
            try:
                float(parts[0])  # Se começar com número, é dado
                numeric_lines.append(line)
            except ValueError:
                # Não é numérico, pode ser header
                if header_line is None and parts:  # Pega primeiro header
                    header_line = parts
                continue

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
    vars_dict = {}
    if header_line and len(header_line) > 1:
        # First column is time, rest are nodes
        for i in range(1, min(data.shape[1], len(header_line))):
            node_name = header_line[i]
            vars_dict[f"Node {node_name}"] = data[:, i]
        # If more columns than header entries, use generic names
        for i in range(len(header_line), data.shape[1]):
            vars_dict[f"SIM_col_{i}"] = data[:, i]
    else:
        # No header, use generic names
        for i in range(1, data.shape[1]):
            vars_dict[f"SIM_col_{i}"] = data[:, i]

    print(f"[DEBUG] {len(time)} pontos carregados do .sim, {len(vars_dict)} variáveis")
    return time, vars_dict

# ------------------------------------------------------------
# 3) Plotar lado a lado: Simulação atual (Python) vs referência (.SIM)
# ------------------------------------------------------------
def plot_all(py_time: np.ndarray, py_vars: Dict[str, np.ndarray],
             sim_time: Optional[np.ndarray] = None,
             sim_vars: Optional[Dict[str, np.ndarray]] = None,
             save_path: Optional[str] = None):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5), sharey=True)

    # Plot da simulação Python
    for name, values in py_vars.items():
        ax1.plot(py_time, values, label=name, linewidth=1.5)
    ax1.set_title("Simulação Atual (Python)", fontsize=12, fontweight='bold')
    ax1.set_xlabel("Tempo (s)")
    ax1.set_ylabel("Tensão (V)")
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='best')

    # Plot da referência .SIM se existir
    if sim_time is not None and sim_vars is not None:
        for name, values in sim_vars.items():
            ax2.plot(sim_time, values, linestyle="--", label=name, linewidth=1.0, alpha=0.8)
        ax2.set_title("Referência (.SIM)", fontsize=12, fontweight='bold')
        ax2.set_xlabel("Tempo (s)")
        ax2.grid(True, alpha=0.3)
        ax2.legend(loc='best')
    else:
        ax2.set_title("Nenhum .SIM disponível")
        ax2.set_axis_off()

    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"[DEBUG] Gráfico salvo em: {save_path}")
    else:
        plt.show()

# ------------------------------------------------------------
# 4) CLI MAIN - chamadas de análise e plot limpas e compatíveis
# ------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Plot results of circuit simulation")
    parser.add_argument("--net", required=True, help="Caminho da netlist (.net)")
    parser.add_argument("--nodes", nargs="+", type=int, default=None,
                        help="Nós a serem plotados (padrão: todos os nós)")
    parser.add_argument("--output", "-o", help="Caminho para salvar o gráfico (PNG)")

    args = parser.parse_args()

    abs_path = os.path.abspath(args.net)
    print(f"[DEBUG] Lendo netlist: {abs_path}")

    # Parse da netlist para criar NetlistOOP
    netlist_oop = parse_netlist(abs_path)
    
    # Se nodes não especificado, usar todos os nós (exceto ground)
    if args.nodes is None:
        args.nodes = list(range(1, netlist_oop.max_node + 1))
        print(f"[DEBUG] Plotando todos os nós: {args.nodes}")
    
    # Criar circuito com NetlistOOP
    ckt = Circuit(netlist_oop)

    # Chamando a análise transient - usa configurações da netlist (.TRAN)
    py_time, py_out = ckt.run_tran(
        desired_nodes=args.nodes,
        nr_tol=1e-8,        # tolerância do Newton
        v0_vector=None      # usa default interno se None
    )

    # Obter labels significativos para os nós
    node_labels = get_node_labels(abs_path, args.nodes)
    
    # Montar dict do resultado Python para plot com labels
    py_vars = {
        node_labels[node]: py_out[i] for i, node in enumerate(args.nodes)
    }

    # Localizar e carregar .SIM se houver
    sim_file = find_sim_file(abs_path)
    sim_time, sim_vars = None, None

    if sim_file:
        print(f"[DEBUG] Comparando com: {sim_file}")
        sim_time, sim_vars = load_sim_file(sim_file)

    # Plotar lado a lado
    plot_all(py_time, py_vars, sim_time, sim_vars, save_path=args.output)


if __name__ == "__main__":
    main()
