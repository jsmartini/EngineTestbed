import numpy as np
import skfuzzy.control as ctrl
import asyncio
import skfuzzy as fuzz
import matplotlib.pyplot as plt


#universe variables
#0 psi -> 5000 psi
pressure = np.arange(0, 1200, 1)
vent = np.arange(0,2,1)
#LOX
p_low = fuzz.trimf(pressure, [0,0,300])
p_nom = fuzz.trimf(pressure, [0,300, 700])
p_high = fuzz.trimf(pressure, [500, 700, 800])
p_danger = fuzz.trimf(pressure, [600, 800, 1200])
LOX_no_vent = fuzz.trimf(vent, [0,0,1])
LOX_vent = fuzz.trimf(vent, [0,1,2])

#Kerosense



#rules

p_low_level = fuzz.interp_membership(pressure, p_low, 650)
p_nom_level = fuzz.interp_membership(pressure, p_nom, 650)
p_high_level= fuzz.interp_membership(pressure, p_high, 650)
p_danger_level = fuzz.interp_membership(pressure, p_danger, 650)

low = np.fmin(p_nom_level, p_low_level)
nom = np.fmax(p_nom_level, p_low_level)
high = np.fmin(p_nom_level, p_high_level)
danger = np.fmax(p_danger_level, p_high_level)




a_spc = np.zeros_like(vent)
a = fuzz.defuzz(vent, , "centroid")
print(a)


fig, (ax, ax2) = plt.subplots(nrows=2)

ax.plot(pressure, p_low, label="low")
ax.plot(pressure, p_nom, label="nom")
ax.plot(pressure, p_high, label = "high")
ax.plot(pressure, p_danger, label="danger")
ax.legend()

ax2.plot(vent, LOX_no_vent, label="no vent")
ax2.plot(vent, LOX_vent, label = "vent")
ax2.legend()
plt.show()