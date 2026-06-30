"""
Adaptive Decision Matrix (ADM) - Phase-Dependent MCDA
Implements the thesis's third original contribution: criterion weights
evolve across three civilisational development phases.

Source: Shaikh (2026), Thesis Chapter 11.4, Table 11.4.
"""

import numpy as np
from mcda_engine import RATINGS, rank_architectures

PHASE_WEIGHTS = {
    'Exploration Era': {
        'C1_Environmental_Compatibility': 0.25, 'C2_ISRU_Compatibility': 0.10,
        'C3_Energy_Sustainability': 0.10, 'C4_Operational_Reliability': 0.20,
        'C5_Scalability': 0.05, 'C6_Technical_Readiness': 0.20,
        'C7_Infrastructure_Demand': 0.05, 'C8_Autonomy_Compatibility': 0.05,
    },
    'Settlement Era': {
        'C1_Environmental_Compatibility': 0.20, 'C2_ISRU_Compatibility': 0.20,
        'C3_Energy_Sustainability': 0.15, 'C4_Operational_Reliability': 0.15,
        'C5_Scalability': 0.10, 'C6_Technical_Readiness': 0.10,
        'C7_Infrastructure_Demand': 0.05, 'C8_Autonomy_Compatibility': 0.05,
    },
    'Civilisation Era': {
        'C1_Environmental_Compatibility': 0.15, 'C2_ISRU_Compatibility': 0.20,
        'C3_Energy_Sustainability': 0.20, 'C4_Operational_Reliability': 0.10,
        'C5_Scalability': 0.20, 'C6_Technical_Readiness': 0.05,
        'C7_Infrastructure_Demand': 0.05, 'C8_Autonomy_Compatibility': 0.05,
    },
}

# KNOWN DISCREPANCY (documented honestly, not silently corrected):
# Thesis Table 11.4 states the Civilisation Era favours Nuclear-Electric and
# CO2-Utilisation systems. Running the actual per-criterion ratings from
# Table 11.2 against the stated Civilisation Era weights, this toolkit finds
# that DEP remains the top-ranked architecture even under those weights,
# because DEP's ratings are equal-to-or-better than Nuclear-Electric's on
# 7 of 8 criteria (only Energy Sustainability favours Nuclear, 5 vs 4).
# No combination of weights consistent with the stated Civilisation Era
# priorities is sufficient to overcome this rating dominance. This is a
# genuine inconsistency between the qualitative narrative in Thesis Section
# 11.4 and the quantitative ratings in Table 11.2, surfaced here rather than
# resolved by silently altering either table. Future thesis revision should
# either adjust the Table 11.2 ratings or revise the qualitative claim.

for phase, w in PHASE_WEIGHTS.items():
    total = sum(w.values())
    assert abs(total - 1.0) < 1e-9, f'{phase} weights sum to {total}, not 1.0'

def adm_rankings():
    """Returns dict of phase to ranking, computed live for all three eras."""
    return {phase: rank_architectures(RATINGS, weights)
            for phase, weights in PHASE_WEIGHTS.items()}

if __name__ == '__main__':
    print('=== ADAPTIVE DECISION MATRIX (ADM) - PHASE-DEPENDENT RANKING ===\n')
    results = adm_rankings()
    for phase, ranking in results.items():
        print(f'--- {phase} ---')
        for rank, arch, score in ranking:
            print(f'  {rank}. {arch}: {score:.3f}')
        print()
    print('NOTE: See source comments for a documented discrepancy between')
    print('thesis narrative and computed Civilisation Era ranking.')
