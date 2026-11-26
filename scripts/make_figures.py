"""Графики к README по агрегатам из data/aggregates/ (их считает scripts/aggregate*.py по полному датасету)."""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

A = "data/aggregates/"
BLUE, ORANGE, GREY = "#2a6fdb", "#e07a1f", "#9aa5b1"
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.alpha": 0.3})

m = pd.read_csv(A + "monthly.csv")
m = m[(m.ym >= "2018-09") & (m.ym <= "2021-04")]          # до сентября 2018 — единицы объявлений, май 2021 неполный
m["date"] = pd.to_datetime(m.ym)

# 1. Динамика по рынкам и географии
import matplotlib.dates as mdates
fig, axes = plt.subplots(1, 3, figsize=(15, 4.6), sharex=True)
for ax, geo in zip(axes, ["Москва", "Санкт-Петербург", "Остальные регионы"]):
    notes = []
    for mk, c in [("вторичный", BLUE), ("первичный", ORANGE)]:
        d = m[(m.geo == geo) & (m.market == mk)].sort_values("date")
        ax.plot(d.date, d.med / 1000, color=c, lw=2, label=mk)
        a = d[d.ym == "2020-03"].med.iloc[0]; b = d[d.ym == "2021-04"].med.iloc[0]
        notes.append((f"{mk}: +{(b / a - 1) * 100:.0f}%", c))
    ax.axvline(pd.Timestamp("2020-04-01"), color=GREY, ls="--", lw=1)
    for k, (t, c) in enumerate(notes):
        ax.text(0.03, 0.93 - k * 0.08, t, transform=ax.transAxes, color=c, fontsize=10, fontweight="bold")
    ax.text(0.03, 0.77, "март 2020 → апрель 2021", transform=ax.transAxes, color=GREY, fontsize=8)
    ax.set_title(geo, fontsize=11); ax.set_ylabel("медиана, тыс. ₽ за м²" if geo == "Москва" else "")
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7])); ax.xaxis.set_major_formatter(mdates.DateFormatter("%m.%y"))
axes[0].legend(frameon=False, loc="lower right")
axes[2].annotate("скачок — смена состава\nобъявлений новостроек", (pd.Timestamp("2019-10-15"), 52), xytext=(pd.Timestamp("2019-12-01"), 42),
                 fontsize=8, color=GREY, arrowprops=dict(arrowstyle="->", color=GREY))
axes[1].text(pd.Timestamp("2020-04-20"), axes[1].get_ylim()[0] + 2, "старт льготной\nипотеки", fontsize=8, color=GREY)
fig.suptitle("С весны 2020 метр подорожал на четверть и больше, в Петербурге новостройки — на 44%", fontsize=13)
fig.tight_layout(); fig.savefig("images/price_m2_by_market.png", dpi=150); plt.close(fig)

# 2. Сезонность: отклонение медианы месяца от центрированного 12-месячного среднего (вторичка)
rows = []
for geo, d in m[m.market == "вторичный"].groupby("geo"):
    s = d.sort_values("date").set_index("date").med
    n = d.sort_values("date").set_index("date").n
    trend = s.rolling(12, center=True).mean().rolling(2).mean().shift(-1)   # 2×12 MA
    ntr = n.rolling(12, center=True).mean().rolling(2).mean().shift(-1)
    x = pd.DataFrame({"price": s / trend - 1, "listings": n / ntr - 1}).dropna()
    x["month"] = x.index.month; x["geo"] = geo
    rows.append(x)
sz = pd.concat(rows)
avg = sz.groupby("month")[["price", "listings"]].mean() * 100
fig, ax1 = plt.subplots(figsize=(9, 4.2))
months = ["янв", "фев", "мар", "апр", "май", "июн", "июл", "авг", "сен", "окт", "ноя", "дек"]
ax1.bar(months, avg.listings, color=GREY, alpha=0.5, label="число объявлений, отклонение от тренда")
ax1.set_ylabel("объявления, % от тренда")
ax2 = ax1.twinx(); ax2.grid(False); ax2.spines["right"].set_visible(True)
ax2.plot(months, avg.price, color=BLUE, marker="o", lw=2, label="цена за м², отклонение от тренда")
ax2.axhline(0, color=BLUE, lw=0.6); ax2.set_ylim(-2.5, 2.5); ax2.set_ylabel("цена, % от тренда")
h1, l1 = ax1.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
ax1.legend(h1 + h2, l1 + l2, frameon=False, loc="lower left", fontsize=9)
ax1.set_title("Летом и в начале осени метр на 1–2% ниже тренда, это меньше обычного торга", fontsize=11)
fig.tight_layout(); fig.savefig("images/seasonality.png", dpi=150); plt.close(fig)
print(avg.round(2))

# 3. Этаж и высота дома: цена относительно медианы своего региона, месяца и рынка
fl = pd.read_csv(A + "floor.csv"); hg = pd.read_csv(A + "height.csv")
fig, axes = plt.subplots(1, 2, figsize=(13, 4.3))
order = ["первый", "средний", "последний"]; x = np.arange(3); w = 0.38
for i, (mk, c) in enumerate([("вторичный", BLUE), ("первичный", ORANGE)]):
    d = fl[fl.market == mk].set_index("floor").loc[order]
    b = axes[0].bar(x + (i - 0.5) * w, (d.rel_med - 1) * 100, w, color=c, label=mk)
    axes[0].bar_label(b, fmt="%+.0f%%", fontsize=9, padding=2)
axes[0].set_xticks(x, order); axes[0].axhline(0, color="black", lw=0.6)
axes[0].set_ylabel("% к медиане региона × месяца × рынка"); axes[0].legend(frameon=False)
axes[0].set_title("На вторичке первый этаж дешевле на 12%, в новостройках почти без разницы", fontsize=10)
lv = ["2–5", "6–9", "10–16", "17–25", "26+"]; x = np.arange(5)
for i, (mk, c) in enumerate([("вторичный", BLUE), ("первичный", ORANGE)]):
    d = hg[hg.market == mk].set_index("lvlb").loc[lv]
    b = axes[1].bar(x + (i - 0.5) * w, (d.rel_med - 1) * 100, w, color=c, label=mk)
    axes[1].bar_label(b, fmt="%+.0f%%", fontsize=9, padding=2)
axes[1].set_xticks(x, lv); axes[1].set_xlabel("этажность дома"); axes[1].axhline(0, color="black", lw=0.6)
axes[1].set_title("Чем выше дом, тем дороже метр: пятиэтажки −11%, 17–25 этажей +16% (вторичка)", fontsize=10)
fig.tight_layout(); fig.savefig("images/floor_and_height.png", dpi=150); plt.close(fig)

# 4. Гипотеза про нижнюю/верхнюю половину дома
hf = pd.read_csv(A + "half.csv")
fig, ax = plt.subplots(figsize=(8, 4.2))
lv = ["2–5", "6–9", "10–16", "17+"]; x = np.arange(4)
for i, (half, c) in enumerate([("нижняя половина", BLUE), ("верхняя половина", ORANGE)]):
    d = hf[hf.half == half].set_index("hb").loc[lv]
    b = ax.bar(x + (i - 0.5) * w, d.mean_pm2 / 1000, w, color=c, label=half)
    ax.bar_label(b, fmt="%.1f", fontsize=8, padding=2)
ax.set_xticks(x, [f"{l} этажей" for l in lv])
ax.set_ylabel("средняя цена, тыс. ₽ за м²"); ax.legend(frameon=False, loc="upper left")
ax.set_title("Внутри домов одной высоты нижняя половина дороже только в малоэтажках", fontsize=11)
fig.tight_layout(); fig.savefig("images/floor_hypothesis_check.png", dpi=150); plt.close(fig)
