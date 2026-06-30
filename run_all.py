"""
Mars Propulsion Toolkit - Main Runner
Companion to: Shaikh, F. (2026), Conceptual Investigation of Environment-
Adaptive Propulsion Architectures for Martian Atmospheric Flight
"""
import os
os.makedirs('figures', exist_ok=True)

print('=' * 60)
print('MARS PROPULSION TOOLKIT')
print('Transparent MCDA Engine + Sabatier ISRU + Atmosphere Model')
print('Author: Faraz Shaikh, Sandip University (2026)')
print('=' * 60)

print('\n[1/4] Mars atmosphere model...')
import atmosphere

print('\n[2/4] Sabatier ISRU stoichiometry...')
import sabatier_isru

print('\n[3/4] Transparent MCDA engine...')
import mcda_engine
mcda_engine.verify_against_thesis()

print('\n[4/4] Adaptive Decision Matrix (phase-dependent)...')
import adm_phases
adm_phases.adm_rankings()

print('\nDone. Run individual modules directly for full output and figures.')
