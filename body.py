"""
body.py — Clase CelestialBody
==============================
Representa cualquier objeto con masa: estrella, planeta, luna, asteroide.
El tipo de cuerpo determina el color automáticamente, y la masa determina
el tamaño visual en el renderer (escala logarítmica).
"""

import numpy as np

# Paleta de colores por tipo — usada si no se pasa `color` explícito
TYPE_COLORS: dict[str, str] = {
    "star":     "#FFD700",   # dorado
    "planet":   "#4FC3F7",   # azul cielo
    "moon":     "#90A4AE",   # gris azulado
    "asteroid": "#CD853F",   # marrón arena
    "custom":   "#E0E0E0",   # blanco suave
}


class CelestialBody:
    """
    Modela un cuerpo celeste con masa, posición, velocidad y trayectoria.

    Atributos físicos:
        name      : nombre descriptivo
        mass      : masa en kg
        pos       : vector posición  [x, y] en metros (numpy array)
        vel       : vector velocidad [vx, vy] en m/s  (numpy array)
        acc       : aceleración [ax, ay] — la inicializa el integrador Leapfrog

    Atributos visuales:
        body_type : "star" | "planet" | "moon" | "asteroid" | "custom"
        color     : color hex — si no se provee, se asigna según body_type
        trail     : historial de posiciones para dibujar la trayectoria
    """

    def __init__(
        self,
        name:      str,
        mass:      float,
        pos:       list,
        vel:       list,
        body_type: str       = "planet",
        color:     str|None  = None,
    ):
        # Física
        self.name  = name
        self.mass  = float(mass)
        self.pos   = np.array(pos, dtype=float)
        self.vel   = np.array(vel, dtype=float)
        # acc se añade dinámicamente por el integrador (primera llamada a leapfrog_step)

        # Visual
        self.body_type = body_type
        self.color     = color or TYPE_COLORS.get(body_type, "#E0E0E0")
        self.trail: list[np.ndarray] = []

    def update_trail(self, max_trail: int = 600) -> None:
        """Añade la posición actual al historial y elimina los más antiguos."""
        self.trail.append(self.pos.copy())
        if len(self.trail) > max_trail:
            self.trail.pop(0)

    def __repr__(self) -> str:
        return (
            f"CelestialBody(name={self.name!r}, type={self.body_type!r}, "
            f"mass={self.mass:.2e} kg, pos={self.pos}, vel={self.vel})"
        )
