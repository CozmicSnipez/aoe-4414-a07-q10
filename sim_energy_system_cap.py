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
import math

# Constant
irr_w_m2 = 1366.1  # Solar irradiance in watts per square meter

# Parse script arguments
if len(sys.argv) == 11:
    sa_m2 = float(sys.argv[1])     # Solar array area in square meters
    eff = float(sys.argv[2])       # Solar panel efficiency (fraction)
    voc = float(sys.argv[3])       # Open-circuit voltage of the solar panel in volts
    c_f = float(sys.argv[4])       # Capacitance of the capacitor in farads
    r_esr = float(sys.argv[5])     # Equivalent series resistance of the capacitor in ohms
    q0_c = float(sys.argv[6])      # Initial charge of the capacitor in coulombs
    p_on_w = float(sys.argv[7])    # Power consumption of the system when on in watts
    v_thresh = float(sys.argv[8])  # Voltage threshold for the system to turn on in volts
    dt_s = float(sys.argv[9])      # Simulation time step in seconds
    dur_s = float(sys.argv[10])    # Total simulation duration in seconds
else:
    print("Usage: python3 sim_energy_system_cap.py sa_m2 eff voc c_f r_esr q0_c p_on_w v_thresh dt_s dur_s")
    exit()

# Functions
def calc_solar_current(irr_w_m2, sa_m2, eff, voc):
    """Calculate the solar array current based on solar irradiance."""
    return (irr_w_m2 * sa_m2 * eff) / voc

def calc_node_discr(q_c, c_f, i_a, esr_ohm, power_w):
    """Calculate the discriminant for the capacitor node voltage."""
    return (q_c / c_f + i_a * esr_ohm) ** 2 - 4 * power_w * esr_ohm

def calc_node_voltage(disc, q_c, c_f, i_a, esr_ohm):
    """Calculate the node voltage using the discriminant and system parameters."""
    return (q_c / c_f + i_a * esr_ohm + math.sqrt(disc)) / 2

# Set initial values
isc_a = calc_solar_current(irr_w_m2, sa_m2, eff, voc)  # Solar array current in amperes
i1_a = isc_a                                           # Initial solar array current
qt_c = q0_c                                            # Initial charge in the capacitor
p_mode_w = p_on_w                                      # Initial power consumption
t_s = 0.0                                              # Simulation start time

node_discr = calc_node_discr(qt_c, c_f, i1_a, r_esr, p_mode_w)
if node_discr < 0.0:
    p_mode_w = 0.0  # Disable power mode if the discriminant is invalid
    node_discr = calc_node_discr(qt_c, c_f, i1_a, r_esr, p_mode_w)
node_v = calc_node_voltage(node_discr, qt_c, c_f, i1_a, r_esr)

if voc <= node_v and i1_a != 0.0:
    i1_a = 0.0

if node_v < v_thresh:
    p_mode_w = 0.0

# ITERATIVE SIMULATION
log = []  # Log to store simulation results
while t_s < dur_s:
    i3_a = p_mode_w / node_v if node_v > 0 else 0.0
    qt_c += (i1_a - i3_a) * dt_s
    if qt_c < 0.0:
        qt_c = 0.0  # Prevent negative charge
    i1_a = isc_a
    
    if p_mode_w == 0.0 and node_v >= voc:
        p_mode_w = p_on_w
    node_discr = calc_node_discr(qt_c, c_f, i1_a, r_esr, p_mode_w)
    
    if node_discr < 0.0:
        p_mode_w = 0.0  # Disable power mode if the discriminant is invalid
        node_discr = calc_node_discr(qt_c, c_f, i1_a, r_esr, p_mode_w)

    node_v = calc_node_voltage(node_discr, qt_c, c_f, i1_a, r_esr)
    
    if voc <= node_v and i1_a != 0.0:
        i1_a = 0.0
    
    if node_v < v_thresh:
        p_mode_w = 0.0
    log.append([t_s, node_v])
    t_s += dt_s

# OUTPUT
with open('./log.csv', mode='w', newline='') as outfile:
    csvwriter = csv.writer(outfile)
    csvwriter.writerow(['t_s', 'volts'])  # Write header
    for e in log:
        csvwriter.writerow(e)
