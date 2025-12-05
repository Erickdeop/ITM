==============
Visão Geral do Projeto
==============

Propósito
---------

O **Circuit Simulator MNA** é um simulador de circuitos eletrônicos desenvolvido em Python que utiliza o método de Análise Nodal Modificada (Modified Nodal Analysis - MNA). O software permite simular circuitos lineares e não-lineares com diversos tipos de componentes.

Principais Funcionalidades
---------------------------

Elementos Suportados
~~~~~~~~~~~~~~~~~~~~

**Elementos Lineares:**
  - Resistores (R)
  - Capacitores (C)
  - Indutores (L)

**Fontes:**
  - Fontes de tensão DC, AC, SIN, PULSE
  - Fontes de corrente DC, AC, SIN, PULSE

**Fontes Controladas:**
  - VCVS (Voltage-Controlled Voltage Source)
  - VCCS (Voltage-Controlled Current Source)
  - CCVS (Current-Controlled Voltage Source)
  - CCCS (Current-Controlled Current Source)

**Elementos Não-Lineares:**
  - Diodos
  - Resistores não-lineares
  - Amplificadores operacionais ideais

Análises Disponíveis
~~~~~~~~~~~~~~~~~~~~~

1. **Análise DC**: Calcula os pontos de operação do circuito
2. **Análise Transiente**: Simula o comportamento do circuito no tempo

Métodos de Integração
~~~~~~~~~~~~~~~~~~~~~~

- **Backward Euler (BE)**: Estável e implícito
- **Forward Euler (FE)**: Explícito e simples
- **Trapezoidal (TRAP)**: Maior precisão

Características Especiais
~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Newton-Raphson com Retry**: Mecanismo automático de múltiplas tentativas com vetores aleatórios para circuitos com convergência difícil
- **Arquitetura OOP**: Design orientado a objetos com polimorfismo
- **Parser de Netlists**: Leitura de arquivos .net no formato SPICE
- **Suite de Testes**: 76 testes unitários e de integração

Aplicações
----------

O simulador pode ser utilizado para:

- Análise de circuitos em cursos de eletrônica
- Prototipagem rápida de circuitos
- Validação de projetos antes da implementação física
- Estudos de comportamento transitório de circuitos
- Análise de circuitos não-lineares

Tecnologias Utilizadas
-----------------------

- **Python 3.9+**
- **NumPy**: Operações matriciais e álgebra linear
- **SciPy**: Métodos numéricos avançados
- **Matplotlib**: Visualização de resultados
- **Pytest**: Framework de testes
- **Sphinx**: Geração de documentação
