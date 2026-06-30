"""
Transparent Multi-Criteria Decision Analysis (MCDA) Engine
For Martian Propulsion Architecture Selection

This module makes the MCDA scoring fully transparent and verifiable:
unlike a black-box result, every weighted score here is COMPUTED LIVE
from an explicit per-criterion ratings table - nothing is hardcoded.

Source: Shaikh, F. (2026), Conceptual Investigation of Environment-
Adaptive Propulsion Architectures for Martian Atmospheric Flight,
Chapter 11, Tables 11.1-11.4 (corrected scores, verified by this toolkit).

Methodology references:
- Saaty, T.L., The Analytic Hierarchy Process, McGraw-Hill, 1980.
- Vincke, P., Multicriteria Decision-Aid, Wiley, 1992.

IMPORTANT: The per-criterion ratings (R_ij, 1-5 scale) below represent
the author's subjective engineering judgement, exactly as in any real-world
MCDA study. This toolkit does not claim these ratings are objectively
true - it claims only that the weighted score is correctly and verifiably
computed FROM these stated ratings, which is the actual authenticity gap
this toolkit closes.
"""

import numpy as np

WEIGHTS = {
    'C1_Environmental_Compatibility': 0.20,
    'C2_ISRU_Compatibility':          0.15,
    'C3_Energy_Sustainability':       0.15,
    'C4_Operational_Reliability':     0.15,
    'C5_Scalability':                 0.10,
    'C6_Technical_Readiness':         0.10,
    'C7_Infrastructure_Demand':       0.05,
    'C8_Autonomy_Compatibility':      0.10,
}

assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9, "Weights must sum to 1.0"

# Per-criterion ratings (1=Very Poor, 5=Excellent) - Thesis Table 11.2
RATINGS = {
    'Methane-LOX':     {'C1_Environmental_Compatibility':4,'C2_ISRU_Compatibility':5,'C3_Energy_Sustainability':4,'C4_Operational_Reliability':4,'C5_Scalability':4,'C6_Technical_Readiness':3,'C7_Infrastructure_Demand':3,'C8_Autonomy_Compatibility':4},
    'Solar-Electric':  {'C1_Environmental_Compatibility':5,'C2_ISRU_Compatibility':5,'C3_Energy_Sustainability':4,'C4_Operational_Reliability':3,'C5_Scalability':3,'C6_Technical_Readiness':5,'C7_Infrastructure_Demand':5,'C8_Autonomy_Compatibility':5},
    'Nuclear-Electric':{'C1_Environmental_Compatibility':4,'C2_ISRU_Compatibility':3,'C3_Energy_Sustainability':5,'C4_Operational_Reliability':4,'C5_Scalability':5,'C6_Technical_Readiness':2,'C7_Infrastructure_Demand':2,'C8_Autonomy_Compatibility':4},
    'Hybrid':          {'C1_Environmental_Compatibility':4,'C2_ISRU_Compatibility':5,'C3_Energy_Sustainability':4,'C4_Operational_Reliability':5,'C5_Scalability':4,'C6_Technical_Readiness':3,'C7_Infrastructure_Demand':2,'C8_Autonomy_Compatibility':5},
    'CO2_Utilisation': {'C1_Environmental_Compatibility':5,'C2_ISRU_Compatibility':5,'C3_Energy_Sustainability':2,'C4_Operational_Reliability':2,'C5_Scalability':3,'C6_Technical_Readiness':1,'C7_Infrastructure_Demand':3,'C8_Autonomy_Compatibility':3},
    'DEP':             {'C1_Environmental_Compatibility':5,'C2_ISRU_Compatibility':5,'C3_Energy_Sustainability':4,'C4_Operational_Reliability':5,'C5_Scalability':5,'C6_Technical_Readiness':4,'C7_Infrastructure_Demand':4,'C8_Autonomy_Compatibility':5},
}

def compute_weighted_score(ratings_row, weights=WEIGHTS):
    """Computes S = sum(W_j * R_j). This is the ONLY place scores are computed."""
    return sum(weights[c] * ratings_row[c] for c in weights)

def compute_all_scores(ratings=RATINGS, weights=WEIGHTS):
    """Returns dict of architecture to weighted_score, computed live."""
    return {arch: compute_weighted_score(r, weights) for arch, r in ratings.items()}

def rank_architectures(ratings=RATINGS, weights=WEIGHTS):
    """Returns list of (rank, architecture, score) sorted descending."""
    scores = compute_all_scores(ratings, weights)
    sorted_scores = sorted(scores.items(), key=lambda x: -x[1])
    return [(i+1, arch, score) for i, (arch, score) in enumerate(sorted_scores)]

def sensitivity_analysis(criterion, weight_range, ratings=RATINGS, base_weights=WEIGHTS):
    """Re-runs ranking varying ONE criterion weight, renormalising the rest."""
    results = {}
    other_criteria = [c for c in base_weights if c != criterion]
    other_total = sum(base_weights[c] for c in other_criteria)
    for w in weight_range:
        new_weights = dict(base_weights)
        new_weights[criterion] = w
        remaining = 1.0 - w
        for c in other_criteria:
            new_weights[c] = base_weights[c] / other_total * remaining
        results[w] = rank_architectures(ratings, new_weights)
    return results

def verify_against_thesis():
    """Cross-check toolkit computation against corrected thesis values."""
    thesis_corrected = {
        'DEP': 4.70, 'Solar-Electric': 4.35, 'Hybrid': 4.20,
        'Methane-LOX': 4.00, 'Nuclear-Electric': 3.80, 'CO2_Utilisation': 3.20,
    }
    computed = compute_all_scores()
    print('=== VERIFICATION: Toolkit computation vs. corrected thesis values ===')
    print(f"{'Architecture':<18}{'Thesis':>10}{'Toolkit':>10}{'Match?':>8}")
    all_match = True
    for arch, thesis_val in thesis_corrected.items():
        comp_val = computed[arch]
        match = abs(comp_val - thesis_val) < 0.01
        all_match &= match
        print(f"{arch:<18}{thesis_val:>10.2f}{comp_val:>10.3f}{'PASS' if match else 'FAIL':>8}")
    print(f'\nAll scores match: {all_match}')
    return all_match

if __name__ == '__main__':
    print('=== TRANSPARENT MCDA ENGINE ===\n')
    print('Criterion weights (Table 11.1):')
    for c, w in WEIGHTS.items():
        print(f'  {c}: {w*100:.0f}%')
    print(f'  TOTAL: {sum(WEIGHTS.values())*100:.0f}%\n')
    print('=== LIVE-COMPUTED RANKING ===')
    ranking = rank_architectures()
    print(f"{'Rank':<6}{'Architecture':<18}{'Score':>8}")
    for rank, arch, score in ranking:
        print(f'{rank:<6}{arch:<18}{score:>8.3f}')
    print()
    verify_against_thesis()
