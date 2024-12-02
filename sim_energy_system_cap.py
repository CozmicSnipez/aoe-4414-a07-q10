# sim_energy_system_cap.py
#
# Usage: python3 sim_energy_system_cap.py sa_m2 eff voc c_f r_esr q0_c p_on_w v_thresh dt_s dur_s
# Simulates a capacitor-based energy system and logs the time and voltage to a CSV file.
# Parameters:
#  sa_m2: Solar array area in square meters
#  eff: Solar panel efficiency (0 < eff <= 1)
#  voc: Open-circuit voltage of the solar panel in volts
#  c_f: Capacitance of the capacitor in farads
#  r_esr: Equivalent series resistance of the capacitor in ohms
#  q0_c: Initial charge of the capacitor in coulombs
#  p_on_w: Power consumption of the system when on in watts
#  v_thresh: Voltage threshold for the system to turn on in volts
#  dt_s: Time step for the simulation in seconds
#  dur_s: Duration of the simulation in seconds
# Output:
#  Writes a CSV file `log.csv` containing time (t_s) and voltage (volts).
#
# Written by Nick Davis
# Other contributors: None
#
# This work is licensed under CC BY-SA 4.0

# Import necessary modules
import sys
import csv

# Parse script arguments
if len(sys.argv) == 11:
    sa_m2 = float(sys.argv[1])     # Solar array area in square meters
    eff = float(sys.argv[2])       # Solar panel efficiency
    voc = float(sys.argv[3])       # Open-circuit voltage of the solar panel in volts
    c_f = float(sys.argv[4])       # Capacitance of the capacitor in farads
    r_esr = float(sys.argv[5])     # Equivalent series resistance in ohms
    q0_c = float(sys.argv[6])      # Initial charge in coulombs
    p_on_w = float(sys.argv[7])    # Power consumption in watts
    v_thresh = float(sys.argv[8])  # Voltage threshold in volts
    dt_s = float(sys.argv[9])      # Time step in seconds
    dur_s = float(sys.argv[10])    # Duration in seconds

    # Validate inputs
    if not (0 < eff <= 1):
        print("Error: Efficiency must be in the range (0, 1].")
        exit()
    if any(v < 0 for v in [sa_m2, voc, c_f, r_esr, q0_c, p_on_w, v_thresh, dt_s, dur_s]):
        print("Error: All parameters must be non-negative.")
        exit()

    # Initialize simulation variables
    solar_power_w = sa_m2 * eff * voc  # Solar power in watts
    charge_c = q0_c                    # Initial charge in coulombs
    log = []                           # List to store time and voltage
    time_s = 0                         # Simulation time in seconds

    # Simulation loop
    while time_s <= dur_s:
        voltage_v = charge_c / c_f
        
        if voltage_v >= v_thresh:
            current_on_a = p_on_w / voltage_v if voltage_v > 0 else 0
            discharge_c = current_on_a * dt_s
        else:
            discharge_c = 0

        charge_in_c = (solar_power_w / voltage_v if voltage_v > 0 else 0) * dt_s
        charge_c += charge_in_c - discharge_c
        esr_voltage_drop = r_esr * (charge_in_c - discharge_c) / dt_s if dt_s > 0 else 0
        voltage_v = max(voltage_v - esr_voltage_drop, 0)  # Makes sure voltage stays non-negative
        log.append((time_s, voltage_v))

        time_s += dt_s

    # Write results to CSV file
    with open('./log.csv', mode='w', newline='') as outfile:
        csvwriter = csv.writer(outfile)
        csvwriter.writerow(['t_s', 'volts'])
        for e in log:
            csvwriter.writerow(e)

else:
    print("Usage: python3 sim_energy_system_cap.py sa_m2 eff voc c_f r_esr q0_c p_on_w v_thresh dt_s dur_s")
    exit()
