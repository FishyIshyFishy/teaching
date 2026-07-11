from pathlib import Path

import numpy as np
from manim import (
    Arrow, Circle, GrowArrow, LaggedStart, Line, MathTex, Scene, Text,
    VGroup, config, smooth,
    BLUE, RED, WHITE, YELLOW, DOWN, UP,
)

TOP_Y, BOT_Y = 3.0, -3.0
PLATE_X = 6.0


def make_charge(sign, radius=0.22):
    """A red '+' charge (sign=+1) or blue '-' charge (sign=-1)."""
    color = RED if sign > 0 else BLUE
    dot = Circle(radius=radius, color=WHITE, stroke_width=2).set_fill(color, opacity=1)
    glyph = MathTex("+" if sign > 0 else "-", color=WHITE).scale(0.6)
    glyph.move_to(dot.get_center())
    charge = VGroup(dot, glyph)
    charge.sign = sign
    return charge


class FieldAndCharges(Scene):
    def construct(self):
        # --- Setup (this is the opening freeze-frame / thumbnail) ---
        top_line = Line([-PLATE_X, TOP_Y, 0], [PLATE_X, TOP_Y, 0], color=RED, stroke_width=8)
        bot_line = Line([-PLATE_X, BOT_Y, 0], [PLATE_X, BOT_Y, 0], color=BLUE, stroke_width=8)
        high_label = Text("High V", color=RED, font_size=34).next_to(top_line, UP, buff=0.2)
        low_label = Text("Low V", color=BLUE, font_size=34).next_to(bot_line, DOWN, buff=0.2)

        # Scatter a fixed (seeded) mix of + and - charges in the region between the plates.
        rng = np.random.default_rng(3)
        positions = []
        while len(positions) < 12:
            p = np.array([rng.uniform(-5.0, 5.0), rng.uniform(-2.1, 2.1), 0.0])
            if all(np.linalg.norm(p - q) > 1.2 for q in positions):
                positions.append(p)
        charges = VGroup(*[make_charge(1 if i % 2 == 0 else -1).move_to(p)
                           for i, p in enumerate(positions)])

        # Field lines drawn behind the charges when they appear.
        charges.set_z_index(2)

        self.add(top_line, bot_line, high_label, low_label, charges)
        self.wait(2)

        # --- Beat 1: electric field lines appear (high -> low, i.e. downward) ---
        self.next_section("field lines")
        field_lines = VGroup(*[
            Arrow([x, TOP_Y - 0.1, 0], [x, BOT_Y + 0.1, 0], buff=0, color=YELLOW,
                  stroke_width=4, tip_length=0.3, max_tip_length_to_length_ratio=0.06)
            for x in np.linspace(-4.5, 4.5, 7)
        ]).set_z_index(1)
        self.play(LaggedStart(*[GrowArrow(a) for a in field_lines], lag_ratio=0.08), run_time=1.5)
        self.wait(2)

        # --- Beat 2: charges migrate (+ down to low V, - up to high V) ---
        self.next_section("migration")
        self.play(
            *[c.animate.move_to([c.get_x(), BOT_Y + 0.4 if c.sign > 0 else TOP_Y - 0.4, 0])
              for c in charges],
            run_time=3, rate_func=smooth,
        )
        self.wait(1.5)


if __name__ == "__main__":
    config.media_dir = str(Path(__file__).resolve().parent.parent / "media")
    config.quality = "high_quality"  # low_quality | medium_quality | high_quality
    FieldAndCharges().render()
