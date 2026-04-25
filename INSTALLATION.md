# Installation Guide

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

## Installation Methods

### Method 1: From Source (Recommended)

```bash
# Clone the repository
git clone https://github.com/4qsmkrdtp6-bot/N-body-simulator.git
cd N-body-simulator

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import numpy; import matplotlib; print('✓ Installation successful')"
```

### Method 2: Using pip

```bash
# Install from GitHub
pip install git+https://github.com/4qsmkrdtp6-bot/N-body-simulator.git

# Or install with development dependencies
pip install git+https://github.com/4qsmkrdtp6-bot/N-body-simulator.git#egg=n-body-simulator[dev]
```

### Method 3: Development Installation

```bash
# Clone and install in development mode
git clone https://github.com/4qsmkrdtp6-bot/N-body-simulator.git
cd N-body-simulator
pip install -e .
```

## Verify Installation

Run the simulator to verify everything works:

```bash
python simulator/simulador_completo.py
```

You should see a menu prompting you to select a scenario and integrator.

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'numpy'"

**Solution:**
```bash
pip install numpy matplotlib
```

### Issue: "Permission denied" on Linux/Mac

**Solution:**
```bash
chmod +x simulator/simulador_completo.py
python simulator/simulador_completo.py
```

### Issue: Virtual environment not activating

**Solution:**
Ensure you're in the correct directory and use the full path:
```bash
source /path/to/venv/bin/activate
```

## System Requirements

- **Minimum**: 512 MB RAM, 50 MB disk space
- **Recommended**: 2 GB RAM, 200 MB disk space
- **For large simulations (1000+ bodies)**: 8+ GB RAM

## Optional Dependencies

For enhanced functionality:

```bash
# For Jupyter notebook support
pip install jupyter

# For advanced visualization
pip install plotly

# For data analysis
pip install pandas scipy
```

## Getting Started

After installation, try running a simple simulation:

```python
from simulator.simulador_completo import Simulation, CelestialBody

# Create bodies
sun = CelestialBody("Sun", 1.989e30, [0, 0], [0, 0], body_type="star")
earth = CelestialBody("Earth", 5.972e24, [1.496e11, 0], [0, 29780], body_type="planet")

# Create simulation
sim = Simulation(dt=3600.0, integrator="leapfrog")
sim.add_body(sun)
sim.add_body(earth)

# Run for 365 days
for _ in range(365 * 24):
    sim.step()
    print(f"Time: {sim.time/86400:.1f} days")
```

## Need Help?

- Check the [README.md](README.md) for overview
- See [examples](examples/) for usage examples
- Open an [issue](https://github.com/4qsmkrdtp6-bot/N-body-simulator/issues) for problems
- Read the [documentation](docs/) for detailed information

## Uninstallation

```bash
pip uninstall n-body-simulator
```

---

**Happy simulating! 🚀**
