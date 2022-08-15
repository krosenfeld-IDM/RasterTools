import numpy as np

from rastertools.utils import read_json, save_json


clipped = read_json("results/clipped_pop.json")
zonal = read_json("results/zonal_pop.json")

perc_diff = {}
dot_names = set(list(clipped) + list(zonal))
for name in dot_names:
    c = clipped[name] if name in clipped else 0
    z = zonal[name] if name in zonal else 0
    if c == 0 and z == 0:
        perc_diff[name] = 0
    elif c ==0:
        perc_diff[name] = 1
    else:
        perc_diff[name] = round((c-z)/c, 2)

save_json(perc_diff, json_path="results/diff.json", sort_keys=True)
mean_diff = round(100.0 * np.mean([v for v in list(perc_diff.values())]), 0)
median_diff = round(100.0 * np.median([v for v in list(perc_diff.values())]), 0)

print("Diff greater than 20%")
for k, v in perc_diff.items():
    if abs(v) > 0.2:
        print(f"{k}: {v}")

print()
print(f"Mean diff: {mean_diff}%")
print(f"Median diff: {median_diff}%")