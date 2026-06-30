"""
Mars Atmosphere Model
Source: NASA Mars Fact Sheet (NASA Goddard Space Flight Center, NSSDCA)
        https://nssdc.gsfc.nasa.gov/planetary/factsheet/marsfact.html
Verified against: Haberle et al. (Eds.), The Atmosphere and Climate of Mars,
                   Cambridge University Press, 2017.

All values cross-checked in thesis authenticity audit (Shaikh, 2026).
"""

import numpy as np

# Verified physical constants
G_MARS      = 3.71      # m/s^2 - Martian surface gravity (NASA fact sheet)
G_EARTH     = 9.81      # m/s^2 - Earth surface gravity (reference)
R_CO2       = 188.92    # J/(kg*K) - specific gas constant for CO2
P_SURFACE   = 600.0     # Pa - average Martian surface pressure (NASA)
P_EARTH     = 101325.0  # Pa - Earth sea-level pressure (reference)
RHO_SURFACE = 0.017     # kg/m^3 - average Martian surface density (0.015-0.020 range)
RHO_EARTH   = 1.225     # kg/m^3 - Earth sea-level density (reference)
T_SURFACE_AVG = 210.0   # K - average Mars surface temperature (NASA fact sheet)
T_POLE_MIN  = 148.0     # K (-125 C) - polar minimum
T_EQ_MAX    = 293.0     # K (+20 C) - equatorial daytime maximum
SPEED_OF_SOUND_MARS = 240.0  # m/s - at reference temperature (thesis Table 10.1)

# Atmospheric composition (% by volume) - NASA fact sheet / thesis Table 2.1
COMPOSITION = {
    'CO2': 95.3,
    'N2':  2.7,
    'Ar':  1.6,
    'O2':  0.13,
    'CO':  0.08,
}

def atmosphere_ratio():
    """Returns dict of Mars/Earth ratios for key atmospheric parameters."""
    return {
        'pressure_ratio': P_SURFACE / P_EARTH,
        'density_ratio': RHO_SURFACE / RHO_EARTH,
        'gravity_ratio': G_MARS / G_EARTH,
    }

def dynamic_pressure(rho, V):
    """Dynamic pressure q = 0.5 * rho * V^2 (Pa)."""
    return 0.5 * rho * V**2

def required_velocity(W, rho, S, CL):
    """
    Required flight velocity from lift equation, rearranged.
    L = 0.5*rho*V^2*S*CL = W  =>  V = sqrt(2W/(rho*S*CL))
    Ref: Thesis Eq. 10.1, Anderson, Fundamentals of Aerodynamics (2017)
    """
    return np.sqrt(2 * W / (rho * S * CL))

def lift_force(rho, V, S, CL):
    """Lift force L = 0.5*rho*V^2*S*CL (N)."""
    return 0.5 * rho * V**2 * S * CL

if __name__ == '__main__':
    print("=== MARS ATMOSPHERE MODEL ===")
    print(f"Surface gravity: {G_MARS} m/s^2 ({G_MARS/G_EARTH*100:.1f}% of Earth)")
    print(f"Surface pressure: {P_SURFACE} Pa ({P_SURFACE/P_EARTH*100:.2f}% of Earth)")
    print(f"Surface density: {RHO_SURFACE} kg/m^3 ({RHO_SURFACE/RHO_EARTH*100:.2f}% of Earth)")
    print(f"Composition: {COMPOSITION}")
