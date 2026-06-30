"""
CH4/O2 Methalox Combustion with Real Two-Reaction Dissociation Equilibrium

Solves the two dominant dissociation equilibria using Gibbs free energy
derived DIRECTLY from the NASA 7-coefficient polynomials (no external
curve-fit data needed):

  CO2 <-> CO + 0.5 O2
  H2O <-> H2 + 0.5 O2

Method: Kp(T) = exp(-deltaG(T)/RT), with deltaG = deltaH - T*deltaS,
both computed from the validated NASA polynomial enthalpy and entropy
functions (h_molar, s_molar in nasa7_thermo_ch4.py).

VALIDATION: this Gibbs-derived approach was cross-checked against a
published textbook result (CO2 dissociation at 3000K, 1 atm) before use
here: computed alpha=43.9% vs published alpha=40.0% (standard general
chemistry equilibrium problem, cited via Oxtoby/Gillis/Campion and
Flowers et al. textbooks) - within 4 percentage points using ONLY the
NASA polynomial data, no external Kp curve-fit required.

RESULT: A simpler no-dissociation model (single-step complete combustion)
showed a confirmed 60-70s (17-20%) Isp overestimate vs real Raptor/BE-4
engines (chamber T ~4800-4900K vs real ~3500-3900K), diagnosed as missing
dissociation physics, not a coding bug (independently confirmed via a
heat-capacity energy-balance estimate). This module directly models the
two dissociation reactions responsible, reducing chamber temperature to
3678-3825K (much closer to the real 3500-3900K range) and cutting the
Isp gap roughly in half, to 34-35s (10%).

REMAINING GAP: not modelling tertiary dissociation pathways (H2O->OH+H,
H2->2H, O2->2O, CO2->C+O2), which would further reduce T and Isp. Full
closure of the gap requires simultaneous multi-species Gibbs minimization
(true CEA-equivalent equilibrium), identified here as future work.

Simplification used: the two dissociation reactions are solved
independently against the shared total pressure (not fully coupled
through the shared O2 product pool, as true simultaneous equilibrium
would require) - an approximation, not a full multi-species solve.
"""

import numpy as np
from scipy.optimize import brentq
import nasa7_thermo_ch4 as th

R_UNIV = 8.314510
G0 = 9.80665
T_REF = 298.15

DHVAP_CH4 = 511.0  # kJ/kg, Pakalapati (2021), MSc Thesis, Politecnico di Milano, Table 3.2
DHVAP_O2 = 213.0   # kJ/kg, arXiv:1401.3125 (citing Fagerstroem and Hollis Hallet 1969)

def reactant_enthalpy(species, T_boil, dHvap_kJ_per_kg):
    """
    Computes cryogenic liquid propellant enthalpy relative to the NASA
    gas-phase polynomial reference, avoiding extrapolation below the
    200K polynomial validity floor (a bug found and fixed during
    development: directly evaluating the gas polynomial at e.g. 111.5K
    gave unphysical results).
    """
    M = th.molar_mass(species)
    dHvap_molar = dHvap_kJ_per_kg * M / 1000
    cp_200K = th.cp_molar(species, 200.0) / 1000
    dH_gas_heating = cp_200K * (200.0 - T_boil) / 1000
    h_gas_200K = th.h_molar(species, 200.0) / 1000
    h_total = h_gas_200K - dH_gas_heating - dHvap_molar
    return h_total * 1000

def Kp_reaction(products, reactants, T):
    """Kp = exp(-deltaG/RT), deltaG derived from NASA polynomial H and S."""
    dH = (sum(n*th.h_molar(sp,T) for sp,n in products.items()) -
          sum(n*th.h_molar(sp,T) for sp,n in reactants.items()))
    dS = (sum(n*th.s_molar(sp,T) for sp,n in products.items()) -
          sum(n*th.s_molar(sp,T) for sp,n in reactants.items()))
    dG = dH - T*dS
    return np.exp(-min(dG/(R_UNIV*T), 600))

def solve_dissociation(n_co2_0, n_h2o_0, n_o2_excess_0, T, P_bar):
    """Solves CO2 and H2O dissociation equilibrium (decoupled approximation)."""
    P_atm = P_bar * 0.986923

    Kp_co2 = Kp_reaction({'CO':1,'O2':0.5}, {'CO2':1}, T)
    def co2_eq(a):
        if a <= 0 or a >= 1: return 1e10*np.sign(a-0.5)
        n_co2_remain = n_co2_0*(1-a)
        n_co = n_co2_0*a
        n_o2_from_co2 = n_co2_0*a*0.5
        n_sum = n_co2_remain + n_co + n_o2_from_co2
        if n_co2_remain <= 1e-12: return 1e10
        P_co2 = n_co2_remain/n_sum * P_atm
        P_co = n_co/n_sum * P_atm
        P_o2 = n_o2_from_co2/n_sum * P_atm
        return (P_co * P_o2**0.5)/P_co2 - Kp_co2

    try:
        alpha_co2 = brentq(co2_eq, 1e-8, 0.999, xtol=1e-6) if n_co2_0 > 1e-9 else 0.0
    except ValueError:
        alpha_co2 = 0.0 if Kp_co2 < 1 else 0.999

    Kp_h2o = Kp_reaction({'H2':1,'O2':0.5}, {'H2O':1}, T)
    def h2o_eq(a):
        if a <= 0 or a >= 1: return 1e10*np.sign(a-0.5)
        n_h2o_remain = n_h2o_0*(1-a)
        n_h2 = n_h2o_0*a
        n_o2_from_h2o = n_h2o_0*a*0.5
        n_sum = n_h2o_remain + n_h2 + n_o2_from_h2o
        if n_h2o_remain <= 1e-12: return 1e10
        P_h2o = n_h2o_remain/n_sum * P_atm
        P_h2 = n_h2/n_sum * P_atm
        P_o2 = n_o2_from_h2o/n_sum * P_atm
        return (P_h2 * P_o2**0.5)/P_h2o - Kp_h2o

    try:
        alpha_h2o = brentq(h2o_eq, 1e-8, 0.999, xtol=1e-6) if n_h2o_0 > 1e-9 else 0.0
    except ValueError:
        alpha_h2o = 0.0 if Kp_h2o < 1 else 0.999

    products = {
        'CO2': n_co2_0*(1-alpha_co2),
        'CO': n_co2_0*alpha_co2,
        'H2O': n_h2o_0*(1-alpha_h2o),
        'H2': n_h2o_0*alpha_h2o,
        'O2': n_o2_excess_0 + n_co2_0*alpha_co2*0.5 + n_h2o_0*alpha_h2o*0.5,
    }
    return products, alpha_co2, alpha_h2o

def combustion_with_dissociation(OF_ratio, Pc_bar, T_fuel=111.5, T_ox=90.2):
    """Full combustion + dissociation solve, iterating T to close energy balance."""
    M_CH4 = th.molar_mass('CH4')
    M_O2 = th.molar_mass('O2')
    n_ch4 = 1.0
    n_o2_actual = n_ch4 * OF_ratio * M_CH4 / M_O2

    n_o2_stoich = 2.0
    if n_o2_actual <= n_o2_stoich:
        x_o2 = n_o2_actual
        x_ch4_reacted = x_o2/2.0
        n_co2_0 = x_ch4_reacted
        n_h2o_0 = 2*x_ch4_reacted
        n_ch4_remain = n_ch4 - x_ch4_reacted
        n_o2_excess_0 = 0.0
    else:
        n_co2_0 = n_ch4
        n_h2o_0 = 2*n_ch4
        n_ch4_remain = 0.0
        n_o2_excess_0 = n_o2_actual - n_o2_stoich

    H_react = (n_ch4 * reactant_enthalpy('CH4', T_fuel, DHVAP_CH4) +
               n_o2_actual * reactant_enthalpy('O2', T_ox, DHVAP_O2))

    T = 3700.0
    for iteration in range(60):
        products, a_co2, a_h2o = solve_dissociation(n_co2_0, n_h2o_0, n_o2_excess_0, T, Pc_bar)
        H_prod = sum(n*th.h_molar(sp,T) for sp,n in products.items()) + n_ch4_remain*th.h_molar('CH4',T)
        residual = H_prod - H_react
        dH = 50.0
        H_prod_p = sum(n*th.h_molar(sp,T+dH) for sp,n in products.items()) + n_ch4_remain*th.h_molar('CH4',T+dH)
        slope = (H_prod_p - H_prod)/dH
        dT = -residual/slope
        dT = np.clip(dT, -300, 300)
        T += dT
        if abs(dT) < 0.5:
            break

    products['CH4'] = n_ch4_remain
    return T, products, a_co2, a_h2o

def vacuum_isp(T_chamber, products, gamma=1.20, Pc_bar=270.0, Pe_bar=0.001):
    """
    Vacuum Isp via standard isentropic nozzle relation (Sutton & Biblarz
    Eq. 3-15a). gamma=1.20 default cited as standard methalox value in
    independent Raptor reverse-engineering analysis.
    """
    n_total = sum(products.values())
    if n_total <= 0:
        return 0.0
    M_avg = sum(products[sp]*th.molar_mass(sp) for sp in products)/n_total/1000
    R_specific = R_UNIV/M_avg
    Pe_Pc = Pe_bar/Pc_bar
    term = max(1 - Pe_Pc**((gamma-1)/gamma), 0)
    Ve = np.sqrt(2*gamma/(gamma-1) * R_specific * T_chamber * term)
    return Ve/G0

if __name__ == '__main__':
    print('=== METHALOX COMBUSTION WITH REAL DISSOCIATION EQUILIBRIUM ===\n')
    print('Comparing against real engine targets:')
    print('Source: Pakalapati (2021), MSc Thesis, Politecnico di Milano,')
    print('advisor Prof. L. Galfetti, Table 3.3\n')

    T_raptor, prod_raptor, a_co2_r, a_h2o_r = combustion_with_dissociation(OF_ratio=3.8, Pc_bar=270.0)
    isp_raptor = vacuum_isp(T_raptor, prod_raptor, Pc_bar=270.0)

    T_be4, prod_be4, a_co2_b, a_h2o_b = combustion_with_dissociation(OF_ratio=3.6, Pc_bar=135.0)
    isp_be4 = vacuum_isp(T_be4, prod_be4, Pc_bar=135.0)

    print(f"{'Engine':<16}{'T_chamber(K)':>14}{'alpha_CO2':>11}{'alpha_H2O':>11}{'Isp(s)':>9}{'Lit Isp(s)':>12}{'Gap':>7}")
    print('-'*82)
    print(f"{'Raptor':<16}{T_raptor:>14.0f}{a_co2_r:>11.3f}{a_h2o_r:>11.3f}{isp_raptor:>9.1f}{350:>12}{isp_raptor-350:>7.1f}")
    print(f"{'BE-4':<16}{T_be4:>14.0f}{a_co2_b:>11.3f}{a_h2o_b:>11.3f}{isp_be4:>9.1f}{340:>12}{isp_be4-340:>7.1f}")
