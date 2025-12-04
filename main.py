import argparse
from typing import Tuple
from pathlib import Path

from simulator.parser import parse_netlist
from simulator.circuit import Circuit
from simulator.builder import CircuitBuilder
from plot import find_sim_file, load_sim_file, plot_all 

NETLIST_OUTPUT_DIR = Path("./created_net_files")

# ------------------------------------------------#
#             ADD COMPONENT TO CIRCUIT            #
# ------------------------------------------------#

def add_component (builder: CircuitBuilder):
    print(f"\n==> ADICIONANDO COMPONENTE À {builder.name}")
    print("\tTIPO DO COMPONENTE:")
    print("\tR: Resistor")
    print("\tC: Capacitor")
    print("\tL: Indutor")
    print("\tI: Fonte de corrente")
    print("\tV: Fonte de tensão")
    print("\tN: Resistor não-linear")
    print("\tD: Diodo")
    print("\tE: Fonte VCVS (tensão controlada por tensão)")
    print("\tF: Fonte CCCS (corrente controlada por corrente)")
    print("\tG: Fonte VCCS (corrente controlada por tensão)")
    print("\tH: Fonte CCVS (tensão controlada por corrente)")
    print("\tO: Amplificador operacional ideal")
    ctype = input("Escolha um componente:\n>> ").strip().upper()

    # ---------------------- LINEAR ELEMENTS ----------------------
    if ctype == "R":
        a = int(input("\tNó positivo: "))
        b = int(input("\tNó negativo: "))
        R = float(input("\tResistência [ohms]: "))
        builder.add_resistor(a, b, R)

    elif ctype == "C":
        a = int(input("\tNó positivo: "))
        b = int(input("\tNó negativo: "))
        C = float(input("\tCapacitância [F]: "))
        ic = float(input("\tTensão inicial [V] (0 se não houver): ") or "0")
        builder.add_capacitor(a, b, C, ic)
    elif ctype == "L":
        a = int(input("\tNó positivo: "))
        b = int(input("\tNó negativo: "))
        C = float(input("\tIndutância [H]: "))
        ic = float(input("\tTensão inicial [V] (0 se não houver): ") or "0")
        builder.add_inductor(a, b, C, ic)

     # ---------------------- CURRENT SOURCE ----------------------
    elif ctype == "I":
        a = int(input("\tNó positivo: "))
        b = int(input("\tNó negativo: "))
        stype = input("\tTipo de fonte (DC/AC): ").strip().upper() or "DC"

        if stype == "DC":
            dc = float(input("\tCorrente DC [A]: "))
            builder.add_current_source_dc(a, b, dc)
            print("\tFonte de corrente DC adicionada com sucesso.")
        elif stype == "AC":
            dc = float(input("\tComponente DC [A] (0 se não houver): ") or "0")
            amp = float(input("\tAmplitude AC [A]: "))
            freq = float(input("\tFrequência [Hz]: "))
            phase = float(input("\tFase [graus] (0 se não houver): ") or "0")
            builder.add_current_source_ac(a, b, dc, amp, freq, phase)
            print("\tFonte de corrente AC adicionada com sucesso.")
        else:
            print("\033[31mTipo de fonte de corrente não reconhecido.\033[0m")

    # ---------------------- VOLTAGE SOURCE ----------------------
    elif ctype == "V":
        a = int(input("\tNó positivo: "))
        b = int(input("\tNó negativo: "))
        print("\tTipo de fonte de tensão:")
        print("\t  DC   - fonte de tensão contínua")
        print("\t  AC   - fonte senoidal AC (amplitude/frequência)")
        print("\t  SIN  - fonte senoide do tipo SPICE (offset, amplitude, etc.)")
        print("\t  PULSE- fonte pulsada (PULSE)")
        stype = input("\tTipo (DC/AC/SIN/PULSE): ").strip().upper() or "DC"

        if stype == "DC":
            dc = float(input("\tTensão DC [V]: "))
            builder.add_voltage_source_dc(a, b, dc)
            print("\tFonte de tensão DC adicionada com sucesso.")

        elif stype == "AC":
            dc = float(input("\tComponente DC [V] (0 se não houver): ") or "0")
            amp = float(input("\tAmplitude AC [V]: "))
            freq = float(input("\tFrequência [Hz]: "))
            phase = float(input("\tFase [graus] (0 se não houver): ") or "0")
            builder.add_voltage_source_ac(a, b, dc, amp, freq, phase)
            print("\tFonte de tensão AC adicionada com sucesso.")

        elif stype == "SIN":
            offset = float(input("\tOffset [V] (0 se não houver): ") or "0")
            amplitude = float(input("\tAmplitude [V]: "))
            freq = float(input("\tFrequência [Hz]: "))
            delay = float(input("\tAtraso [s] (0 se não houver): ") or "0")
            damping = float(input("\tAtenuação (damping) (0 se não houver): ") or "0")
            phase = float(input("\tFase [graus] (0 se não houver): ") or "0")
            builder.add_voltage_source_sin(
                a, b, offset, amplitude, freq, delay, damping, phase
            )
            print("\tFonte de tensão SIN adicionada com sucesso.")

        elif stype == "PULSE":
            v1 = float(input("\tV1 [V] (nível baixo): "))
            v2 = float(input("\tV2 [V] (nível alto): "))
            delay = float(input("\tAtraso [s] (0 se não houver): ") or "0")
            rise_time = float(input("\tTempo de subida [s]: ") or "0")
            fall_time = float(input("\tTempo de descida [s]: ") or "0")
            pulse_width = float(input("\tLargura do pulso [s]: ") or "0")
            period = float(input("\tPeríodo [s]: ") or "0")
            builder.add_voltage_source_pulse(
                a, b, v1, v2, delay, rise_time, fall_time, pulse_width, period
            )
            print("\tFonte de tensão PULSE adicionada com sucesso.")
        else:
            print("\033[31mTipo de fonte de tensão não reconhecido.\033[0m")
            
    # ---------------------- CONTROLLED SOURCES ----------------------
    elif ctype == "E":
        print("\n==> Fonte VCVS (E): tensão controlada por tensão")
        a = int(input("\tNó de saída +: "))
        b = int(input("\tNó de saída -: "))
        c = int(input("\tNó de controle +: "))
        d = int(input("\tNó de controle -: "))
        gain = float(input("\tGanho (Vout / Vctrl): "))
        builder.add_vcvs(a, b, c, d, gain)
        print("\tVCVS adicionada com sucesso.")

    elif ctype == "F":
        print("\n==> Fonte CCCS (F): corrente controlada por corrente")
        a = int(input("\tNó de saída +: "))
        b = int(input("\tNó de saída -: "))
        c = int(input("\tNó do ramo de controle +: "))
        d = int(input("\tNó do ramo de controle -: "))
        gain = float(input("\tGanho (Iout / Ictrl): "))
        builder.add_cccs(a, b, c, d, gain)
        print("\tCCCS adicionada com sucesso.")

    elif ctype == "G":
        print("\n==> Fonte VCCS (G): corrente controlada por tensão")
        a = int(input("\tNó de saída +: "))
        b = int(input("\tNó de saída -: "))
        c = int(input("\tNó de controle +: "))
        d = int(input("\tNó de controle -: "))
        gm = float(input("\tTranscondutância gm [A/V]: "))
        builder.add_vccs(a, b, c, d, gm)
        print("\tVCCS adicionada com sucesso.")

    elif ctype == "H":
        print("\n==> Fonte CCVS (H): tensão controlada por corrente")
        a = int(input("\tNó de saída +: "))
        b = int(input("\tNó de saída -: "))
        c = int(input("\tNó do ramo de controle +: "))
        d = int(input("\tNó do ramo de controle -: "))
        rm = float(input("\tTransresistência rm [V/A]: "))
        builder.add_ccvs(a, b, c, d, rm)
        print("\tCCVS adicionada com sucesso.")

    # ------------------------- AmpOp -----------------------
    elif ctype == "O":
        print("\n==> Amplificador operacional ideal (O)")
        vp = int(input("\tNó de entrada não-inversora (+): "))
        vn = int(input("\tNó de entrada inversora (-): "))
        vo = int(input("\tNó de saída: "))
        gain_str = input("\tGanho (padrão = 1e5, Enter para padrão): ").strip()
        gain = float(gain_str) if gain_str else 1e5
        builder.add_opamp(vp, vn, vo, gain)
        print("\tAmplificador operacional ideal adicionado com sucesso.")

    # ---------------------- NON LINEAR ELEMENTS ----------------------
    elif ctype == "N":
        a = int(input("\tNó positivo: "))
        b = int(input("\tNó negativo: "))
        print("\tDefina 4 pontos (V, I) para o resistor não-linear.")
        V_points = []
        I_points = []
        for k in range(1, 5):
            v = float(input(f"\tV{k} [V]: "))
            i = float(input(f"\tI{k} [A]: "))
            V_points.append(v)
            I_points.append(i)
        builder.add_nonlinear_resistor(a, b, V_points, I_points)
        print("\tResistor não-linear adicionado com sucesso.")

    elif ctype == "D":
        a = int(input("\tNó ânodo: "))
        b = int(input("\tNó cátodo: "))
        builder.add_diode(a, b)
        print("\tDiodo adicionado com sucesso.")

    else:
        raise ValueError("Tipo de componente não reconhecido.")


    # Others

# ------------------------------------------------#
#                    MAIN MENU                    #
# ------------------------------------------------#

def main_menu(circuit_name: str):
    print(f"\n==> NOVO CIRCUITO: {circuit_name}")
    print("\t1. Renomear circuito")
    print("\t2. Adicionar componente")
    print("\t3. Remover componente")
    print("\t4. Visualizar componentes")
    print("\t5. Alterar configurações de simulação")
    print("\t6. Adicionar arquivo .sim para comparação")
    print("\t7. Salvar netlist para arquivo .net")
    print("\t8. Rodar simulação")
    print("\t0. Sair")

def build_circuit() -> Tuple[Circuit, str]:
    builder = CircuitBuilder()
    sim_file: str = ""

    while True:
        main_menu(builder.name)
        choice = input("Escolha uma opção: \n>> ").strip()
        # Quit
        if choice == "0":
            print("Saindo do construtor de circuitos.")
            exit(0)
        # Rename
        elif choice == "1":
            new_name = input("Novo nome do circuito: ").strip()
            builder.rename(new_name) if new_name else print("Nome não alterado.")
        # Add component
        elif choice == "2":
            try:
                add_component(builder)
                print(f"\n==> CIRCUITO {builder.name} COM NOVO COMPONENTE:")
                for idx, elem in enumerate(builder.elements, start=1):
                    print(f"\t{idx}. {elem}")

            except ValueError:
                print(
                    "\033[31mValue Error\033[0m: Por favor insira valores válidos para os componentes."
                )
            except Exception as e:
                print(f"\033[31mErro inesperado:\033[0m {e}")
        # Remove component
        elif choice == "3":
            print(f"\n==> REMOVER COMPONENTE DE {builder.name}")

            if not builder.elements:
                print("\tNenhum componente para remover.")
                continue

            for idx, elem in enumerate(builder.elements, start=1):
                print(f"\t{idx}. {elem}")

            sel = input(
                "\tDigite o número do componente a remover (ou Enter para cancelar): "
            ).strip()

            if not sel:
                print("\tRemoção cancelada.")
                continue

            try:
                idx = int(sel)
            except ValueError:
                print("\tEntrada inválida. Nenhum componente foi removido.")
                continue

            if builder.remove_component(idx):
                print("\tComponente removido com sucesso.")
            else:
                print("\tÍndice inválido. Nenhum componente foi removido.")

        # View components
        elif choice == "4":
            print(f"\n==> COMPONENTES DE {builder.name}:")
            if not builder.elements:
                print("\t(nenhum componente adicionado ainda)")
            else:
                for idx, elem in enumerate(builder.elements, start=1):
                    print(f"\t{idx}. {elem}")
        # Change simulation settings
        elif choice == "5":
            print("\nCONFIGURAÇÕES ATUAIS DE SIMULAÇÃO")
            current_mode = "TRAN" if builder.transient.enabled else "DC"
            print("\tAnálise:", "Transiente" if builder.transient.enabled else "DC")
            if builder.transient.enabled:
                print(f"\tTempo de simulação: {builder.transient.t_stop} s")
                print(f"\tPasso de tempo: {builder.transient.dt} s")
                print(f"\tMétodo de integração: {builder.transient.method}")
                print(f"\tPassos internos: {builder.transient.intetnal_steps}")

            print("\nALTERAR CONFIGURAÇÕES DE SIMULAÇÃO")
            print("\tDeixe em branco para manter o valor atual.")
            new_type = input("\tTipo de análise (TRAN/DC): ").strip().upper()
            if not new_type:
                new_type = current_mode

            if new_type == "TRAN":
                t_stop_str = input("\tTempo de simulação (s): ")
                dt_str = input("\tPasso de tempo (s): ")
                method = input("\tMétodo de integração (BE, FE, TRAP): ").strip().upper()
                internal_steps_str = input(
                    "\tPassos internos (1 se nenhum): "
                ).strip()

                t_stop = float(t_stop_str) if t_stop_str else builder.transient.t_stop
                dt = float(dt_str) if dt_str else builder.transient.dt
                internal_steps = (
                    int(internal_steps_str)
                    if internal_steps_str
                    else builder.transient.intetnal_steps
                )
                if not method:
                    method = builder.transient.method

                builder.enable_transient(True)
                builder.set_transient(t_stop, dt, method, internal_steps)
            else:  # DC
                builder.enable_transient(False)
                print("\tAnálise definida para DC.")
            
        # Add .sim file
        elif choice == "6":
            print("\n==> ADICIONAR ARQUIVO .sim PARA COMPARAÇÃO GRÀFICA (TRAN)")

            # Only transient
            if not builder.transient.enabled:
                print("\t\033[33mWarning:\033[0m Apenas simulações TRANSIENTES exibem gráfico no tempo.")
                print("\tDefina a análise como TRAN em '5. Alterar configurações de simulação'.")
                continue

            path_str = input("\tInforme o caminho do arquivo .sim (ou Enter para cancelar):\n\t>> ").strip()
            if not path_str:
                print("\tOperação cancelada.")
                continue

            sim_path = Path(path_str)

            # If exists
            if not sim_path.is_file():
                print(f"\t\033[33mWarning:\033[0m Arquivo .sim não encontrado: {sim_path}")
                print("\tVerifique o caminho e tente novamente.")
            else:
                sim_file = str(sim_path)
                print(f"\tArquivo .sim definido para comparação: {sim_file}")

        # Create .net file
        elif choice == "7":
            NETLIST_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

            # Nome de arquivo = nome_do_circuito.net
            filename = (builder.name or "circuito").replace(" ", "_")
            net_path = NETLIST_OUTPUT_DIR / f"{filename}.net"

            try:
                builder.save_netlist(str(net_path))
                print(f"\nNetlist salva em: {net_path}")
            except Exception as e:
                print("\033[31mErro ao salvar netlist\033[0m:", e)

        # Exit and run
        elif choice == "8":
            new_circuit = builder.to_netlist_oop()
            break
        else:
            print("Opção inválida. Tente novamente.")

    print ("\n\nFINALIZANDO CONSTRUÇÃO DO CIRCUITO...")
    return Circuit(new_circuit), sim_file  # Placeholder implementation



# ------------------------------------------------#
#                   CLI MANAGER                   #
# ------------------------------------------------#
def _cli():
    parser = argparse.ArgumentParser()

    parser.add_argument("--netlist", type=str)
    parser.add_argument("--nr_tol", type=float, default=1e-8)
    parser.add_argument("--nodes", nargs="+", type=int, default=None)
    parser.add_argument("--guide", type=str) # existing .sim file path to print alongsige
    parser.add_argument("--create_sim", action="store_true") # create .sim file after simulating

    
    args = parser.parse_args()

    # Built or open existing circuit
    if args.netlist is None:
        circuit, sim_file = build_circuit()
    else:
        netlist = parse_netlist(args.netlist)
        circuit = Circuit(netlist)
        if args.guide:
            sim_file = args.guide

    if __debug__:
        circuit.print()

    # Transient or DC based on netlist settings
    if circuit.data.transient.enabled:
        t, out = circuit.run_tran(
            args.nodes,
            nr_tol=args.nr_tol,
        )

        print("\n==> TRANSIENT CIRCUIT ANALYSIS RESULTS")
        print("Transient points:", len(t))
        if args.nodes is None:
            node_ids = list(range(out.shape[0]))
        else:
            node_ids = args.nodes

        for i in range(out.shape[0]):
            node = node_ids[i]
            print(f"\n- Node {node} first results:", out[i, :10].tolist())
            print(f"- Node {node} last results:", out[i, -10:].tolist())

        # ------------------ PLOTTING ---------------------
        # ----------------- Dict for plot -----------------
        py_vars = {
            f"Node_{node_ids[i]}": out[i]
            for i in range(out.shape[0])
        }

        # ---------- Choose correct .sim file --------------
        sim_time = None
        sim_vars = None

        try:
            sim_file # type: ignore
        except:
            sim_file = find_sim_file(args.netlist)

        if sim_file:
            sim_time, sim_vars = load_sim_file(sim_file)

        # ----------------- Call plot -----------------
        plot_all(t, py_vars, sim_time, sim_vars)
        
    else: # data.transient.enabled = false
        print("CIRCUIT DC ANALYSIS RESULTS")
        result = circuit.run_dc(args.nodes, nr_tol=args.nr_tol)
        print("DC Result:", result.tolist())


if __name__ == "__main__":
    _cli()