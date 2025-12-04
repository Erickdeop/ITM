import numpy as np
from simulator.elements.ampop import OpAmp


def test_opamp_augments_mna():
    # Matriz G/I inicial com nós 0,1,2,3
    G = np.zeros((4, 4))
    I = np.zeros(4)

    # OpAmp entre:
    #   saída: a=1, b=2
    #   entradas: c=3 (v+), d=0 (v-)
    gain = 10.0
    op = OpAmp(a=1, b=2, c=3, d=0, gain=gain)

    G2, I2 = op.stamp_dc(G.copy(), I.copy())

    # 1) tem que aumentar o tamanho da matriz em +1
    assert G2.shape == (5, 5)
    assert I2.shape == (5,)

    # Índice da variável MNA extra (corrente da fonte interna do opamp)
    x_idx = 4  # era 0..3, vira 0..4

    # 2) KCL nos nós de saída: corrente da fonte entra em a e sai em b
    assert G2[1, x_idx] == 1.0   # +I em a
    assert G2[2, x_idx] == -1.0  # -I em b

    # 3) Equação de controle do ampop (linha x_idx):
    #    v_a - v_b - gain * (v_c - v_d) = 0
    #
    #    => -v_a + v_b + gain*v_c - gain*v_d = 0
    assert G2[x_idx, 1] == -1.0        # -v_a
    assert G2[x_idx, 2] == 1.0         # +v_b
    assert G2[x_idx, 3] == gain        # +gain * v_c
    assert G2[x_idx, 0] == -gain       # -gain * v_d (nó 0)


def test_opamp_does_not_change_original_G_I():
    """Garante que stamp_dc não modifica G/I in-place."""
    G = np.zeros((4, 4))
    I = np.zeros(4)
    G_copy = G.copy()
    I_copy = I.copy()

    op = OpAmp(a=1, b=2, c=3, d=0, gain=1e5)
    op.stamp_dc(G, I)

    # originais intactos
    assert np.array_equal(G, G_copy)
    assert np.array_equal(I, I_copy)
