"""
energy.py — Cálculo de energías en sistemas gravitacionales
============================================================
Contiene funciones para calcular energía cinética, potencial y total.
"""

import numpy as np
from body import CelestialBody

G: float = 6.674e-11  # Constante de gravitación universal


def kinetic_energy(bodies: list[CelestialBody]) -> float:
    """
    Calcula la energía cinética total del sistema.
    
    E_k = Σᵢ ½·mᵢ·|vᵢ|²
    
    Retorna:
        float: Energía cinética en Joules
    """
    total = 0.0
    for body in bodies:
        v_squared = np.dot(body.vel, body.vel)
        total += 0.5 * body.mass * v_squared
    return total


def potential_energy(bodies: list[CelestialBody]) -> float:
    """
    Calcula la energía potencial gravitacional total.
    
    E_p = Σᵢ<ⱼ −G·mᵢ·mⱼ / rᵢⱼ
    
    Retorna:
        float: Energía potencial en Joules (negativa para órbitas ligadas)
    """
    total = 0.0
    for i, body_i in enumerate(bodies):
        for body_j in bodies[i+1:]:
            r = np.linalg.norm(body_j.pos - body_i.pos)
            if r > 0:
                total -= G * body_i.mass * body_j.mass / r
    return total


def total_energy(bodies: list[CelestialBody]) -> float:
    """
    Calcula la energía total del sistema.
    
    E_total = E_k + E_p
    
    Retorna:
        float: Energía total en Joules
    """
    return kinetic_energy(bodies) + potential_energy(bodies)


def calculate_energies(bodies: list[CelestialBody]) -> dict[str, float]:
    """
    Calcula todas las energías del sistema.
    
    Retorna:
        dict con claves: "kinetic", "potential", "total"
    """
    ek = kinetic_energy(bodies)
    ep = potential_energy(bodies)
    return {
        "kinetic": ek,
        "potential": ep,
        "total": ek + ep,
    }


def energy_error(current_energy: float, initial_energy: float) -> float:
    """
    Calcula el error relativo de energía.
    
    Parámetros:
        current_energy: Energía actual
        initial_energy: Energía inicial
    
    Retorna:
        float: Error relativo (ΔE / |E₀|)
    """
    scale = abs(initial_energy) if abs(initial_energy) > 1e-12 else 1.0
    return abs(current_energy - initial_energy) / scale
