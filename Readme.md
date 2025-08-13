# AeroForge Framework Supplementary Code

This repository contains open-source computational tools supporting the AeroForge research paper on aluminum-ion (Al-ion) batteries with silicon carbide (SiC) integration for ultra-long-range electric aviation.

## Overview
- Implements Monte Carlo analysis, range calculations, and Simulink modeling.
- Reproduces results like 5000+ km mean range with 50%+ probability for 5,000+ km.
- For details, see the paper [link to DOI or PDF].

## Files
- **python/aeroforge_analysis.py**: Monte Carlo simulation in Python.
- **matlab/aeroForge_RangeCalc.m**: Core range calculation function.
- **matlab/build_AlIon_sic_simulinkmodel.m**: Builds Simulink model.
- **matlab/run_AeroForge_montecarlo.m**: Runs Monte Carlo analysis.

## Requirements
- Python 3.x: See requirements.txt (run `pip install -r requirements.txt`).
- MATLAB R2020a+ with Simulink.

## How to Run
1. For Python: `python python/aeroforge_analysis.py` (generates CSV and plots).
2. For MATLAB: Open `matlab/run_AeroForge_montecarlo.m` and run it.
- Use seed 42 for reproducible results.

## License
MIT License — feel free to use and modify.

