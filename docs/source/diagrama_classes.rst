================
Diagrama de Classes
================

Hierarquia de Classes de Elementos
-----------------------------------

O Circuit Simulator MNA utiliza uma arquitetura orientada a objetos com herança e polimorfismo. A hierarquia de classes demonstra claramente os princípios de encapsulamento e reutilização de código.

Diagrama UML
------------

.. placeholder for the image diagram -- IGNORE ---

Descrição das Classes Base
---------------------------

Element (Classe Abstrata Base)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Responsabilidade**: Define interface comum para todos os elementos de circuito.

**Atributos**:
  - ``a: int`` - Nó positivo
  - ``b: int`` - Nó negativo

**Métodos Abstratos**:
  - ``stamp_dc(G, I, x_guess) → (G, I)`` - Stamp para análise DC
  - ``stamp_transient(G, I, state, t, dt, method, x_guess) → (G, I, state)`` - Stamp transiente

**Métodos Concretos**:
  - ``is_linear() → bool`` - Retorna se elemento é linear
  - ``augments_mna() → bool`` - Retorna se aumenta matriz MNA

LinearElement (Classe Abstrata)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Herda de**: ``Element``

**Responsabilidade**: Base para elementos passivos lineares (R, L, C).

**Características**:
  - ``is_linear() → True``
  - ``augments_mna() → False``
  - Não requer Newton-Raphson

Source (Classe Abstrata)
~~~~~~~~~~~~~~~~~~~~~~~~~

**Herda de**: ``Element``

**Responsabilidade**: Base para fontes independentes (tensão e corrente).

**Atributos Comuns**:
  - ``dc: float`` - Valor DC
  - ``amp: float`` - Amplitude AC
  - ``freq: float`` - Frequência
  - ``source_type: str`` - Tipo: "DC", "AC", "SIN", "PULSE"
  - ``sin_params: Optional[Dict]`` - Parâmetros SIN
  - ``pulse_params: Optional[Dict]`` - Parâmetros PULSE

**Métodos**:
  - ``get_value_at(time: float) → float`` - Valor da fonte no tempo t

ControlledSource (Classe Abstrata)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Herda de**: ``Element``

**Responsabilidade**: Base para fontes controladas (VCVS, VCCS, CCVS, CCCS).

**Atributos Comuns**:
  - Nós de controle
  - Nós de saída  
  - Ganho/transcondutância/transresistência

**Características**:
  - ``augments_mna() → True`` (exceto VCCS)
  - Linear mas com coupling entre variáveis

NonlinearElement (Classe Abstrata)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Herda de**: ``Element``

**Responsabilidade**: Base para elementos não-lineares (diodo, resistor NL).

**Métodos Abstratos**:
  - ``i_nl(v: float) → float`` - Corrente não-linear
  - ``di_nl(v: float) → float`` - Derivada (condutância incremental)

**Características**:
  - ``is_linear() → False``
  - Requer Newton-Raphson
  - Implementa linearização local

Classes Concretas - Elementos Lineares
---------------------------------------

Resistor
~~~~~~~~

.. code-block:: python

   class Resistor(LinearElement):
       def __init__(self, a: int, b: int, R: float):
           self.a = a
           self.b = b
           self.R = R
       
       def stamp_dc(self, G, I, x_guess=None):
           g = 1.0 / self.R
           G[self.a, self.a] += g
           G[self.a, self.b] -= g
           G[self.b, self.a] -= g
           G[self.b, self.b] += g
           return G, I

**Equação**: V = I × R → G = 1/R

Capacitor
~~~~~~~~~

.. code-block:: python

   class Capacitor(LinearElement):
       def __init__(self, a: int, b: int, C: float, v0: float = 0.0):
           self.a = a
           self.b = b
           self.C = C
           self.v0 = v0  # Condição inicial
           self.state = {}

**Modelos de Integração**:
  - **BE**: Geq = C/dt, Ieq = C/dt × V(t-dt)
  - **TRAP**: Geq = 2C/dt, Ieq = 2C/dt × V(t-dt) + I(t-dt)

Indutor
~~~~~~~

.. code-block:: python

   class Inductor(LinearElement):
       def __init__(self, a: int, b: int, L: float, i0: float = 0.0):
           self.a = a
           self.b = b
           self.L = L
           self.i0 = i0  # Condição inicial de corrente
           self.state = {}

**Modelos de Integração**:
  - **BE**: Geq = dt/L, Ieq = I(t-dt)
  - **TRAP**: Geq = 2dt/L, Ieq = -I(t-dt) + 2dt/L × V(t-dt)

Classes Concretas - Fontes
---------------------------

VoltageSource
~~~~~~~~~~~~~

.. code-block:: python

   class VoltageSource(Source):
       def __init__(self, a: int, b: int, dc: float = 0.0, ...):
           # Aumenta MNA com variável auxiliar de corrente
           self.branch_index = next_available_index
       
       def augments_mna(self) → bool:
           return True

**Stamp MNA**:
  - Adiciona linha e coluna para corrente auxiliar
  - Equação: V(a) - V(b) = Vsource

CurrentSource
~~~~~~~~~~~~~

.. code-block:: python

   class CurrentSource(Source):
       def __init__(self, a: int, b: int, dc: float = 0.0, ...):
           # Não aumenta MNA
       
       def stamp_dc(self, G, I, x_guess=None):
           val = self.get_value_at(0.0)
           I[self.a] -= val  # Corrente sai do nó a
           I[self.b] += val  # Corrente entra no nó b
           return G, I

**Convenção**: Corrente flui de ``a`` para ``b``

Classes Concretas - Fontes Controladas
---------------------------------------

VCVS (E)
~~~~~~~~

.. code-block:: python

   class VCVS(ControlledSource):
       # E1 n+ n- nc+ nc- gain
       # V(n+, n-) = gain × V(nc+, nc-)

**Equação**: Vout = Av × Vin

VCCS (G)
~~~~~~~~

.. code-block:: python

   class VCCS(ControlledSource):
       # G1 n+ n- nc+ nc- gm
       # I(n+→n-) = gm × V(nc+, nc-)

**Equação**: Iout = gm × Vin (transcondutância)

CCVS (H)
~~~~~~~~

.. code-block:: python

   class CCVS(ControlledSource):
       # H1 n+ n- Vcontrol rm
       # V(n+, n-) = rm × I(Vcontrol)

**Equação**: Vout = rm × Iin (transresistência)

CCCS (F)
~~~~~~~~

.. code-block:: python

   class CCCS(ControlledSource):
       # F1 n+ n- Vcontrol beta
       # I(n+→n-) = beta × I(Vcontrol)

**Equação**: Iout = β × Iin (ganho de corrente)

Classes Concretas - Elementos Não-Lineares
-------------------------------------------

Diode
~~~~~

.. code-block:: python

   class Diode(NonlinearElement):
       def __init__(self, a: int, b: int, IS: float = 1e-14, N: float = 1.0):
           self.a = a
           self.b = b
           self.IS = IS  # Corrente de saturação
           self.N = N    # Fator de idealidade
       
       def i_nl(self, v: float) → float:
           VT = 0.026  # kT/q a 300K
           return self.IS * (exp(v / (self.N * VT)) - 1)
       
       def di_nl(self, v: float) → float:
           # Condutância incremental
           VT = 0.026
           return self.IS / (self.N * VT) * exp(v / (self.N * VT))

**Equação de Shockley**: I = IS × (e^(V/(N×VT)) - 1)

NonlinearResistor
~~~~~~~~~~~~~~~~~

.. code-block:: python

   class NonlinearResistor(NonlinearElement):
       def __init__(self, a: int, b: int, segments: List[Tuple[float, float]]):
           # Segmentos PWL: [(V1, I1), (V2, I2), ...]
           self.segments = segments
       
       def i_nl(self, v: float) → float:
           # Interpolação linear entre segmentos
           # ...
       
       def di_nl(self, v: float) → float:
           # Condutância local (slope do segmento)
           # ...

**Modelo**: Piecewise Linear (PWL) com interpolação

Opamp (Ideal)
~~~~~~~~~~~~~

.. code-block:: python

   class Opamp:
       def __init__(self, nin: int, nout: int, nfb: int):
           # V(nin) = V(nfb)  # Virtual short
           # I(nout) = qualquer  # Saída ideal

**Características**:
  - Ganho infinito
  - Impedância de entrada infinita
  - Virtual short entre entradas

Encapsulamento e Abstração
---------------------------

Princípios Aplicados
~~~~~~~~~~~~~~~~~~~~

1. **Encapsulamento**:
   - Atributos privados/protegidos via convenção
   - Métodos públicos bem definidos
   - Estado interno (``state``) gerenciado internamente

2. **Herança**:
   - Hierarquia clara de classes
   - Reutilização de código nas classes base
   - Especialização em subclasses

3. **Polimorfismo**:
   - Mesma interface (``stamp_dc``, ``stamp_transient``) para todos elementos
   - Engine processa elementos polimorficamente
   - Permite adicionar novos elementos sem modificar engine

4. **Abstração**:
   - Classes abstratas definem contratos
   - Detalhes de implementação ocultados
   - Interface limpa para o usuário

Exemplo de Uso Polimórfico
---------------------------

.. code-block:: python

   def assemble_mna(elements: List[Element], num_nodes: int):
       G = np.zeros((num_nodes, num_nodes))
       I = np.zeros(num_nodes)
       
       for elem in elements:
           # Polimorfismo: cada elemento implementa seu stamp
           G, I = elem.stamp_dc(G, I)
       
       return G, I

Independente do tipo concreto de elemento, o código funciona graças ao polimorfismo.

Diagrama de Sequência - Análise DC
-----------------------------------

.. code-block:: text

   User → Circuit.run_dc()
           ↓
   Circuit → engine.solve_dc(netlist)
                   ↓
   Engine → parse elements
                   ↓
   Engine → assemble_mna(elements)
                   ↓
   [for each element]
       Element.stamp_dc(G, I)  # Polimorfismo
                   ↓
   Engine → newton_raphson_retry(...)
                   ↓
   Newton → [Iterações]
       - Avalia i_nl() para não-lineares
       - Calcula Jacobiano
       - Resolve sistema linear
       - Atualiza x
                   ↓
   Newton → return voltages
                   ↓
   Engine → return voltages
                   ↓
   Circuit → return voltages
                   ↓
   User ← resultado

Benefícios da Arquitetura OOP
------------------------------

1. **Manutenibilidade**: Código organizado e fácil de entender
2. **Extensibilidade**: Novos elementos via herança sem quebrar código existente
3. **Testabilidade**: Componentes isolados são fáceis de testar
4. **Reutilização**: Código compartilhado nas classes base
5. **Flexibilidade**: Polimorfismo permite tratar elementos uniformemente
