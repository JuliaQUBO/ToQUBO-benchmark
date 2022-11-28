import matplotlib.pyplot as plt
from pandas import read_csv
import scienceplots

toqubo_data = read_csv("./benchmark/ToQUBO/tsp_ToQUBO.csv")
pyqubo_current_data = read_csv("./benchmark/pyqubo/tsp_pyqubo.csv")
pyqubo_040_data = read_csv("./benchmark/pyqubo_040/tsp_pyqubo_040.csv")

plt.figure(figsize = (5,4))

plt.style.use(['science','no-latex'])

plt.plot(toqubo_data["n_var"], toqubo_data["time"], label = "ToQUBO 0.1.3", marker='o')
plt.plot(pyqubo_current_data["n_var"], pyqubo_current_data["time"], label = "PyQUBO 1.3.1", marker='o')
plt.plot(pyqubo_040_data["n_var"], pyqubo_040_data["time"], label = "PyQUBO 0.4.0", marker='o')



plt.xscale('symlog')
plt.yscale('symlog')
plt.xlabel("#variables")
plt.ylabel("Execution Time(sec)")
plt.grid(True)
plt.legend()
plt.savefig('benchmark.png')

plt.show()