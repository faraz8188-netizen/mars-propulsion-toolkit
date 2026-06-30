"""
Sabatier Reaction and ISRU Propellant Production Model
Reaction: CO2 + 4H2 -> CH4 + 2H2O   (Sabatier and Senderens, 1897/1902)
Electrolysis: 2H2O -> 2H2 + O2

Verified thermodynamic data:
- Reaction enthalpy: dH = -165.0 kJ/mol (Strucks et al., Chemie Ingenieur
  Technik, 2021: dH298K = -165 kJ/mol)
- Reaction is exothermic, thermodynamically favoured at low T, high P
- Operates industrially at 300-400 C with nickel catalyst

NASA references for Mars ISRU application:
- Hintze, Meier, Shah and Devor, "Sabatier System Design Study for a Mars
  ISRU Propellant Production Plant," 48th ICES, Albuquerque, NM, 2018.
- Hecht et al., "Production of Oxygen by Electrolysis of CO2 on Mars:
  The MOXIE Experiment," Science Advances, vol 7, no 50, 2021.

Stoichiometric propellant mixture ratio (O2:CH4 by mass) for complete
combustion: CH4 + 2O2 -> CO2 + 2H2O requires O:F = 4.0:1 by mass (verified
by code below and confirmed in literature, e.g. arXiv:1902.02446, stating
the stoichiometric O/F ratio for the O2/CH4 reaction is 4.0). Note: real
methalox rocket engines (e.g. Raptor) deliberately run fuel-rich at O:F
~3.5-3.8:1 for performance and thermal management, NOT at the true
stoichiometric 4.0:1 ratio - this toolkit computes and reports the actual
stoichiometric value, distinct from typical engine operating ratios.
"""

import numpy as np

M_CO2 = 44.01
M_H2  = 2.016
M_CH4 = 16.04
M_H2O = 18.015
M_O2  = 32.00

DH_SABATIER = -165.0  # kJ/mol CH4 produced (verified literature value)

def sabatier_stoichiometry(moles_co2):
    """Compute Sabatier reaction stoichiometry: CO2 + 4H2 -> CH4 + 2H2O"""
    moles_h2  = 4 * moles_co2
    moles_ch4 = moles_co2
    moles_h2o = 2 * moles_co2
    return {
        'moles_CO2': moles_co2, 'moles_H2': moles_h2,
        'moles_CH4': moles_ch4, 'moles_H2O': moles_h2o,
        'mass_CO2_kg': moles_co2 * M_CO2 / 1000,
        'mass_H2_kg': moles_h2 * M_H2 / 1000,
        'mass_CH4_kg': moles_ch4 * M_CH4 / 1000,
        'mass_H2O_kg': moles_h2o * M_H2O / 1000,
        'heat_released_kJ': moles_co2 * abs(DH_SABATIER),
    }

def electrolysis_stoichiometry(moles_h2o):
    """Compute water electrolysis stoichiometry: 2H2O -> 2H2 + O2"""
    moles_h2 = moles_h2o
    moles_o2 = moles_h2o / 2
    return {
        'moles_H2O_in': moles_h2o, 'moles_H2_out': moles_h2, 'moles_O2_out': moles_o2,
        'mass_H2_kg': moles_h2 * M_H2 / 1000, 'mass_O2_kg': moles_o2 * M_O2 / 1000,
    }

def combustion_stoichiometric_ratio():
    """CH4 + 2O2 -> CO2 + 2H2O. Returns stoichiometric O2:CH4 mass ratio."""
    mass_ch4 = 1 * M_CH4
    mass_o2 = 2 * M_O2
    return mass_o2 / mass_ch4  # ~4.0:1, verified against arXiv:1902.02446

def full_isru_cycle(moles_co2_processed, h2_recycle_fraction=0.0):
    """Full ISRU propellant production cycle: Sabatier + electrolysis."""
    sab = sabatier_stoichiometry(moles_co2_processed)
    elec = electrolysis_stoichiometry(sab['moles_H2O'])
    net_o2_mass = elec['mass_O2_kg']
    net_ch4_mass = sab['mass_CH4_kg']
    actual_ratio = net_o2_mass / net_ch4_mass if net_ch4_mass > 0 else 0
    required_ratio = combustion_stoichiometric_ratio()
    return {
        'CH4_produced_kg': net_ch4_mass, 'O2_produced_kg': net_o2_mass,
        'H2_required_kg': sab['mass_H2_kg'] * (1 - h2_recycle_fraction),
        'O2_CH4_ratio_achieved': actual_ratio, 'O2_CH4_ratio_required': required_ratio,
        'oxidizer_shortfall_kg': max(0, net_ch4_mass * required_ratio - net_o2_mass),
        'heat_released_kJ': sab['heat_released_kJ'],
    }

if __name__ == '__main__':
    print('=== SABATIER REACTION STOICHIOMETRY ===')
    print(f'Reaction: CO2 + 4H2 -> CH4 + 2H2O  (dH = {DH_SABATIER} kJ/mol)')
    result = sabatier_stoichiometry(moles_co2=1000)
    print('Per 1000 mol CO2 processed:')
    for k, v in result.items():
        print(f'  {k}: {v:.2f}')
    print()
    print('=== COMBUSTION STOICHIOMETRY CHECK ===')
    ratio = combustion_stoichiometric_ratio()
    print(f'Stoichiometric O2:CH4 mass ratio = {ratio:.2f}:1')
    print('(Literature confirms 4.0:1 - arXiv:1902.02446; engines run fuel-rich ~3.5-3.8:1)')
    print()
    print('=== FULL ISRU CYCLE (no H2 recycle) ===')
    cycle = full_isru_cycle(moles_co2_processed=1000)
    for k, v in cycle.items():
        print(f'  {k}: {v:.3f}')
