# Mars Propulsion Toolkit

> **Transparent MCDA engine, Sabatier ISRU stoichiometry, and Mars atmosphere model for environment-adaptive propulsion architecture analysis**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![Transparent MCDA](https://img.shields.io/badge/MCDA-fully%20transparent-brightgreen)]()

---

## Companion Thesis

This toolkit is the computational companion to:

**A Conceptual Investigation of Environment-Adaptive Propulsion Architectures for Martian Atmospheric Flight**
Faraz Shaikh | Independent Research | 2026

Five original frameworks: EAPA, PHAP, ADM, MTNH, TCI. This toolkit implements and verifies the quantitative core of the thesis - the Multi-Criteria Decision Analysis (MCDA) underlying the Adaptive Decision Matrix (ADM).

---

## What Makes This Toolkit Transparent

The thesis's original MCDA result was presented as a final answer with no visible derivation. This toolkit closes that gap: every weighted score is computed live from an explicit per-criterion ratings table - nothing is hardcoded.

```python
S_i = sum(W_j * R_ij for j in criteria)
```

Change any rating in mcda_engine.py and the score recalculates automatically. The ratings are still the author's subjective engineering judgement (as in any real MCDA study), but the arithmetic connecting them to the final score is now fully inspectable.

---

## Authenticity Audit Findings

During development, this toolkit caught and corrected a real arithmetic error in the original thesis: computing S=sum(W*R) from the stated Table 11.2 ratings did NOT match the thesis's originally published scores (errors of 0.05-0.20 across all 6 architectures). The thesis has since been corrected to match the verified arithmetic.

This toolkit also surfaces an unresolved discrepancy (documented in adm_phases.py): the thesis narrative claims Nuclear-Electric should rank highest in the Civilisation Era, but computing the actual ratings against the stated era weights shows DEP remains top-ranked, because DEP's ratings dominate Nuclear-Electric's on 7 of 8 criteria. This is surfaced honestly rather than silently resolved.

---

## Repository Structure

```
mars-propulsion-toolkit/
|- atmosphere.py       # Mars atmosphere model (NASA fact sheet verified)
|- sabatier_isru.py    # Sabatier reaction + electrolysis stoichiometry
|- mcda_engine.py      # Transparent MCDA - live computation, no hardcoding
|- adm_phases.py       # Adaptive Decision Matrix (phase-dependent weights)
|- run_all.py          # Main runner
|- requirements.txt    # Python dependencies
```

---

## Verified Physical Data

| Parameter | Value | Source |
|---|---|---|
| Mars surface gravity | 3.71 m/s2 | NASA Mars Fact Sheet |
| Mars surface pressure | 600 Pa (0.6% Earth) | NASA Mars Fact Sheet |
| Mars surface density | 0.017 kg/m3 (~1/72 Earth) | NASA Mars Fact Sheet |
| Atmosphere composition | 95.3% CO2, 2.7% N2, 1.6% Ar, 0.13% O2 | NASA Mars Fact Sheet |
| Sabatier reaction enthalpy | -165.0 kJ/mol | Strucks et al., Chemie Ingenieur Technik, 2021 |
| CH4/O2 stoichiometric ratio | 4.0:1 by mass | Verified by code; arXiv:1902.02446 |

---

## Installation

```bash
git clone https://github.com/faraz8188-netizen/mars-propulsion-toolkit.git
cd mars-propulsion-toolkit
pip install -r requirements.txt
python run_all.py
```

Run individual modules for detailed output:
```bash
python mcda_engine.py
python adm_phases.py
python sabatier_isru.py
python atmosphere.py
```

---

## Key References

- NASA, Mars Fact Sheet, NASA Goddard Space Flight Center, NSSDCA.
- Haberle et al. (Eds.), The Atmosphere and Climate of Mars, Cambridge University Press, 2017.
- Hintze, Meier, Shah and Devor, Sabatier System Design Study for a Mars ISRU Propellant Production Plant, 48th ICES, 2018.
- Hecht et al., Production of Oxygen by Electrolysis of CO2 on Mars: The MOXIE Experiment, Science Advances, 2021.
- Saaty, T.L., The Analytic Hierarchy Process, McGraw-Hill, 1980.
- Vincke, P., Multicriteria Decision-Aid, Wiley, 1992.

---

## Author

**Faraz Shaikh**
B.Tech Aerospace Engineering | Sandip University, Nashik, India | CGPA: 7.84/10

Research interests: Hypersonic propulsion, spacecraft propulsion, planetary aviation, detonation-based engines.

---

## Citation

```bibtex
@software{shaikh2026marspropulsion,
  author = {Shaikh, Faraz},
  title  = {Mars Propulsion Toolkit: Transparent MCDA Engine for Environment-Adaptive Propulsion Architecture Analysis},
  year   = {2026},
  url    = {https://github.com/faraz8188-netizen/mars-propulsion-toolkit}
}
```

## License

MIT License
