# simulator/plot_utils.py
import numpy as np
import matplotlib.pyplot as plt
import os


def load_sim_file(path):
    data = None
    last_err = None

    for skip in (0, 1):
        try:
            print(f"[DEBUG] Tentando ler .sim com skiprows={skip}")
            data = np.loadtxt(path, skiprows=skip)
            break
        except Exception as e:
            last_err = e
            print(f"[PLOT] erro ao ler {path} com skiprows={skip}: {e}")

    if data is None:
        print(f"Erro ao ler arquivo .sim ({path}): {last_err}")
        return None, None

    if data.ndim == 1:
        data = data.reshape(1, -1)

    # primeira coluna = tempo
    time = data[:, 0]

    # demais colunas = variáveis
    variables = {
        f"SIM_col{i}": data[:, i]
        for i in range(1, data.shape[1])
    }

    print(f"[DEBUG] .sim carregado: {data.shape[0]} pontos, {data.shape[1]-1} variáveis")
    return time, variables


def plot_simulation(py_time, py_vars, sim_time=None, sim_vars=None):

    plt.figure(figsize=(12, 6))

    # Curvas Python
    for name, values in py_vars.items():
        plt.plot(py_time, values, label=f"PY: {name}")

    # Curvas SIM
    if sim_vars is not None:
        for name, values in sim_vars.items():
            plt.plot(sim_time, values, "--", label=f"SIM: {name}")

    plt.xlabel("Tempo (s)")
    plt.ylabel("Valor")
    plt.title("Simulação Transiente (Python vs .SIM)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()