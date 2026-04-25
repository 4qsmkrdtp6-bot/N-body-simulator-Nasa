"""
physics.py — Motor de física gravitacional
==========================================
Contiene:
  · gravitational_force()  — ley de Newton entre dos cuerpos
  · _net_acceleration()    — aceleración neta por todos los demás cuerpos
  · leapfrog_step()        — integrador Kick-Drift-Kick para N cuerpos

¿Por qué Leapfrog en vez de Euler-Cromer?
──────────────────────────────────────────
  Euler clásico    : error local O(dt²), la energía crece indefinidamente
  Euler-Cromer     : error local O(dt²), mejor pero asimétrico en el tiempo
  Leapfrog (KDK)   : error local O(dt³), simpléctico, reversible en el tiempo
                     → conserva la energía sin deriva secular a largo plazo

¿Cómo se calcula la aceleración?
─────────────────────────────────
  F = G·mA·mB / r²    (ley de gravitación universal de Newton)
  a = F / mA           (segunda ley de Newton)

  El vector dirección es (posB − posA) / |posB − posA|, apuntando de A hacia B.

Algoritmo Leapfrog KDK:
─────────────────────────
  Para cada tick de tiempo dt:

    KICK  ½ :  v½ = v + a_ant · (dt/2)          ← medio impulso con aceleración vieja
    DRIFT    :  x' = x + v½ · dt                ← posición completa  (TODOS primero)
    KICK  ½ :  a' = F(x') / m                   ← recalcular con posiciones nuevas
                v' = v½ + a' · (dt/2)           ← medio impulso con aceleración nueva

  La clave: actualizar TODAS las posiciones antes de recalcular NINGUNA aceleración.
  Si se hiciera cuerpo a cuerpo, algunos verían posiciones de t y otros de t+dt.
"""

import numpy as np
from body import CelestialBody

G: float = 6.674e-11   # N·m²/kg² — constante de gravitación universal


# ── Fuerza gravitacional entre dos cuerpos ──────────────────────────────────

def gravitational_force(a: CelestialBody, b: CelestialBody) -> np.ndarray:
    """
    Vector fuerza que b ejerce sobre a.

        F⃗ = G·mA·mB / r²  ·  r̂(A→B)

    Parámetros:
        a, b : los dos cuerpos
    Retorna:
        np.ndarray [Fx, Fy] en Newtons sobre el cuerpo a
    """
    delta = b.pos - a.pos                               # vector A→B
    r     = np.linalg.norm(delta)                       # distancia escalar

    if r == 0.0:                                        # evitar división por cero
        return np.zeros(2)

    return (G * a.mass * b.mass / r**2) * (delta / r)  # magnitud × dirección unitaria


# ── Aceleración neta de un cuerpo por todos los demás ──────────────────────

def _net_acceleration(body: CelestialBody,
                      all_bodies: list[CelestialBody]) -> np.ndarray:
    """
    Suma las fuerzas de todos los demás cuerpos sobre `body` y divide por su masa.

        a⃗ = Σⱼ≠ᵢ F⃗ᵢⱼ / mᵢ

    Retorna:
        np.ndarray [ax, ay] en m/s²
    """
    total_force = np.zeros(2)
    for other in all_bodies:
        if other is not body:
            total_force += gravitational_force(body, other)
    return total_force / body.mass


# ── Integrador Leapfrog Kick-Drift-Kick ─────────────────────────────────────

def leapfrog_step(bodies: list[CelestialBody], dt: float) -> None:
    """
    Avanza todos los cuerpos un paso dt con el método Leapfrog KDK.

    Soporta N cuerpos interactuando mutuamente (cada par de cuerpos
    se atrae, no solo planeta-estrella).

    La aceleración anterior se guarda en body.acc para usarla en el
    siguiente tick. Se inicializa automáticamente en la primera llamada
    sin necesidad de modificar body.py.

    Parámetros:
        bodies : lista de CelestialBody (cualquier cantidad)
        dt     : paso de tiempo en segundos
    """
    half = dt * 0.5

    # ── Inicialización (primer tick únicamente) ───────────────────────────
    # Calcula la aceleración inicial antes de mover nada
    for body in bodies:
        if not hasattr(body, "acc"):
            body.acc = _net_acceleration(body, bodies)

    # ── KICK ½ — medio impulso con la aceleración anterior ───────────────
    # Guardamos v½ en una lista para que todos partan del mismo instante t
    half_vels: list[np.ndarray] = [
        body.vel + body.acc * half
        for body in bodies
    ]

    # ── DRIFT — mover todas las posiciones con v½ ─────────────────────────
    # TODAS las posiciones se actualizan antes de recalcular ninguna fuerza
    for body, v_half in zip(bodies, half_vels):
        body.pos += v_half * dt
        body.update_trail()

    # ── KICK ½ — recalcular aceleraciones y completar el impulso ─────────
    # Con todas las posiciones en t+dt, calculamos las fuerzas correctas
    for body, v_half in zip(bodies, half_vels):
        body.acc = _net_acceleration(body, bodies)   # guardado para el próximo tick
        body.vel = v_half + body.acc * half          # velocidad completa en t+dt
