import numpy as np
import pytest
from simulator.elements.diode import Diode
from simulator.elements.nonlinear_resistor import NonLinearResistor

def test_diode_shockley_math():

    d = Diode(1, 0, Is=3.7751345e-14, Vt=0.025)
    
    Vd = 0.7

    # Expected values based on Shockley equation
    Id_expected = d.Is * (np.exp(Vd/d.Vt) - 1) # Id = Is * (exp(Vd/Vt) - 1)
    Gd_expected = (d.Is / d.Vt) * np.exp(Vd/d.Vt) # Gd = Is/Vt * exp(Vd/Vt)
    Ieq_expected = Id_expected - (Gd_expected * Vd) # I_eq = Id - Gd * Vd

    # Clalculated values from the method
    I_calc, G_calc = d._get_norton_equivalent(Vd)

    # Checks
    assert I_calc == pytest.approx(Ieq_expected, rel=1e-5)
    assert G_calc == pytest.approx(Gd_expected, rel=1e-5)

def test_diode_clamp_safety():

    d = Diode(1, 0)
    
    I_calc, G_calc = d._get_norton_equivalent(5.0)
    
    # Calculations must match the clamped values (0.9V)
    I_expected, G_expected = d._get_norton_equivalent(0.9)
    
    assert I_calc == I_expected
    assert G_calc == G_expected

def test_nonlinear_resistor_segment_selection():
    # Curve: (0,0) -> (1,1) -> (2,3) -> (4,4)
    # Segment 1 (0 a 1V): Inclinação (G) = 1.0
    # Segment 2 (1 a 2V): Inclinação (G) = 2.0

    V_points = np.array([0., 1., 2., 4.])
    I_points = np.array([0., 1., 3., 4.])
    
    nlr = NonLinearResistor(1, 0, V_points, I_points)
    
    I_nr, G_eq = nlr._get_current_and_conductance(0.5)
    assert G_eq == 1.0
    assert I_nr == 0.0
    
    I_nr, G_eq = nlr._get_current_and_conductance(1.5)
    assert G_eq == 2.0
    assert I_nr == -1.0