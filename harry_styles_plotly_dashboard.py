# ==========================================================
# BILLIONAIRE-LEVEL ART DIRECTION GENERATOR
# Netflix x Spotify x Data Intelligence
# FULL AUTOMATED CAROUSEL + ANIMATION
# ==========================================================

import os
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# ----------------------------------------------------------
# SET PROJECT PATH
# ----------------------------------------------------------
project_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(project_path)

# ----------------------------------------------------------
# LOAD DATA
# ----------------------------------------------------------
love = pd.read_excel("data/love_on_tour.xlsx")
love.columns = love.columns.str.lower().str.replace(" ", "_")
love = love.dropna(subset=["venue_type"])

love["gross_per_show"] = love["gross_(usd)"] / love["shows"]
love["total_market_gross"] = love["gross_per_show"] * love["shows"]

total_revenue = love["total_market_gross"].sum()
market_data = love.groupby("city")["total_market_gross"].sum().sort_values(ascending=False)

top_market = market_data.index[0]

# ----------------------------------------------------------
# AUTO LOAD IMAGES
# ----------------------------------------------------------
images = [f for f in os.listdir() if f.lower().endswith((".jpg",".jpeg",".png"))]

if len(images) < 2:
    raise Exception("Add at least 2 images (artist + world map).")

artist_img = Image.open(images[0]).convert("RGBA").resize((1080,1350))
map_img = Image.open(images[1]).convert("RGBA").resize((1080,1350)).filter(ImageFilter.GaussianBlur(3))
map_img.putalpha(70)

background = Image.alpha_composite(artist_img, map_img)

# ----------------------------------------------------------
# ADD SPOTLIGHT VIGNETTE
# ----------------------------------------------------------
vignette = Image.new("L", (1080,1350), 0)
v_draw = ImageDraw.Draw(vignette)
v_draw.ellipse((-200,200,1280,1200), fill=255)
vignette = vignette.filter(ImageFilter.GaussianBlur(250))
background.putalpha(vignette)

background = background.convert("RGBA")

# ----------------------------------------------------------
# ADD GRADIENT DARK LAYER
# ----------------------------------------------------------
grad = Image.new("RGBA", background.size, (0,0,0,0))
gdraw = ImageDraw.Draw(grad)

for y in range(1350):
    opacity = int(200 * (y/1350))
    gdraw.line([(0,y),(1080,y)], fill=(0,0,0,opacity))

background = Image.alpha_composite(background, grad)

# ----------------------------------------------------------
# LOAD FONTS
# ----------------------------------------------------------
try:
    font_big = ImageFont.truetype("Inter-Bold.ttf", 130)
    font_mid = ImageFont.truetype("Inter-Bold.ttf", 40)
    font_small = ImageFont.truetype("Inter-Regular.ttf", 28)
except:
    font_big = ImageFont.load_default()
    font_mid = ImageFont.load_default()
    font_small = ImageFont.load_default()

draw = ImageDraw.Draw(background)

# ----------------------------------------------------------
# NEON COUNTER
# ----------------------------------------------------------
def neon_text(draw, position, text, font, color):
    x,y = position
    for offset in range(1,10):
        draw.text((x-offset,y-offset), text, font=font, fill=color, anchor="mm")
    draw.text((x,y), text, font=font, fill=(255,255,255), anchor="mm")

# ----------------------------------------------------------
# ADD MASSIVE REVENUE
# ----------------------------------------------------------
draw.text((540,200), "GLOBAL TOUR INTELLIGENCE", font=font_mid, fill=(29,185,84), anchor="mm")
neon_text(draw,(540,500), f"${total_revenue/1e6:.0f}M", font_big,(29,185,84,120))
draw.text((540,620), "TOTAL REVENUE GENERATED", font=font_mid, fill=(200,200,200), anchor="mm")
draw.text((540,750), f"TOP MARKET: {top_market.upper()}", font=font_small, fill=(255,255,255), anchor="mm")

# ----------------------------------------------------------
# ADD 3D STYLE BARS
# ----------------------------------------------------------
bar_base_y = 950
max_value = market_data.max()

for i,(city,value) in enumerate(market_data.head(5).items()):
    bar_height = int((value/max_value) * 200)
    x = 150 + i*170
    draw.rectangle([x,bar_base_y-bar_height,x+100,bar_base_y], fill=(29,185,84,180))
    draw.text((x+50,bar_base_y+30), city[:3].upper(), font=font_small, fill=(255,255,255), anchor="mm")

# ----------------------------------------------------------
# SAVE SLIDE 1
# ----------------------------------------------------------
background.convert("RGB").save("slide_1_master.png", quality=95)

# ----------------------------------------------------------
# AUTO GENERATE SLIDE 2 (Histogram)
# ----------------------------------------------------------
plt.figure(figsize=(6,4))
plt.hist(market_data/1e6, bins=8, color="#1DB954")
plt.axis("off")
plt.tight_layout()
plt.savefig("slide_2_histogram.png", dpi=300)
plt.close()

# ----------------------------------------------------------
# AUTO GENERATE SLIDE 3 (Market Breakdown)
# ----------------------------------------------------------
plt.figure(figsize=(6,6))
plt.barh(market_data.index[:8], market_data.values[:8]/1e6, color="#1DB954")
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig("slide_3_market_breakdown.png", dpi=300)
plt.close()

# ----------------------------------------------------------
# ANIMATED COUNTER VERSION
# ----------------------------------------------------------
fig, ax = plt.subplots(figsize=(6,10))
fig.patch.set_facecolor("#0A0A0F")
ax.set_facecolor("#0A0A0F")
ax.axis("off")

text = ax.text(0.5,0.5,"$0M",fontsize=60,color="white",ha="center")

def animate(frame):
    value = int((total_revenue/1e6) * frame/100)
    text.set_text(f"${value}M")
    return text,

ani = animation.FuncAnimation(fig, animate, frames=100, interval=40)

try:
    Writer = animation.FFMpegWriter(fps=30)
    ani.save("slide_4_animated_counter.mp4", writer=Writer)
    print("✅ Animation exported.")
except:
    print("⚠️ ffmpeg not installed. Animation skipped.")

print("✅ FULL CAROUSEL GENERATED:")
print(" - slide_1_master.png")
print(" - slide_2_histogram.png")
print(" - slide_3_market_breakdown.png")
print(" - slide_4_animated_counter.mp4")