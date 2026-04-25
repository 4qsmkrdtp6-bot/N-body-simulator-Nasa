"""
simulador_completo.py — Simulador de N-cuerpos gravitacionales
===============================================================

Archivo autocontenido con todas las partes:
  1. CelestialBody      — Clase de cuerpos celestes
  2. Física             — Fuerzas gravitacionales
  3. Energía            — Cinética, potencial, total
  4. Integradores       — Leapfrog, Euler-Cromer, Yoshida4
  5. Simulación         — Gestor principal
  6. Escenarios         — 4 demos predefinidas
  7. Visualización      — Panel dual (órbitas + energía)
  8. Menú Interactivo   — Interfaz de usuario

Uso:
  python simulador_completo.py
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import copy

# ═══════════════════════════════════════════════════════════════════════════════
# PARTE 1: CLASE CELESTIALBODY
# ═══════════════════════════════════════════════════════════════════════════════

TYPE_COLORS = {
    "star":     "#FFD700",
    "planet":   "#4FC3F7",
    "moon":     "#90A4AE",
    "asteroid": "#CD853F",
    "custom":   "#E0E0E0",
}


class CelestialBody:
    """Representa un cuerpo celeste con masa, posición, velocidad y trayectoria."""

    def __init__(self, name, mass, pos, vel, body_type="planet", color=None):
        self.name = name
        self.mass = float(mass)
        self.pos = np.array(pos, dtype=float)
        self.vel = np.array(vel, dtype=float)
        self.body_type = body_type
        self.color = color or TYPE_COLORS.get(body_type, "#E0E0E0")
        self.trail = []

    def update_trail(self, max_trail=600):
        """Añade posición actual al historial."""
        self.trail.append(self.pos.copy())
        if len(self.trail) > max_trail:
            self.trail.pop(0)

    def __repr__(self):
        return f"CelestialBody({self.name}, mass={self.mass:.2e} kg)"


# ═══════════════════════════════════════════════════════════════════════════════
# PARTE 2: FÍSICA GRAVITACIONAL
# ═══════════════════════════════════════════════════════════════════════════════

G = 6.674e-11  # Constante de gravitación universal


def gravitational_force(a, b):
    """Fuerza que b ejerce sobre a."""
    delta = b.pos - a.pos
    r = np.linalg.norm(delta)
    if r == 0.0:
        return np.zeros(2)
    return (G * a.mass * b.mass / r**2) * (delta / r)


def _net_acceleration(body, all_bodies):
    """Aceleración neta sobre un cuerpo."""
    total_force = np.zeros(2)
    for other in all_bodies:
        if other is not body:
            total_force += gravitational_force(body, other)
    return total_force / body.mass


# ═══════════════════════════════════════════════════════════════════════════════
# PARTE 3: ENERGÍA
# ═══════════════════════════════════════════════════════════════════════════════

def kinetic_energy(bodies):
    """Energía cinética total."""
    total = 0.0
    for body in bodies:
        v_squared = np.dot(body.vel, body.vel)
        total += 0.5 * body.mass * v_squared
    return total


def potential_energy(bodies):
    """Energía potencial gravitacional."""
    total = 0.0
    for i, body_i in enumerate(bodies):
        for body_j in bodies[i+1:]:
            r = np.linalg.norm(body_j.pos - body_i.pos)
            if r > 0:
                total -= G * body_i.mass * body_j.mass / r
    return total


def calculate_energies(bodies):
    """Calcula todas las energías."""
    ek = kinetic_energy(bodies)
    ep = potential_energy(bodies)
    return {"kinetic": ek, "potential": ep, "total": ek + ep}


# ═══════════════════════════════════════════════════════════════════════════════
# PARTE 4: INTEGRADORES NUMÉRICOS
# ═══════════════════════════════════════════════════════════════════════════════

def leapfrog_kdk(bodies, dt):
    """Integrador Leapfrog KDK (recomendado)."""
    half = dt * 0.5

    # Inicialización
    for body in bodies:
        if not hasattr(body, "acc"):
            body.acc = _net_acceleration(body, bodies)

    # KICK ½
    half_vels = [body.vel + body.acc * half for body in bodies]

    # DRIFT
    for body, v_half in zip(bodies, half_vels):
        body.pos += v_half * dt
        body.update_trail()

    # KICK ½
    for body, v_half in zip(bodies, half_vels):
        body.acc = _net_acceleration(body, bodies)
        body.vel = v_half + body.acc * half


def euler_cromer(bodies, dt):
    """Integrador Euler-Cromer (simple)."""
    for body in bodies:
        if not hasattr(body, "acc"):
            body.acc = _net_acceleration(body, bodies)

    # Actualizar velocidades
    for body in bodies:
        body.acc = _net_acceleration(body, bodies)
        body.vel += body.acc * dt

    # Actualizar posiciones
    for body in bodies:
        body.pos += body.vel * dt
        body.update_trail()


def yoshida4(bodies, dt):
    """Integrador Yoshida de orden 4 (máxima precisión)."""
    c1 = 1.0 / (2.0 * (2.0 - 2.0**(1.0/3.0)))
    c2 = 1.0 - 2.0 * c1
    d1 = 1.0 / (2.0 - 2.0**(1.0/3.0))
    d2 = -2.0**(1.0/3.0) / (2.0 - 2.0**(1.0/3.0))

    coeffs = [(c1, d1), (c2, d2), (c1, d1)]

    for c, d in coeffs:
        # KICK ½
        for body in bodies:
            if not hasattr(body, "acc"):
                body.acc = _net_acceleration(body, bodies)
            body.vel += body.acc * (c * dt / 2.0)

        # DRIFT
        for body in bodies:
            body.pos += body.vel * (d * dt)
            body.update_trail()

        # KICK ½
        for body in bodies:
            body.acc = _net_acceleration(body, bodies)
            body.vel += body.acc * (c * dt / 2.0)


# ═══════════════════════════════════════════════════════════════════════════════
# PARTE 5: SIMULACIÓN
# ═══════════════════════════════════════════════════════════════════════════════

class Simulation:
    """Gestor principal de simulación."""

    def __init__(self, dt=3600.0, integrator="leapfrog"):
        self.dt = dt
        self.integrator_name = integrator
        self.bodies = []
        self.time = 0.0
        self.energy_history = []

        # Mapeo de integradores
        self.integrators = {
            "leapfrog": leapfrog_kdk,
            "euler": euler_cromer,
            "yoshida4": yoshida4,
        }

    def add_body(self, body):
        """Añade un cuerpo a la simulación."""
        self.bodies.append(body)

    def step(self):
        """Ejecuta un paso de simulación."""
        integrator = self.integrators[self.integrator_name]
        integrator(self.bodies, self.dt)
        self.time += self.dt

        # Registrar energía
        energies = calculate_energies(self.bodies)
        self.energy_history.append(energies["total"])

    def run(self, steps):
        """Ejecuta múltiples pasos."""
        for _ in range(steps):
            self.step()

    def get_state(self):
        """Retorna el estado actual como diccionario."""
        return {
            "time": self.time,
            "bodies": [
                {
                    "name": b.name,
                    "pos": b.pos.tolist(),
                    "vel": b.vel.tolist(),
                    "mass": b.mass,
                    "trail": [p.tolist() for p in b.trail],
                }
                for b in self.bodies
            ],
            "energy": self.energy_history[-1] if self.energy_history else 0.0,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# PARTE 6: ESCENARIOS PREDEFINIDOS
# ═══════════════════════════════════════════════════════════════════════════════

def setup_circular_orbit(sim):
    """Escenario 1: Órbita circular (Tierra-Sol)."""
    # Sol
    sun = CelestialBody(
        "Sol", 1.989e30, [0, 0], [0, 0], body_type="star", color="#FFD700"
    )
    sim.add_body(sun)

    # Tierra en órbita circular
    # Velocidad circular: v = sqrt(GM/r)
    r = 1.496e11  # 1 UA
    v = np.sqrt(G * sun.mass / r)
    earth = CelestialBody(
        "Tierra", 5.972e24, [r, 0], [0, v], body_type="planet", color="#4FC3F7"
    )
    sim.add_body(earth)


def setup_elliptical_orbit(sim):
    """Escenario 2: Órbita elíptica (70% velocidad circular)."""
    sun = CelestialBody(
        "Sol", 1.989e30, [0, 0], [0, 0], body_type="star", color="#FFD700"
    )
    sim.add_body(sun)

    r = 1.496e11
    v_circular = np.sqrt(G * sun.mass / r)
    v = 0.7 * v_circular  # Órbita elíptica

    earth = CelestialBody(
        "Tierra", 5.972e24, [r, 0], [0, v], body_type="planet", color="#4FC3F7"
    )
    sim.add_body(earth)


def setup_earth_moon(sim):
    """Escenario 3: Sistema Tierra-Luna."""
    # Sol (fijo)
    sun = CelestialBody(
        "Sol", 1.989e30, [0, 0], [0, 0], body_type="star", color="#FFD700"
    )
    sim.add_body(sun)

    # Tierra
    r_earth = 1.496e11
    v_earth = np.sqrt(G * sun.mass / r_earth)
    earth = CelestialBody(
        "Tierra", 5.972e24, [r_earth, 0], [0, v_earth], body_type="planet"
    )
    sim.add_body(earth)

    # Luna (orbita Tierra)
    r_moon = 3.844e8  # distancia Tierra-Luna
    v_moon = v_earth + np.sqrt(G * earth.mass / r_moon)
    moon = CelestialBody(
        "Luna", 7.342e22, [r_earth + r_moon, 0], [0, v_moon], body_type="moon"
    )
    sim.add_body(moon)


def setup_solar_system(sim):
    """Escenario 4: Sistema Solar (snapshot)."""
    # Sol
    sun = CelestialBody(
        "Sol", 1.989e30, [0, 0], [0, 0], body_type="star", color="#FFD700"
    )
    sim.add_body(sun)

    # Mercurio
    r = 5.79e10
    v = np.sqrt(G * sun.mass / r)
    mercury = CelestialBody(
        "Mercurio", 3.285e23, [r, 0], [0, v], body_type="planet", color="#8C7853"
    )
    sim.add_body(mercury)

    # Venus
    r = 1.082e11
    v = np.sqrt(G * sun.mass / r)
    venus = CelestialBody(
        "Venus", 4.867e24, [r, 0], [0, v], body_type="planet", color="#FFC649"
    )
    sim.add_body(venus)

    # Tierra
    r = 1.496e11
    v = np.sqrt(G * sun.mass / r)
    earth = CelestialBody(
        "Tierra", 5.972e24, [r, 0], [0, v], body_type="planet", color="#4FC3F7"
    )
    sim.add_body(earth)

    # Marte
    r = 2.279e11
    v = np.sqrt(G * sun.mass / r)
    mars = CelestialBody(
        "Marte", 6.417e23, [r, 0], [0, v], body_type="planet", color="#E27B58"
    )
    sim.add_body(mars)


# ═══════════════════════════════════════════════════════════════════════════════
# PARTE 7: VISUALIZACIÓN
# ═══════════════════════════════════════════════════════════════════════════════

def visualize_simulation(sim, steps=500, scale=2.2e11):
    """Visualiza la simulación en panel dual (órbitas + energía)."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Panel 1: Órbitas
    ax1.set_aspect("equal")
    ax1.set_xlabel("X (m)")
    ax1.set_ylabel("Y (m)")
    ax1.set_title("Órbitas")
    ax1.set_xlim(-scale, scale)
    ax1.set_ylim(-scale, scale)
    ax1.grid(alpha=0.3)

    # Panel 2: Energía
    ax2.set_xlabel("Pasos")
    ax2.set_ylabel("Energía (J)")
    ax2.set_title("Conservación de Energía")
    ax2.grid(alpha=0.3)

    def animate(frame):
        ax1.clear()
        ax1.set_aspect("equal")
        ax1.set_xlim(-scale, scale)
        ax1.set_ylim(-scale, scale)
        ax1.grid(alpha=0.3)

        # Dibujar órbitas
        for body in sim.bodies:
            if body.trail:
                trail = np.array(body.trail)
                ax1.plot(trail[:, 0], trail[:, 1], color=body.color, alpha=0.5, linewidth=0.5)
            ax1.plot(body.pos[0], body.pos[1], "o", color=body.color, markersize=8, label=body.name)

        ax1.legend(loc="upper right", fontsize=8)
        ax1.set_title(f"Órbitas (t={sim.time/86400:.1f} días)")

        # Dibujar energía
        ax2.clear()
        if sim.energy_history:
            ax2.plot(sim.energy_history, color="#0EA5E9", linewidth=1.5)
            ax2.set_xlabel("Pasos")
            ax2.set_ylabel("Energía Total (J)")
            ax2.set_title("Conservación de Energía")
            ax2.grid(alpha=0.3)

        sim.step()

    anim = FuncAnimation(fig, animate, frames=steps, interval=50, repeat=True)
    plt.tight_layout()
    plt.show()


# ═══════════════════════════════════════════════════════════════════════════════
# PARTE 8: MENÚ INTERACTIVO
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Menú interactivo principal."""
    print("\n" + "="*60)
    print("SIMULADOR DE N-CUERPOS GRAVITACIONALES")
    print("="*60)

    print("\n📍 Selecciona un escenario:")
    print("  1. Órbita Circular (Tierra-Sol)")
    print("  2. Órbita Elíptica (70% velocidad circular)")
    print("  3. Sistema Tierra-Luna")
    print("  4. Sistema Solar (4 planetas)")

    scenario = input("\nEscenario (1-4): ").strip()

    print("\n⚙️  Selecciona un integrador:")
    print("  1. Leapfrog KDK (recomendado)")
    print("  2. Euler-Cromer")
    print("  3. Yoshida 4 (máxima precisión)")

    integrator_choice = input("\nIntegrador (1-3): ").strip()

    integrators = {"1": "leapfrog", "2": "euler", "3": "yoshida4"}
    integrator = integrators.get(integrator_choice, "leapfrog")

    # Crear simulación
    sim = Simulation(dt=3600.0, integrator=integrator)

    # Configurar escenario
    scenarios = {
        "1": setup_circular_orbit,
        "2": setup_elliptical_orbit,
        "3": setup_earth_moon,
        "4": setup_solar_system,
    }
    setup_func = scenarios.get(scenario, setup_circular_orbit)
    setup_func(sim)

    print(f"\n✅ Simulación iniciada con {integrator}")
    print(f"   Cuerpos: {len(sim.bodies)}")
    print(f"   Paso de tiempo: {sim.dt} segundos")

    # Visualizar
    visualize_simulation(sim, steps=500)


if __name__ == "__main__":
    main()
