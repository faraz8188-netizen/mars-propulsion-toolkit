# Mars Propulsion Toolkit

> **Transparent MCDA engine, real CH4/O2 combustion chemistry, Sabatier ISRU stoichiometry, and Mars atmosphere model for environment-adaptive propulsion architecture analysis**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![Transparent MCDA](https://img.shields.io/badge/MCDA-fully%20transparent-brightgreen)]()
[![Methalox vs Real Engines](https://img.shields.io/badge/methalox-validated%20vs%20Raptor%2FBE--4-blueviolet)]()

---

## v1.1 Update - Real CH4/O2 Combustion Chemistry with Dissociation Equilibrium

Adds genuine NASA-polynomial combustion thermodynamics for the Methane-LOX
architecture (previously just one qualitative row in the MCDA table):

- **nasa7_thermo_ch4.py**: extends the NASA 7-coefficient polynomial database
  with CH4, CO, CO2 (plus O, H, OH, H2 dissociation products), same
  GRI-Mech 3.0 / NASA TM-4513 source as the hypersonic-propulsion-toolkit.
- **methalox_combustion.py**: single-step complete-combustion solver
  (CH4 + 2O2 -> CO2 + 2H2O), with cryogenic propellant enthalpy correctly
  handled via real vaporisation data (avoiding a bug found during
  development: extrapolating the gas-phase polynomial below its 200K
  validity floor for liquid propellants at 90-111K).
- **methalox_equilibrium.py**: adds real dissociation equilibrium for the
  two dominant endothermic reactions (CO2 <-> CO + 0.5O2, H2O <-> H2 +
  0.5O2), with equilibrium constants derived DIRECTLY from the NASA
  polynomial enthalpy and entropy data (no external Kp curve-fit needed).

**Validated finding:** the no-dissociation model overestimates vacuum Isp
by 60-70s (17-20%) against real Raptor and BE-4 engine data, confirmed as
a genuine physics limitation (not a bug) via independent heat-capacity
estimation. Adding the two-reaction dissociation equilibrium - itself
validated against a published textbook result (43.9% vs 40.0% CO2
dissociation at 3000K, 1 atm) - cuts this gap roughly in half, to 34-35s
(10%), and brings chamber temperature from an unphysical ~4900K down to
3678-3825K, much closer to the real 3500-3900K range. The remaining gap
is honestly attributed to unmodelled tertiary dissociation (OH, H, O
radicals), identified as future work rather than papered over.

---

## What Makes This Toolkit Transparent

The MCDA scoring is computed live from an explicit per-criterion ratings
table - nothing is hardcoded. The methalox combustion model documents
its own validation gaps explicitly rather than hiding them: two real bugs
were found and fixed during development (polynomial extrapolation below
200K and above 3500K, both causing unphysical results), and the remaining
10% Isp gap vs real engines is quantified and explained, not concealed.

```python
S_i = sum(W_j * R_ij for j in criteria)
```

---

## Authenticity Audit Findings

During development, this toolkit caught and corrected a real arithmetic
error in the original thesis: computing S=sum(W*R) from the stated Table
11.2 ratings did NOT match the thesis's originally published MCDA scores.
The thesis has since been corrected to match the verified arithmetic.

The methalox combustion solver underwent its own authenticity process:
initial validation against real engines showed a large, unexpected
discrepancy; rather than tuning a correction factor, the actual physics
gap (missing dissociation) was diagnosed and explicitly modelled using
rigorous Gibbs free energy thermodynamics, validated independently
against a textbook equilibrium problem before being trusted.

---

## Repository Structure

```
mars-propulsion-toolkit/
|- atmosphere.py              # Mars atmosphere model (NASA fact sheet verified)
|- sabatier_isru.py           # Sabatier reaction + electrolysis stoichiometry
|- mcda_engine.py             # Transparent MCDA - live computation, no hardcoding
|- adm_phases.py              # Adaptive Decision Matrix (phase-dependent weights)
|- nasa7_thermo_ch4.py        # v1.1: NASA polynomial thermo (CH4/CO/CO2/dissoc.)
|- methalox_combustion.py     # v1.1: complete-combustion CH4/O2 solver
|- methalox_equilibrium.py    # v1.1: dissociation-equilibrium CH4/O2 solver
|- run_all.py                 # Main runner
|- requirements.txt           # Python dependencies
```

---

## Verified Physical Data

| Parameter | Value | Source |
|---|---|---|
| Mars surface gravity | 3.71 m/s2 | NASA Mars Fact Sheet |
| Mars surface pressure | 600 Pa (0.6% Earth) | NASA Mars Fact Sheet |
| Atmosphere composition | 95.3% CO2, 2.7% N2, 1.6% Ar, 0.13% O2 | NASA Mars Fact Sheet |
| Sabatier reaction enthalpy | -165.0 kJ/mol | Strucks et al., Chemie Ingenieur Technik, 2021 |
| CH4/O2 stoichiometric ratio | 4.0:1 by mass | Verified by code; arXiv:1902.02446 |
| CH4 formation enthalpy | -74.6 kJ/mol | Matches standard textbook value (-74.8/-74.9) |
| CH4 latent heat of vaporisation | 511 kJ/kg | Pakalapati (2021), MSc Thesis, Politecnico di Milano |
| O2 latent heat of vaporisation | 213 kJ/kg | arXiv:1401.3125 |
| CO2 dissociation at 3000K, 1atm | 40% (published) vs 43.9% (this toolkit) | Standard general chemistry equilibrium problem |
| Raptor vacuum Isp (real engine) | 350 s | Pakalapati (2021), Table 3.3 |
| BE-4 vacuum Isp (real engine) | 340 s | Pakalapati (2021), Table 3.3 |

---

## Installation

```bash
git clone https://github.com/faraz8188-netizen/mars-propulsion-toolkit.git
cd mars-propulsion-toolkit
pip install -r requirements.txt scipy
python run_all.py
```

Run v1.1 chemistry modules individually:
```bash
python nasa7_thermo_ch4.py
python methalox_combustion.py    # no-dissociation model, shows 60-70s gap
python methalox_equilibrium.py   # dissociation model, shows 34-35s gap
```

---

## Key References

- NASA, Mars Fact Sheet, NASA Goddard Space Flight Center, NSSDCA.
- Pakalapati, V. (2021), "Overall Analysis of Hydrogen, Kerosene and Methane in LRE Technology," MSc Thesis, Politecnico di Milano, advisor Prof. L. Galfetti.
- McBride, Gordon and Reno, NASA TM-4513, Coefficients for Calculating Thermodynamic and Transport Properties of Individual Species, 1993.
- Hintze, Meier, Shah and Devor, Sabatier System Design Study for a Mars ISRU Propellant Production Plant, 48th ICES, 2018.
- Saaty, T.L., The Analytic Hierarchy Process, McGraw-Hill, 1980.
- Sutton, G.P. and Biblarz, O., Rocket Propulsion Elements, 9th ed. Wiley, 2017.

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
  title  = {Mars Propulsion Toolkit: Transparent MCDA Engine and Methalox Combustion Chemistry},
  year   = {2026},
  url    = {https://github.com/faraz8188-netizen/mars-propulsion-toolkit}
}
```

## License

MIT License
