# ==================================================
# HARRY STYLES — GLOBAL TOUR MARKET INTELLIGENCE
# MASTER ANALYTICS SCRIPT
# ==================================================

import pandas as pd
import sqlite3
import os
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.animation as animation

# --------------------------------------------------
# 1️⃣ SET PROJECT DIRECTORY
# --------------------------------------------------
project_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(project_path)

# --------------------------------------------------
# 2️⃣ CONNECT TO SQLITE
# --------------------------------------------------
conn = sqlite3.connect("harry_styles_tour.db")

# --------------------------------------------------
# 3️⃣ LOAD EXCEL FILES
# --------------------------------------------------
love = pd.read_excel("data/love_on_tour.xlsx")
together = pd.read_excel("data/together_together.xlsx")

# --------------------------------------------------
# 4️⃣ CLEAN COLUMN NAMES
# --------------------------------------------------
love.columns = love.columns.str.lower().str.replace(" ", "_")
together.columns = together.columns.str.lower().str.replace(" ", "_")

love = love.dropna(subset=["venue_type"])
love = love.dropna(subset=["leg"])

# --------------------------------------------------
# 5️⃣ CREATE METRICS
# --------------------------------------------------
love["gross_per_show"] = love["gross_(usd)"] / love["shows"]
love["revenue_per_seat"] = love["gross_(usd)"] / love["tickets_sold"]
love["total_market_gross"] = love["gross_per_show"] * love["shows"]

# --------------------------------------------------
# 6️⃣ PUSH TO SQL
# --------------------------------------------------
love.to_sql("love_on_tour", conn, if_exists="replace", index=False)
together.to_sql("together_together", conn, if_exists="replace", index=False)

print("✅ Data successfully loaded into SQLite.\n")

# --------------------------------------------------
# 7️⃣ SQL QUERIES
# --------------------------------------------------

arena_stadium = pd.read_sql("""
SELECT venue_type,
       ROUND(AVG(gross_per_show),2) AS avg_gross_per_show,
       ROUND(AVG(revenue_per_seat),2) AS avg_revenue_per_seat
FROM love_on_tour
GROUP BY venue_type;
""", conn)

regional_perf = pd.read_sql("""
SELECT leg,
       ROUND(AVG(gross_per_show),2) AS avg_gross_per_show,
       ROUND(AVG(revenue_per_seat),2) AS avg_revenue_per_seat
FROM love_on_tour
GROUP BY leg;
""", conn)

concentration = pd.read_sql("""
SELECT city,
       ROUND(gross_per_show * shows, 2) AS total_market_gross,
       ROUND((gross_per_show * shows) * 100.0 /
       (SELECT SUM(gross_per_show * shows) FROM love_on_tour), 2)
       AS revenue_share_pct
FROM love_on_tour
ORDER BY total_market_gross DESC;
""", conn)

print("📊 Arena vs Stadium:\n", arena_stadium, "\n")
print("🌍 Regional Performance:\n", regional_perf, "\n")
print("💰 Revenue Concentration:\n", concentration, "\n")

# --------------------------------------------------
# 8️⃣ DARK CINEMATIC DASHBOARD
# --------------------------------------------------

plt.rcParams.update({
    "figure.facecolor": "#0A0A0F",
    "axes.facecolor": "#0A0A0F",
    "axes.labelcolor": "white",
    "xtick.color": "white",
    "ytick.color": "white",
    "text.color": "white",
    "font.family": "sans-serif"
})

market_summary = love.groupby("city", as_index=False).agg({
    "total_market_gross": "sum",
    "revenue_per_seat": "mean",
    "gross_per_show": "mean",
    "shows": "sum"
}).sort_values("total_market_gross", ascending=False)

norm = (market_summary["total_market_gross"] - market_summary["total_market_gross"].min()) / \
       (market_summary["total_market_gross"].max() - market_summary["total_market_gross"].min())

fig = plt.figure(figsize=(20, 12))
gs = gridspec.GridSpec(2, 2)

# Revenue Bars
ax1 = fig.add_subplot(gs[0, 0])
colors = plt.cm.inferno(norm)
ax1.barh(market_summary["city"], market_summary["total_market_gross"], color=colors)
ax1.invert_yaxis()
ax1.set_title("Market Revenue Concentration")

# Bubble Matrix
ax2 = fig.add_subplot(gs[0, 1])
sizes = market_summary["shows"] * 400
ax2.scatter(
    market_summary["gross_per_show"],
    market_summary["revenue_per_seat"],
    s=sizes,
    c=market_summary["total_market_gross"],
    cmap="plasma",
    edgecolors="white"
)
ax2.set_title("Pricing Power vs Scale")

# Violin
ax3 = fig.add_subplot(gs[1, 0])
sns.violinplot(
    data=love,
    x="venue_type",
    y="revenue_per_seat",
    hue="venue_type",
    legend=False,
    palette=["#00F5D4", "#FF006E"],
    ax=ax3
)
ax3.set_title("Revenue Per Seat Distribution")

# Regression
ax4 = fig.add_subplot(gs[1, 1])
sns.regplot(
    data=market_summary,
    x="shows",
    y="total_market_gross",
    scatter_kws={"s":200, "color":"#00F5D4"},
    line_kws={"color":"#FF006E"},
    ax=ax4
)
ax4.set_title("Show Volume vs Revenue")

plt.suptitle("HARRY STYLES — GLOBAL TOUR MARKET INTELLIGENCE", fontsize=18)
plt.tight_layout()
plt.savefig("tour_dashboard.png", dpi=300)
plt.show()

# --------------------------------------------------
# 9️⃣ OPTIONAL ANIMATION (SAFE MODE)
# --------------------------------------------------

try:
    fig2, ax = plt.subplots(figsize=(8, 6))
    bars = ax.barh(
        market_summary["city"],
        np.zeros(len(market_summary)),
        color=plt.cm.plasma(norm)
    )

    ax.set_xlim(0, market_summary["total_market_gross"].max()*1.1)

    def animate(frame):
        for i, bar in enumerate(bars):
            target = market_summary["total_market_gross"].iloc[i]
            bar.set_width(target * frame/100)
        return bars

    ani = animation.FuncAnimation(fig2, animate, frames=100, interval=30)

    Writer = animation.FFMpegWriter(fps=30)
    ani.save("tour_animation.mp4", writer=Writer)

    print("🎬 Animation exported as tour_animation.mp4")

except Exception as e:
    print("⚠️ Animation skipped (ffmpeg not installed).")

# --------------------------------------------------
# 🔚 CLOSE DATABASE
# --------------------------------------------------
conn.close()