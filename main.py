import argparse
from simulator.parser import parse_netlist
from simulator.circuit import Circuit
from simulator.builder import CircuitBuilder
from typing import Tuple

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
            print("\n==> REMOVER COMPONENTE (À IMPLEMENTAR)")
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
            print("\n==> ADICIONAR ARQUIVO .sim (À IMPLEMENTAR)")
        # Create .net file
        elif choice == "7":
            print("\n==> SALVAR NETLIST EM ARQUIVO .net (À IMPLEMENTAR)")
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
        circuit, _ = build_circuit()
    else:
        netlist = parse_netlist(args.netlist)
        circuit = Circuit(netlist)

    if __debug__:
        circuit.print()

    # Transient or DC based on netlist settings
    if circuit.data.transient.enabled:
        t, out = circuit.run_tran(
            args.nodes,
            nr_tol=args.nr_tol,
        )

        print("\n==> CIRCUIT TRANSIENT ANALYSIS RESULTS")
        print("Transient points:", len(t))
        for i in range(out.shape[0]):
            if args.nodes is None:
                node = i
            else: 
                node = args.nodes[i]
            print(f"\n- Node {node} first results:", out[i, :10].tolist())
            print(f"- Node {node} last results:", out[i, -10:].tolist())

        ''' SAVE .SIM FILE
        if args.create_sim:
            sim_path = args.netlist.rsplit(".", 1)[0] + ".sim"
            from simulator.simfile import save_sim_file
            save_sim_file(sim_path, t, {f"Node_{node}": out[i] for i, node in enumerate(args.nodes or range(out.shape[0]))})
            print(f".SIM file saved to: {sim_path}")
            '''
        
    else: # data.transient.enabled = false
        print("CIRCUIT DC ANALYSIS RESULTS")
        result = circuit.run_dc(args.nodes, nr_tol=args.nr_tol)
        print("DC Result:", result.tolist())


if __name__ == "__main__":
    _cli()