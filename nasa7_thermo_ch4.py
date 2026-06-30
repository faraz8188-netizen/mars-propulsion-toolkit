"""
NASA 7-Coefficient Polynomial Thermo Database - Extended for CH4/O2 Combustion
Adds CH4, CO, CO2 species to the H2/O2/N2/H2O database, for methalox rocket
combustion analysis.

Source: Same as hypersonic toolkit's nasa7_thermo.py - GRI-Mech 3.0
Thermodynamics (7/30/99), NASA Polynomial format for CHEMKIN-II.
Coefficients from McBride, Gordon and Reno, NASA TM-4513, 1993.
Public source: https://github.com/OpenFOAM/OpenFOAM-6/blob/master/tutorials/
combustion/reactingFoam/RAS/SandiaD_LTS/chemkin/thermo30.dat
"""

import numpy as np

R_UNIV = 8.314510  # J/(mol*K)

SPECIES = {
    'O2': {
        'Tmid': 1000.0, 'M': 31.9988,
        'high': [3.28253784E+00, 1.48308754E-03, -7.57966669E-07, 2.09470555E-10, -2.16717794E-14, -1.08845772E+03, 5.45323129E+00],
        'low':  [3.78245636E+00, -2.99673416E-03, 9.84730201E-06, -9.68129509E-09, 3.24372837E-12, -1.06394356E+03, 3.65767573E+00],
    },
    'H2O': {
        'Tmid': 1000.0, 'M': 18.01528,
        'high': [3.03399249E+00, 2.17691804E-03, -1.64072518E-07, -9.70419870E-11, 1.68200992E-14, -3.00042971E+04, 4.96677010E+00],
        'low':  [4.19864056E+00, -2.03643410E-03, 6.52040211E-06, -5.48797062E-09, 1.77197817E-12, -3.02937267E+04, -8.49032208E-01],
    },
    'CH4': {
        'Tmid': 1000.0, 'M': 16.04246,
        'high': [7.48514950E-02, 1.33909467E-02, -5.73285809E-06, 1.22292535E-09, -1.01815230E-13, -9.46834459E+03, 1.84373180E+01],
        'low':  [5.14987613E+00, -1.36709788E-02, 4.91800599E-05, -4.84743026E-08, 1.66693956E-11, -1.02466476E+04, -4.64130376E+00],
    },
    'CO': {
        'Tmid': 1000.0, 'M': 28.01010,
        'high': [2.71518561E+00, 2.06252743E-03, -9.98825771E-07, 2.30053008E-10, -2.03647716E-14, -1.41518724E+04, 7.81868772E+00],
        'low':  [3.57953347E+00, -6.10353680E-04, 1.01681433E-06, 9.07005884E-10, -9.04424499E-13, -1.43440860E+04, 3.50840928E+00],
    },
    'CO2': {
        'Tmid': 1000.0, 'M': 44.00950,
        'high': [3.85746029E+00, 4.41437026E-03, -2.21481404E-06, 5.23490188E-10, -4.72084164E-14, -4.87591660E+04, 2.27163806E+00],
        'low':  [2.35677352E+00, 8.98459677E-03, -7.12356269E-06, 2.45919022E-09, -1.43699548E-13, -4.83719697E+04, 9.90105222E+00],
    },
    'O': {
        'Tmid': 1000.0, 'M': 15.9994,
        'high': [2.56942078E+00, -8.59741137E-05, 4.19484589E-08, -1.00177799E-11, 1.22833691E-15, 2.92175791E+04, 4.78433864E+00],
        'low':  [3.16826710E+00, -3.27931884E-03, 6.64306396E-06, -6.12806624E-09, 2.11265971E-12, 2.91222592E+04, 2.05193346E+00],
    },
    'H': {
        'Tmid': 1000.0, 'M': 1.00794,
        'high': [2.50000001E+00, -2.30842973E-11, 1.61561948E-14, -4.73515235E-18, 4.98197357E-22, 2.54736599E+04, -4.46682914E-01],
        'low':  [2.50000000E+00, 7.05332819E-13, -1.99591964E-15, 2.30081632E-18, -9.27732332E-22, 2.54736599E+04, -4.46682853E-01],
    },
    'OH': {
        'Tmid': 1000.0, 'M': 17.00734,
        'high': [3.09288767E+00, 5.48429716E-04, 1.26505228E-07, -8.79461556E-11, 1.17412376E-14, 3.85865700E+03, 4.47669610E+00],
        'low':  [3.99201543E+00, -2.40131752E-03, 4.61793841E-06, -3.88113333E-09, 1.36411470E-12, 3.61508056E+03, -1.03925458E-01],
    },
    'H2': {
        'Tmid': 1000.0, 'M': 2.01588,
        'high': [3.33727920E+00, -4.94024731E-05, 4.99456778E-07, -1.79566394E-10, 2.00255376E-14, -9.50158922E+02, -3.20502331E+00],
        'low':  [2.34433112E+00, 7.98052075E-03, -1.94781510E-05, 2.01572094E-08, -7.37611761E-12, -9.17935173E+02, 6.83010238E-01],
    },
}

def _coeffs(species, T):
    sp = SPECIES[species]
    return sp['low'] if T < sp['Tmid'] else sp['high']

T_POLY_MAX = 3500.0  # K - GRI-Mech 3.0 validity ceiling for CH4/CO/CO2/H2O/O2
                      # Found during development: evaluating these polynomials
                      # above 3500K causes Cp(CO2) to UNPHYSICALLY DECREASE,
                      # a polynomial extrapolation artifact, not real physics.
                      # All functions below clamp T to this ceiling.

def cp_molar(species, T):
    T_eval = min(T, T_POLY_MAX)
    a = _coeffs(species, T_eval)
    return (a[0] + a[1]*T_eval + a[2]*T_eval**2 + a[3]*T_eval**3 + a[4]*T_eval**4) * R_UNIV

def h_molar(species, T):
    T_eval = min(T, T_POLY_MAX)
    a = _coeffs(species, T_eval)
    h_over_RT = a[0] + a[1]*T_eval/2 + a[2]*T_eval**2/3 + a[3]*T_eval**3/4 + a[4]*T_eval**4/5 + a[5]/T_eval
    h_at_cap = h_over_RT * R_UNIV * T_eval
    if T > T_POLY_MAX:
        cp_at_cap = cp_molar(species, T_POLY_MAX)
        h_at_cap += cp_at_cap * (T - T_POLY_MAX)
    return h_at_cap

def molar_mass(species):
    return SPECIES[species]['M']

def s_molar(species, T):
    """Molar entropy [J/(mol*K)] using NASA polynomial a7 coefficient."""
    T_eval = min(T, T_POLY_MAX)
    a = _coeffs(species, T_eval)
    s_over_R = a[0]*np.log(T_eval) + a[1]*T_eval + a[2]*T_eval**2/2 + a[3]*T_eval**3/3 + a[4]*T_eval**4/4 + a[6]
    return s_over_R * R_UNIV

if __name__ == '__main__':
    print('=== CH4/O2 EXTENDED THERMO DATABASE ===')
    for sp in SPECIES:
        h298 = h_molar(sp, 298.15)/1000
        print(f'  {sp}: H(298.15K) = {h298:.3f} kJ/mol, M = {molar_mass(sp):.3f} g/mol')
