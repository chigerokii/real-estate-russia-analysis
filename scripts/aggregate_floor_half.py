"""Агрегаты для графиков README из полного realty_18_21.csv (запуск: python scripts/aggregate_floor_half.py data/realty_18_21.csv)."""
import pandas as pd, numpy as np
import os, sys
p = sys.argv[1] if len(sys.argv) > 1 else "data/realty_18_21.csv"
OUT = "data/aggregates/"
df = pd.read_csv(p, usecols=["price","date","region","level","levels","area","object_type"], parse_dates=["date"])
df = df[(df.area.between(15, 300)) & (df.level <= df.levels) & (df.levels > 1) & (df.price > 0)]
df["pm2"] = df.price / df.area
df = df[df.pm2.between(15_000, 1_500_000)]
df["ym"] = df.date.dt.to_period("M").astype(str)
df["rel"] = df.pm2 / df.groupby(["region", "ym", "object_type"]).pm2.transform("median")
df["half"] = np.where(df.level / df.levels < 0.5, "нижняя половина", "верхняя половина")
df["hb"] = pd.cut(df.levels, [1, 5, 9, 16, 200], labels=["2–5", "6–9", "10–16", "17+"])
out = df.groupby(["hb", "half"], observed=True).agg(n=("pm2","size"), mean_pm2=("pm2","mean"), med_pm2=("pm2","median"), rel_med=("rel","median")).reset_index()
out.to_csv(OUT + "half.csv", index=False); print(out)
print(df.groupby("half").agg(mean=("pm2","mean"), med=("pm2","median"), rel=("rel","median"), share_low_rise=("levels", lambda s: (s<=5).mean())))
