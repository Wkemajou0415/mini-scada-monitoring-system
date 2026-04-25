#Setup
import time
from collections import Counter
import matplotlib.pyplot as plt
import csv


state_history = []
records =[]
critical_events = []

def current_check (c):
    if c > 120:
        return "Critical"
    elif 100 < c <= 120:
        return "Warning"
    else:
        return "Normal"
    
currents = [95, 105, 130, 110, 125, 90, 140]
voltages = [400, 398, 405, 399, 401, 397, 406]

critical_count = 0
warning_count = 0
normal_count = 0

previous_state = None

for c, v in zip (currents, voltages):
    status = current_check (c)

#Status Count
    if status == "Critical":
        critical_count +=1
        event = "FAULT"
    elif status == "Warning":
        warning_count +=1
        event = "ALERT"
    else:
        normal_count +=1
        event = "OK"

#Power Status
    power = c * v

    if power > 50000:
        power_status = "High Power"
    elif power >= 40000:
        power_status = "Normal Power"
    else:
        power_status = "Low Power"

#System State Status
    if critical_count >=2:
        system_state = "SHUTDOWN"
    elif warning_count >=3:
        system_state = "UNSTABLE"
    else:
        system_state = "STABLE"

#Alert and Fault Time
    time.sleep(1)
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    if event == "ALERT":
        print(f"\nAlert time:{timestamp}")
    elif event == "FAULT":
        print(f"\nFault time:{timestamp}")

#System State Changes
    if previous_state is None:
        previous_state = system_state
        print(f"Initial system state: {system_state} at {timestamp}")
    elif system_state != previous_state:
        print(f"\n⚠️ System state changed: {previous_state} → {system_state} at {timestamp}")
        previous_state = system_state
        
#State History Records
    state_history.append (system_state)
    records.append({
        "current": c, 
        "voltage": v, 
        "power": power, 
        "status": status, 
        "power_status": power_status, 
        "event": event, 
        "system_state": system_state, 
        "normal_count": normal_count, 
        "warning_count": warning_count, 
        "critical_count": critical_count, 
        "timestamp": timestamp
    })
#Critical Event Records
    if status == "Critical":
        critical_events.append({
        "time": timestamp,
        "current": c,
        "power": power
        }) 

    if critical_count >= 2 or (warning_count >=3 and normal_count == 0):
        break

#State Count
state_count = Counter (state_history)
print("\nSystem state duration:")
for state, count in state_count.items ():
    print(f"{state}: {count} cycles")

#Dominant Behavior
if state_count:    
    dominant_state = max (state_count, key=state_count.get)    
    print(f"\nDominant system state: {dominant_state} ({state_count[dominant_state]} cycles)")
else:    
    print("\nNo data available.")

#State Percentage
if state_count:
    total = sum(state_count.values())

    for state, count in state_count.items():
        percent = (count / total) * 100
        print (f"{state}: {count} cycles ({percent:.1f}%)")

#Table Summary
print ("\nTable:")
print ("-"*100)
print (f"{'current':<10}   {'voltage':<10}   {'power':<10}   {'status':<13}   {'pwr_status':<13}  {'event':<13}  {'System state':<13} ")
print("-"*100)
for r in records:
    print (f"{r["current"]:<10}   {r["voltage"]:<10}   {r["power"]:<10}   {r["status"]:<13}   {r["power_status"]:<13}   {r["event"]:<13}   {r["system_state"]:<10} ")
print("-"*100)

#Average Power
if records:
    total_power = sum (r["power"] for r in records) 
    avg_power = total_power / len (records)
else:
    avg_power = 0
print(f"\nAverage Power: {avg_power: .1f} W")

#Health Score and Status
if records:
    health_score = normal_count/len(records)*100
else:
    health_score = 0

print(f"\nSystem Health Score:{health_score:.1f}%")

if health_score > 70:
    print ("System is healthy")
elif health_score >40:
    print("System needs monitoring")
else:
    print("System is critical")

#Summary Count
print("\nSummary counts:")
print (f"Normal counts:{normal_count} \nWarning counts: {warning_count} \nCritical counts:{critical_count}")

#System State Status
if system_state == "STABLE":
    print("\nSystem operation normally.")
elif system_state == "UNSTABLE":
    print("\nWarning: system instability detected.")
else:
    print("\nCritical default: system shutdown triggered")

#Critical Event Details
print("\nCritical Event:")
for r in records:
    if r ["status"] == "Critical":
        print (f"{r['timestamp']}  |  {r['current']} A  |  {r['power']} W")

#Last System State 
if records:
    print("\nLast system state:", records[-1]["system_state"])
else:
    print("\nNo records available.")


# Prepare data
cycles = list(range(1, len(records) + 1))
power_values = [r["power"] for r in records]

# Graph
plt.figure(figsize=(8, 5))

plt.plot(cycles, power_values, marker="o", label="Power")

# Highlight critical points
critical_added = False

for i, r in enumerate(records):
    if r["status"] == "Critical":
        if not critical_added:
            plt.scatter(cycles[i], power_values[i], s=120, color="red", label="Critical")
            critical_added = True
        else:
            plt.scatter(cycles[i], power_values[i], s=120, color="red")

# Add FAULT label next to critical point
        plt.text(
            cycles[i],
            power_values[i] + 1500,
            "FAULT",
            fontsize=10,
            fontweight="bold",
            ha="center",
            color="red"
        )

plt.legend()

plt.title("Electrical Monitoring System - Power Trend Analysis")
plt.xlabel("Cycle")
plt.ylabel("Power (W)")
plt.grid(True)

plt.tight_layout()
plt.savefig("scada_power_graph.png", dpi=300)
plt.show()


# Export Mini SCADA Report to CSV
filename = "mini_scada_report.csv"

with open(filename, "w", newline="") as file:
    writer = csv.writer(file)

    # Header row
    writer.writerow([
        "Timestamp",
        "Current (A)",
        "Voltage (V)",
        "Power (W)",
        "Status",
        "Power Status",
        "Event",
        "System State"
    ])

    # Data rows
    for r in records:
        writer.writerow([
            r["timestamp"],
            r["current"],
            r["voltage"],
            r["power"],
            r["status"],
            r["power_status"],
            r["event"],
            r["system_state"]
        ])

print(f"\nCSV report exported successfully: {filename}")
