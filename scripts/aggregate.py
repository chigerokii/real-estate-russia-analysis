"""Агрегаты для графиков README из полного realty_18_21.csv (запуск: python scripts/aggregate.py data/realty_18_21.csv)."""
import pandas as pd, numpy as np
import os, sys
p = sys.argv[1] if len(sys.argv) > 1 else "data/realty_18_21.csv"
OUT = "data/aggregates/"
df = pd.read_csv(p, dtype={"price":"int64","region":"int32","building_type":"int8","level":"int16","levels":"int16","rooms":"int8","area":"float32","kitchen_area":"float32","object_type":"int8"}, parse_dates=["date"])
n0 = len(df)
df = df[(df.area.between(15, 300)) & (df.level <= df.levels) & (df.levels > 0) & (df.price > 0)]
df["pm2"] = df.price / df.area
df = df[df.pm2.between(15_000, 1_500_000)]
print("rows", n0, "kept", len(df))
df["ym"] = df.date.dt.to_period("M").astype(str)
df["geo"] = np.select([df.region == 3, df.region == 2661], ["Москва", "Санкт-Петербург"], "Остальные регионы")
df["market"] = np.where(df.object_type == 11, "первичный", "вторичный")
g = df.groupby(["ym", "geo", "market"]).agg(n=("pm2", "size"), med=("pm2", "median")).reset_index()
g.to_csv((OUT + "monthly.csv"), index=False)
# композиционно-чистое сравнение: отношение к медиане своего региона×месяца×рынка
df["base"] = df.groupby(["region", "ym", "market"]).pm2.transform("median")
df["rel"] = df.pm2 / df.base
df["floor"] = np.select([df.level == 1, df.level == df.levels], ["первый", "последний"], "средний")
df.loc[df.levels == 1, "floor"] = "одноэтажный"
f = df[df.levels > 1].groupby(["market", "floor"]).agg(n=("rel", "size"), rel_med=("rel", "median"), rel_mean=("rel", "mean")).reset_index()
f.to_csv((OUT + "floor.csv"), index=False)
df["lvlb"] = pd.cut(df.levels, [1, 5, 9, 16, 25, 200], labels=["2–5", "6–9", "10–16", "17–25", "26+"])
h = df[df.levels > 1].groupby(["market", "lvlb"], observed=True).agg(n=("rel", "size"), rel_med=("rel", "median")).reset_index()
h.to_csv((OUT + "height.csv"), index=False)
r = df.groupby(["market", "rooms"]).agg(n=("rel", "size"), rel_med=("rel", "median"), area_med=("area","median")).reset_index()
r.to_csv((OUT + "rooms.csv"), index=False)
print(f); print(h); print(r)
