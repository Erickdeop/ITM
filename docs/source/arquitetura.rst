============================
Arquitetura e Estrutura do Código
============================

Visão Geral da Arquitetura
---------------------------

O Circuit Simulator MNA utiliza uma arquitetura orientada a objetos com forte uso de herança e polimorfismo. O design segue os princípios SOLID e facilita a extensão com novos tipos de elementos.

Diagrama de Módulos
--------------------

.. code-block:: text

   Circuit Simulator MNA
   ├── simulator/
   │   ├── parser.py        # Parser de netlists
   │   ├── circuit.py       # Classe Circuit (interface principal)
   │   ├── builder.py       # Builder pattern para construção de circuitos
   │   ├── engine.py        # Algoritmos de solução (DC/Transient)
   │   ├── newton.py        # Solver Newton-Raphson
   │   ├── elements/        # Elementos de circuito
   │   │   ├── base.py      # Classes base abstratas
   │   │   ├── resistor.py
   │   │   ├── capacitor.py
   │   │   ├── inductor.py
   │   │   ├── voltage_source.py
   │   │   ├── current_source.py
   │   │   ├── controlled_sources.py
   │   │   ├── diode.py
   │   │   ├── nonlinear_resistor.py
   │   │   └── ampop.py
   │   └── plotting/
   │       └── plot_utils.py

Descrição dos Módulos Principais
---------------------------------

simulator/parser.py
~~~~~~~~~~~~~~~~~~~

**Função**: Lê e interpreta arquivos netlist (.net) no formato SPICE.

**Responsabilidades**:
  - Parse de linhas de netlist
  - Criação de objetos de elementos
  - Extração de configurações de análise (.TRAN, .DC)
  - Validação de sintaxe

**Classes principais**:
  - ``NetlistOOP``: Estrutura de dados para netlist parseada
  - ``TransientSettings``: Configurações de análise transiente

simulator/circuit.py
~~~~~~~~~~~~~~~~~~~~

**Função**: Interface principal para executar análises de circuito.

**Responsabilidades**:
  - Coordena análises DC e transiente
  - Gerencia estado do circuito
  - Interface de alto nível para o usuário

**Classe principal**:
  - ``Circuit``: Classe principal que encapsula todas as operações

simulator/engine.py
~~~~~~~~~~~~~~~~~~~

**Função**: Implementa os algoritmos de solução de circuitos.

**Responsabilidades**:
  - Montagem das matrizes MNA
  - Solução de sistemas lineares
  - Implementação de métodos de integração numérica
  - Análise DC e transiente

**Funções principais**:
  - ``solve_dc()``: Análise DC com Newton-Raphson
  - ``solve_tran()``: Análise transiente com integração numérica

simulator/newton.py
~~~~~~~~~~~~~~~~~~~

**Função**: Implementa o método Newton-Raphson para circuitos não-lineares.

**Responsabilidades**:
  - Iterações de Newton-Raphson
  - Mecanismo de retry com múltiplos chutes iniciais
  - Cálculo de Jacobiano e resíduo
  - Detecção de convergência

**Funções principais**:
  - ``newton_raphson()``: Solver principal
  - ``newton_raphson_retry()``: Versão com retry automático

simulator/builder.py
~~~~~~~~~~~~~~~~~~~~

**Função**: Pattern Builder para construção interativa de circuitos.

**Responsabilidades**:
  - API fluente para adicionar componentes
  - Geração de netlists
  - Validação de circuitos

**Classe principal**:
  - ``CircuitBuilder``: Builder para construção de circuitos

simulator/elements/
~~~~~~~~~~~~~~~~~~~

Contém todas as classes de elementos de circuito, organizadas hierarquicamente:

**Hierarquia de Classes**:

.. code-block:: text

   Element (ABC)
   ├── LinearElement (ABC)
   │   ├── Resistor
   │   ├── Capacitor
   │   └── Inductor
   ├── Source (ABC)
   │   ├── VoltageSource
   │   └── CurrentSource
   ├── ControlledSource (ABC)
   │   ├── VCVS
   │   ├── VCCS
   │   ├── CCVS
   │   └── CCCS
   ├── NonlinearElement (ABC)
   │   ├── Diode
   │   └── NonlinearResistor
   └── Opamp

Padrões de Design Utilizados
-----------------------------

1. **Herança e Polimorfismo**
   - Classes abstratas definem interfaces comuns
   - Elementos específicos implementam métodos polimórficos

2. **Strategy Pattern**
   - Diferentes métodos de integração (BE, FE, TRAP)
   - Diferentes tipos de fontes (DC, AC, SIN, PULSE)

3. **Builder Pattern**
   - ``CircuitBuilder`` para construção fluente

4. **Factory Method**
   - Parser cria elementos baseado no tipo

Fluxo de Execução
------------------

Análise DC
~~~~~~~~~~

.. code-block:: text

   1. Parser lê netlist → NetlistOOP
   2. Circuit.run_dc() chamado
   3. engine.solve_dc() monta sistema MNA
   4. Newton-Raphson resolve sistema não-linear
   5. Retorna tensões nodais

Análise Transiente
~~~~~~~~~~~~~~~~~~

.. code-block:: text

   1. Parser lê netlist → NetlistOOP
   2. Circuit.run_tran() chamado
   3. Loop temporal:
      a. Atualiza fontes dependentes do tempo
      b. Monta sistema MNA com contribuições dinâmicas
      c. Resolve sistema (linear ou Newton-Raphson)
      d. Atualiza estados dos elementos (L, C)
   4. Retorna histórico temporal

Método de Análise Nodal Modificada (MNA)
-----------------------------------------

O MNA é uma técnica que:

1. Cria equações baseadas na Lei de Kirchhoff das Correntes (LKC)
2. Adiciona variáveis auxiliares para fontes de tensão
3. Resulta em um sistema matricial:

.. math::

   G \\cdot x = I

Onde:
  - **G**: Matriz de condutâncias (aumentada)
  - **x**: Vetor de incógnitas (tensões nodais + correntes auxiliares)
  - **I**: Vetor de fontes independentes

Estampas de Elementos
~~~~~~~~~~~~~~~~~~~~~~

Cada elemento implementa métodos ``stamp_dc()`` e ``stamp_transient()`` que modificam as matrizes G e I apropriadamente.

**Exemplo - Resistor**:

.. code-block:: python

   # Entre nós a e b com resistência R
   G[a,a] += 1/R
   G[a,b] -= 1/R
   G[b,a] -= 1/R
   G[b,b] += 1/R

Extensibilidade
---------------

Para adicionar um novo tipo de elemento:

1. Criar classe herdando de ``Element`` ou subclasse apropriada
2. Implementar ``stamp_dc()`` e ``stamp_transient()``
3. Para não-lineares, implementar ``i_nl()`` e ``di_nl()``
4. Adicionar lógica de parsing em ``parser.py``
5. Escrever testes unitários e de integração
