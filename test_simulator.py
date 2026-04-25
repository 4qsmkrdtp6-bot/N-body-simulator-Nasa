"""
test_simulator.py — Tests del simulador sin visualización
===========================================================
Ejecuta simulaciones y retorna datos para análisis.
"""

import json
from simulador_completo import (
    Simulation,
    setup_circular_orbit,
    setup_elliptical_orbit,
    setup_earth_moon,
    setup_solar_system,
    calculate_energies,
)


def run_simulation_test(scenario: int, integrator: str, steps: int = 500) -> dict:
    """
    Ejecuta una simulación y retorna los resultados.
    
    Parámetros:
        scenario: 1=circular, 2=elliptical, 3=earth-moon, 4=solar
        integrator: "leapfrog", "euler", "yoshida4"
        steps: número de pasos a simular
    
    Retorna:
        dict con resultados de la simulación
    """
    
    # Crear simulación
    sim = Simulation(dt=3600.0, integrator=integrator)
    
    # Configurar escenario
    scenarios = {
        1: setup_circular_orbit,
        2: setup_elliptical_orbit,
        3: setup_earth_moon,
        4: setup_solar_system,
    }
    
    setup_func = scenarios.get(scenario, setup_circular_orbit)
    setup_func(sim)
    
    # Registrar energía inicial
    initial_energy = calculate_energies(sim.bodies)["total"]
    
    # Ejecutar simulación
    for _ in range(steps):
        sim.step()
    
    # Calcular estadísticas
    final_energy = calculate_energies(sim.bodies)["total"]
    energy_error = abs(final_energy - initial_energy) / abs(initial_energy) if initial_energy != 0 else 0
    
    # Retornar resultados
    return {
        "scenario": scenario,
        "integrator": integrator,
        "steps": steps,
        "time_simulated_days": sim.time / 86400,
        "initial_energy": initial_energy,
        "final_energy": final_energy,
        "energy_error_percent": energy_error * 100,
        "bodies": [
            {
                "name": b.name,
                "mass": b.mass,
                "pos": b.pos.tolist(),
                "vel": b.vel.tolist(),
                "trail_length": len(b.trail),
            }
            for b in sim.bodies
        ],
    }


def compare_integrators(scenario: int, steps: int = 500) -> dict:
    """
    Compara los tres integradores en el mismo escenario.
    
    Retorna:
        dict con resultados de cada integrador
    """
    results = {}
    integrators = ["leapfrog", "euler", "yoshida4"]
    
    for integrator in integrators:
        print(f"  Ejecutando {integrator}...")
        result = run_simulation_test(scenario, integrator, steps)
        results[integrator] = result
    
    return results


if __name__ == "__main__":
    print("\n" + "="*60)
    print("TESTS DEL SIMULADOR")
    print("="*60)
    
    # Test 1: Órbita circular con Leapfrog
    print("\n📍 Test 1: Órbita Circular (Leapfrog)")
    result1 = run_simulation_test(1, "leapfrog", 365)
    print(f"   Error de energía: {result1['energy_error_percent']:.6f}%")
    print(f"   Tiempo simulado: {result1['time_simulated_days']:.1f} días")
    
    # Test 2: Comparar integradores
    print("\n⚙️  Test 2: Comparación de Integradores (Órbita Circular)")
    comparison = compare_integrators(1, 365)
    
    print("\n   Resultados:")
    for name, result in comparison.items():
        print(f"   {name:12} → Error: {result['energy_error_percent']:8.6f}%")
    
    # Test 3: Sistema Tierra-Luna
    print("\n🌍 Test 3: Sistema Tierra-Luna (Leapfrog)")
    result3 = run_simulation_test(3, "leapfrog", 500)
    print(f"   Error de energía: {result3['energy_error_percent']:.6f}%")
    print(f"   Cuerpos: {len(result3['bodies'])}")
    
    print("\n✅ Tests completados")
