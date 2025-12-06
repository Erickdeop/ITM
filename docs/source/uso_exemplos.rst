================
Uso e Exemplos
================

Este guia apresenta exemplos práticos de como utilizar o Circuit Simulator MNA.

Interface de Linha de Comando (CLI)
------------------------------------

Criação de um circuito pela linha de comando
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   python3 main.py

**Saída esperada**:

.. code-block:: text

   ==> NOVO CIRCUITO: CIRCUITO_1
        1. Renomear circuito
        2. Adicionar componente
        3. Remover componente
        4. Visualizar componentes
        5. Alterar configurações de simulação
        6. Adicionar arquivo .sim para comparação
        7. Salvar netlist para arquivo .net
        8. Rodar simulação
        0. Sair
   Escolha uma opção: 


Análise DC Simples
~~~~~~~~~~~~~~~~~~

Analisar um divisor de tensão:

.. code-block:: bash

   python3 -m simulator.circuit --netlist ./circuits/vdc_divider.net --analysis DC --nodes 1 2
0
**Saída esperada**:

.. code-block:: text

   Análise DC concluída
   V(1) = 5.0V
   V(2) = 2.5V

Análise Transiente
~~~~~~~~~~~~~~~~~~

Simular resposta de um circuito RC:

.. code-block:: bash

   python3 -m simulator.circuit \\
       --netlist ./circuits/example_tran.net \\
       --analysis TRAN \\
       --total_time 1e-3 \\
       --dt 1e-5 \\
       --method TRAP \\
       --nodes 1

**Parâmetros**:
  - ``--total_time``: Tempo total de simulação (segundos)
  - ``--dt``: Passo de integração (segundos)
  - ``--method``: BE (Backward Euler), FE (Forward Euler), ou TRAP (Trapezoidal)
  - ``--nodes``: Nós a serem plotados

Interface Interativa (main.py)
-------------------------------

Para criar circuitos interativamente:

.. code-block:: bash

   python3 main.py

Menu interativo permite:
  - Adicionar componentes dinamicamente
  - Configurar análises
  - Salvar netlists
  - Executar simulações

Plotagem de Resultados (plot.py)
---------------------------------

Para plotar e comparar resultados:

.. code-block:: bash

   python3 plot.py --net ./circuits/sinusoidal.net --tran 0.05 1e-4 --method BE --nodes 1

Se existir arquivo ``.sim`` correspondente, será comparado automaticamente.

Exemplos de Netlists
---------------------

Exemplo 1: Divisor de Tensão DC
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Arquivo**: ``circuits/vdc_divider.net``

.. code-block:: spice

   * Divisor de tensão DC
   2
   V1 1 0 DC 10
   R1 1 2 1000
   R2 2 0 1000

**Descrição**:
  - Fonte de 10V entre nó 1 e terra (0)
  - Dois resistores de 1kΩ em série
  - Espera-se V(2) = 5V

Exemplo 2: Circuito RC com Resposta ao Degrau
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Arquivo**: ``circuits/example_tran.net``

.. code-block:: spice

   * Circuito RC - resposta ao degrau
   1
   V1 1 0 DC 5
   R1 1 2 1000
   C1 2 0 1e-6
   .TRAN 0.005 1e-5 BE 0

**Descrição**:
  - Fonte de 5V
  - R = 1kΩ, C = 1µF
  - Constante de tempo τ = RC = 1ms
  - Análise transiente de 5ms

Exemplo 3: Fonte Senoidal
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: spice

   * Fonte senoidal
   1
   V1 1 0 SIN 0 5 1000 0 0 0
   R1 1 0 100
   .TRAN 0.01 1e-5 BE 0

**Parâmetros SIN**: offset, amplitude, freq, delay, damping, phase

Exemplo 4: Fonte PULSE
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: spice

   * Fonte pulsada
   1
   V1 1 0 PULSE 0 5 0.001 0.0001 0.0001 0.002 0.01
   R1 1 0 100
   .TRAN 0.05 1e-5 BE 0

**Parâmetros PULSE**: v1, v2, delay, rise_time, fall_time, pulse_width, period

Exemplo 5: Circuito com Diodo
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: spice

   * Retificador simples
   1
   V1 1 0 SIN 0 10 60 0 0 0
   D1 1 2 DIODE IS=1e-14 N=1.0
   R1 2 0 1000
   .TRAN 0.05 1e-4 BE 0

**Parâmetros do diodo**: IS (corrente de saturação), N (fator de idealidade)

Exemplo 6: Fontes Controladas
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: spice

   * Amplificador de tensão com VCVS
   2
   V1 1 0 DC 1
   R1 1 0 1000
   E1 2 0 1 0 10.0
   R2 2 0 1000

**VCVS (E)**: Amplifica tensão V(1,0) por ganho de 10

Exemplo 7: Circuito com Fonte de Corrente SIN
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: spice

   * Fonte de corrente senoidal
   1
   I1 0 1 SIN 0 0.001 1000 0 0 0
   R1 1 0 1000
   .TRAN 0.005 1e-6 BE 0

**Resultado**: Tensão senoidal com amplitude de 1V (I × R = 0.001 × 1000)

Uso Programático (API Python)
------------------------------

Exemplo Básico
~~~~~~~~~~~~~~

.. code-block:: python

   from simulator.parser import parse_netlist
   from simulator.engine import solve_dc
   
   # Parse netlist
   data = parse_netlist("circuits/vdc_divider.net")
   
   # Executar análise DC
   voltages = solve_dc(data, nr_tol=1e-6, v0_vector=None, desired_nodes=[1, 2])
   
   print(f"V(1) = {voltages[0]:.2f}V")
   print(f"V(2) = {voltages[1]:.2f}V")

Análise Transiente Programática
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from simulator.parser import parse_netlist
   from simulator.engine import solve_tran
   from simulator.elements.base import TimeMethod
   import matplotlib.pyplot as plt
   
   # Parse e simular
   data = parse_netlist("circuits/example_tran.net")
   times, outputs = solve_tran(
       data,
       total_time=0.005,
       dt=1e-5,
       nr_tol=1e-6,
       v0_vector=None,
       desired_nodes=[1],
       method=TimeMethod.BACKWARD_EULER
   )
   
   # Plotar
   plt.plot(times, outputs[0, :])
   plt.xlabel('Tempo (s)')
   plt.ylabel('Tensão (V)')
   plt.grid(True)
   plt.show()

Construtor de Circuitos
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from simulator.builder import CircuitBuilder
   
   builder = CircuitBuilder("Meu Circuito")
   builder.add_voltage_source("V1", 1, 0, dc=10)
   builder.add_resistor("R1", 1, 2, 1000)
   builder.add_resistor("R2", 2, 0, 1000)
   builder.set_dc_analysis()
   
   # Salvar netlist
   builder.save_netlist("meu_circuito.net")

Parâmetros do Newton-Raphson
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Para circuitos não-lineares difíceis:

.. code-block:: python

   from simulator.circuit import Circuit
   
   circuit = Circuit("circuits/diode_circuit.net")
   result = circuit.run_dc(
       max_nr_iter=50,      # Iterações por tentativa
       max_nr_guesses=100,  # Número de tentativas
       nr_tol=1e-6
   )

Dicas de Uso
------------

1. **Escolha do Método de Integração**:
   - BE: Mais estável, recomendado para circuitos stiff
   - TRAP: Mais preciso, bom para circuitos suaves
   - FE: Mais rápido mas pode ser instável

2. **Passo de Integração (dt)**:
   - Use dt < τ/10 onde τ é a menor constante de tempo
   - Para fontes senoidais: dt < 1/(20×freq)

3. **Convergência do Newton-Raphson**:
   - Se não convergir, tente aumentar ``max_nr_guesses``
   - Verifique se o circuito está bem condicionado
   - Use valores iniciais próximos da solução (v0_vector)

4. **Performance**:
   - Para simulações longas, use dt maior
   - Evite passos muito pequenos desnecessariamente
   - Use análise DC para condições iniciais da transiente

Exemplos Avançados
-------------------

Oscilador LC
~~~~~~~~~~~~

.. code-block:: spice

   * Oscilador LC
   1
   V1 1 0 DC 5
   L1 1 2 1e-3 IC=0
   C1 2 0 1e-6 IC=5
   .TRAN 0.001 1e-7 BE 0

Retificador com OpAmp
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: spice

   * Retificador de precisão
   3
   V1 1 0 SIN 0 1 60 0 0 0
   R1 1 2 1000
   O1 2 3 3 OPAMP
   D1 3 4 DIODE IS=1e-14 N=1.0
   R2 4 0 1000
   .TRAN 0.05 1e-4 BE 0
