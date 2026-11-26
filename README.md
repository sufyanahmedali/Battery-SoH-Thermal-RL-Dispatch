# Manuscript reconstruction — initial executable core
This is newly written code, not the original implementation. No manuscript result is claimed reproduced. Python 3 and NumPy required. Run `python -m unittest -v`.

`model.py` implements equations 4, 7, 15–18, 23–26, 33–38. `run.py` executes the rule-based reference on user-provided hourly weather CSV (ghi W/m2, ambient Celsius, local time starting midnight). Example syntax: `python run.py --weather weather.csv --rate 1e-10 --tref 24 --entropy 0 --width 3`. Example rate, entropy and width are illustrative assumptions ONLY, not calibrated values. Seed 0, initial estimated SoH 0.8, initial temperature ambient, 60-second substeps, endpoint temperature for degradation, bus-side executed power for current, capacity overflow discarded, evening interval [18,22) are new conventions. Full hour is accounted for at threshold crossing; subhour end-of-service accounting remains to be refined. No LSTM correction is implemented: estimated SoH is propagated only. No weather data included. No annual or economic simulation has been executed. LCOE function requires externally calculated annual costs and served energy.

## Remaining work / blockers
- NASA raw MAT files and NASA POWER 2023 hourly records; original weather time convention and demand Gaussian width.
- Synthetic trajectory lengths, initial conditions, feature generation, noise convention, CX2_44 identity; exact ten features and cycle detection / pack-to-cell measurement mapping.
- Calibrate reference degradation rate using elapsed-time observations; validate pack thermal and entropy parameters.
- EKF transition/covariances and ECM resistance-capacity calibration; LSTM/Transformer training and leakage-free holdout; PPO/DDPG and MPC objectives and training, matched evaluation and sensitivity runs.
- Replacement costs, downtime, salvage, Monte Carlo distributions and lifecycle simulations. Do not use illustrative values to recover old reported metrics.
