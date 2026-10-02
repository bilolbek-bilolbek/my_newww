"""
Render a 9:16 vertical reel (1080x1920) explaining the normal distribution.

Outputs an MP4 if FFmpeg is available, otherwise falls back to a GIF.
"""

from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import animation
from matplotlib.animation import FFMpegWriter, FuncAnimation, PillowWriter

# ---------- Settings ----------
FPS = 30
WIDTH_IN, HEIGHT_IN, DPI = 9, 16, 120  # -> 1080 x 1920
OUT = Path("gaussian_distribution_reel.mp4")
FADE = 0.4  # seconds for text cross-fades

# ---------- Theme ----------
BG = "#0f1115"
FG = "#f2f2f2"
MUTED = "#a0a6b0"
ACCENT = "#4cc9f0"
BAND_1 = "#4cc9f0"
BAND_2 = "#f72585"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "figure.facecolor": BG,
    "axes.facecolor": BG,
    "text.color": FG,
})


# ---------- Timeline ----------
@dataclass(frozen=True)
class Scene:
    start: float
    end: float
    title: str
    subtitle: str
    caption: str


SCENES = [
    Scene(0, 5, "WHY DOES THIS SHAPE\nSHOW UP EVERYWHERE?",
          "You've probably seen it before...", ""),
    Scene(5, 11, "THE NORMAL DISTRIBUTION",
          "also called the Gaussian distribution",
          "Most observations are\nnear the average."),
    Scene(11, 18, "THE MIDDLE = THE AVERAGE",
          "Imagine the heights of 10,000 people.",
          "Most people are somewhere\naround the average."),
    Scene(18, 25, "THE FURTHER YOU GO...",
          "the fewer observations you find",
          "Extreme values are rarer."),
    Scene(25, 32, "THIS PATTERN IS EVERYWHERE",
          "Heights • test scores • measurement errors • finance",
          "Most things are normal.\nExtreme things are rare."),
]

DURATION = SCENES[-1].end
N_FRAMES = int(FPS * DURATION)

# When each visual element appears (seconds)
T_CURVE_DRAWN = 3.0  # curve finishes drawing
T_MEAN = 12.0  # mean line
T_SIGMA1 = 19.0  # ±1σ band
T_SIGMA2 = 21.5  # ±2σ band


# ---------- Helpers ----------
def ease_in_out(p: float) -> float:
    """Smoothstep easing, clamped to [0, 1]."""
    p = min(max(p, 0.0), 1.0)
    return p * p * (3 - 2 * p)


def fade_in(t: float, start: float, dur: float = FADE) -> float:
    return ease_in_out((t - start) / dur)


def scene_at(t: float) -> Scene:
    for scene in SCENES:
        if t < scene.end:
            return scene
    return SCENES[-1]


def text_alpha(t: float, scene: Scene) -> float:
    """Fade in at scene start, fade out at scene end (except the last scene)."""
    a_in = fade_in(t, scene.start)
    if scene is SCENES[-1]:
        return a_in
    a_out = 1 - ease_in_out((t - (scene.end - FADE)) / FADE)
    return min(a_in, a_out)


# ---------- Figure ----------
fig = plt.figure(figsize=(WIDTH_IN, HEIGHT_IN), dpi=DPI)
ax = fig.add_axes([0.06, 0.28, 0.88, 0.50])
ax.set_xlim(-4, 4)
ax.set_ylim(-0.06, 0.46)
ax.axis("off")

x = np.linspace(-4, 4, 1000)
pdf = np.exp(-x ** 2 / 2) / np.sqrt(2 * np.pi)

# Baseline + curve
ax.plot([-4, 4], [0, 0], color=MUTED, lw=1.5, alpha=0.5)
curve, = ax.plot([], [], lw=5, color=ACCENT, solid_capstyle="round")

# Shaded σ bands (drawn behind the curve)
band2 = ax.fill_between(x, 0, pdf, where=np.abs(x) <= 2,
                        color=BAND_2, alpha=0, lw=0, zorder=0)
band1 = ax.fill_between(x, 0, pdf, where=np.abs(x) <= 1,
                        color=BAND_1, alpha=0, lw=0, zorder=0)

# Mean line reaching exactly to the peak
peak = pdf.max()
mean_line, = ax.plot([0, 0], [0, peak], color=FG, lw=2.5, alpha=0)
mean_label = ax.text(0, peak + 0.02, "average", ha="center", va="bottom",
                     fontsize=16, color=FG, alpha=0)

# σ labels
lbl_68 = ax.text(0, 0.12, "68%", ha="center", va="center",
                 fontsize=30, fontweight="bold", color=BG, alpha=0)
lbl_95 = ax.text(0, -0.035, "95% within ±2σ", ha="center", va="center",
                 fontsize=17, color=BAND_2, alpha=0)

# Text
title = fig.text(0.5, 0.905, "", ha="center", va="center",
                 fontsize=34, fontweight="bold", linespacing=1.15)
subtitle = fig.text(0.5, 0.835, "", ha="center", va="center",
                    fontsize=18, color=MUTED)
caption = fig.text(0.5, 0.17, "", ha="center", va="center",
                   fontsize=26, fontweight="bold", linespacing=1.3)


# ---------- Animation ----------
def animate(i: int) -> None:
    t = i / FPS
    scene = scene_at(t)

    # Curve draws on with easing
    progress = ease_in_out(t / T_CURVE_DRAWN)
    n = max(2, int(len(x) * progress))
    curve.set_data(x[:n], pdf[:n])

    # Text with cross-fades
    a = text_alpha(t, scene)
    for artist, text in ((title, scene.title),
                         (subtitle, scene.subtitle),
                         (caption, scene.caption)):
        artist.set_text(text)
        artist.set_alpha(a)

    # Progressive reveal of guides
    a_mean = fade_in(t, T_MEAN)
    mean_line.set_alpha(a_mean)
    mean_label.set_alpha(a_mean)

    a1 = fade_in(t, T_SIGMA1)
    band1.set_alpha(0.55 * a1)
    lbl_68.set_alpha(a1)

    a2 = fade_in(t, T_SIGMA2)
    band2.set_alpha(0.35 * a2)
    lbl_95.set_alpha(a2)


def save(anim: FuncAnimation, out: Path) -> Path:
    """Save as MP4 if FFmpeg exists, otherwise as GIF."""
    out.parent.mkdir(parents=True, exist_ok=True)
    if animation.writers.is_available("ffmpeg"):
        anim.save(out, writer=FFMpegWriter(fps=FPS, bitrate=6000),
                  savefig_kwargs={"facecolor": BG})
        return out
    gif = out.with_suffix(".gif")
    print("FFmpeg not found - saving GIF instead (large and slow).")
    anim.save(gif, writer=PillowWriter(fps=FPS),
              savefig_kwargs={"facecolor": BG})
    return gif


if __name__ == "__main__":
    anim = FuncAnimation(fig, animate, frames=N_FRAMES,
                         interval=1000 / FPS, blit=False)
    result = save(anim, OUT)
    plt.close(fig)
    print(f"Created: {result.resolve()}")
