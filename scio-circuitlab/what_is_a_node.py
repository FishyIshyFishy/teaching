from pathlib import Path

import numpy as np
from manim import (
    Arrow, Create, Dot, FadeIn, FadeOut, FadeTransform, Flash, GrowArrow, Indicate,
    LaggedStart, MathTex, ReplacementTransform, Rotate, Scene,
    SurroundingRectangle, SVGMobject, VGroup, Write, config,
    BLUE, ORANGE, TEAL, WHITE, YELLOW, DL, DOWN, LEFT, RIGHT, UP, PI,
)

CIRC = Path(__file__).parent / "circuits"

# tikz \useasboundingbox baked into each svg -> exact tikz->manim coord mapping
BASE_BBOX = (4.4, 5.2, 12.6, 8.8)
W1_BBOX = (4.2, 5.2, 12.6, 12.2)
W2_BBOX = (3.3, 5.2, 12.6, 10.8)

# per-variant resistor branches: (far end, node end, colour, subscript)
BASE_SPECS = [((5, 8), (8, 8), BLUE, "1"), ((8, 6), (8, 8), TEAL, "2"), ((11, 8), (8, 8), ORANGE, "3")]
W1_SPECS = [((6.284, 11.992), (6.284, 8.992), BLUE, "1"), ((8, 6), (8, 8), TEAL, "2"),
            ((11.02, 9.421), (8.02, 9.421), ORANGE, "3")]
W2_SPECS = [((3.847, 9.789), (6.847, 9.789), BLUE, "1"), ((8, 6), (8, 8), TEAL, "2"),
            ((9.695, 7.388), (9.695, 10.388), ORANGE, "3")]

DERIV = [0.0, -2.5, 0.0]


def make_P(mob, bbox):
    """Return a tikz->manim mapping for an svg placed at its current transform."""
    bx0, by0, bx1, by1 = bbox

    def P(tx, ty):
        dl = mob.get_corner(DL)
        return dl + np.array([(tx - bx0) / (bx1 - bx0) * mob.width,
                              (ty - by0) / (by1 - by0) * mob.height, 0.0])
    return P


def tex(t, color=WHITE, fs=44):
    """Plain coloured MathTex (isolating V_x drops trailing terms in 0.20.1)."""
    return MathTex(t, font_size=fs).set_color(color)


def ohm_chain(color, i_sub, src, R):
    s1 = tex(r"V = I\,R", color)
    s2 = tex(r"I = \dfrac{V}{R}", color)
    s3 = tex(rf"I = \dfrac{{V}}{{{R}\,\Omega}}", color)
    s4 = tex(rf"I_{{{i_sub}}} = \dfrac{{{src} - V_x}}{{{R}\,\Omega}}", color)
    for s in (s1, s2, s3, s4):
        s.move_to(DERIV)
    return s1, s2, s3, s4


def branch_arrows(P, specs):
    """One current arrow riding each resistor, tip toward the node end."""
    g = VGroup()
    for far, node, color, i_sub in specs:
        pf, pn = P(*far), P(*node)
        u = (pn - pf) / np.linalg.norm(pn - pf)
        perp = np.array([-u[1], u[0], 0.0])
        a = Arrow(pf + u * 0.9 + perp * 0.34, pf + np.linalg.norm(pn - pf) * u - u * 0.35 + perp * 0.34,
                  buff=0, color=color, stroke_width=6, tip_length=0.24,
                  max_tip_length_to_length_ratio=0.4)
        lbl = MathTex(rf"I_{{{i_sub}}}", color=color, font_size=38).move_to(
            (pf + pn) / 2 + perp * 0.85)
        g.add(VGroup(a, lbl))
    return g


class WhatIsANode(Scene):
    def construct(self):
        # ---------------- static circuit (freeze-frame) ----------------
        base = SVGMobject(str(CIRC / "base.svg")).set_color(WHITE).set_stroke(WHITE, width=2)
        base.set(width=10.4).move_to([0, 1.4, 0])
        P = make_P(base, BASE_BBOX)
        base.shift(RIGHT * (-P(8, 8)[0]))  # centre the Vx junction at x = 0

        self.add(base)
        self.wait(2)

        # ------------------------------ BEAT 1: nodes ------------------------------
        self.next_section("nodes")
        n5, nx, n2, ng = P(5, 8), P(8, 8), P(11, 8), P(8, 6)
        dot5 = Dot(n5, radius=0.1, color=BLUE).set_z_index(4)
        dot2 = Dot(n2, radius=0.1, color=ORANGE).set_z_index(4)
        dotx = Dot(nx, radius=0.1, color=YELLOW).set_z_index(4)
        dotg = Dot(ng, radius=0.1, color=TEAL).set_z_index(4)
        lbl_vx = MathTex("V_x", color=YELLOW, font_size=42).next_to(dotx, UP, buff=0.18)
        lbl_0v = MathTex(r"0\,\text{V}", color=TEAL, font_size=34).next_to(dotg, DOWN, buff=0.5).shift(RIGHT * 1.0)

        self.play(LaggedStart(FadeIn(dot5), FadeIn(dotx), FadeIn(dot2), FadeIn(dotg),
                              lag_ratio=0.3), run_time=1.4)
        self.play(Write(lbl_vx), Write(lbl_0v), run_time=1.0)
        self.wait(0.4)
        self.play(Indicate(dotx, color=YELLOW, scale_factor=1.8), run_time=1.2)
        self.wait(0.4)

        # --------------------------- BEATS 2-4: branches ---------------------------
        arrL = self._arrow(P(5.9, 8), P(7.4, 8), DOWN * 0.32, BLUE)
        arrM = self._arrow(P(8, 6.55), P(8, 7.45), LEFT * 0.4, TEAL)
        arrR = self._arrow(P(10.1, 8), P(8.6, 8), DOWN * 0.32, ORANGE)
        anchorL = P(6.0, 8) + DOWN * 0.62
        anchorM = arrM.get_center() + LEFT * 1.05
        anchorR = P(10.0, 8) + DOWN * 0.62

        lblI1 = self._branch("left_branch", arrL, anchorL, BLUE, "1", 5, 5, full=True)
        lblI2 = self._branch("middle_branch", arrM, anchorM, TEAL, "2", 0, 1, full=False)
        lblI3 = self._branch("right_branch", arrR, anchorR, ORANGE, "3", 2, 2, full=False)

        # ------------------------------ BEAT 5: KCL ------------------------------
        self.next_section("kcl")
        hdr = MathTex("I_1", "+", "I_2", "+", "I_3", "=", "0", font_size=46).move_to([0, -1.35, 0])
        hdr[0].set_color(BLUE)
        hdr[2].set_color(TEAL)
        hdr[4].set_color(ORANGE)
        self.play(Write(hdr), run_time=1.0)
        self.wait(0.4)

        sub = self._row([(r"\dfrac{5 - V_x}{5}", BLUE), (r"\dfrac{0 - V_x}{1}", TEAL),
                         (r"\dfrac{2 - V_x}{2}", ORANGE)]).move_to([0, -2.5, 0])
        self.play(Write(sub), run_time=1.6)
        self.wait(0.8)

        ans = MathTex(r"V_x = 1.18\ \text{V}", color=YELLOW, font_size=50).move_to([0, -3.6, 0])
        box = SurroundingRectangle(ans, color=YELLOW, buff=0.16)
        self.play(Write(ans), run_time=1.0)
        self.play(Create(box), Flash(ans, color=YELLOW, flash_radius=1.0))
        self.wait(1.2)

        # ------------------- BEAT 6: flip two arrows -> in = out -------------------
        self.next_section("in_equals_out")
        self.play(FadeOut(hdr), FadeOut(sub), FadeOut(ans), FadeOut(box))
        self.play(Rotate(arrM, PI, about_point=arrM.get_center()),
                  Rotate(arrR, PI, about_point=arrR.get_center()), run_time=1.1)
        n2lbl = tex(r"I_2 = \dfrac{V_x}{1\,\Omega}", TEAL).scale(0.5).move_to(anchorM)
        n3lbl = tex(r"I_3 = \dfrac{V_x - 2}{2\,\Omega}", ORANGE).scale(0.5).move_to(anchorR)
        self.play(ReplacementTransform(lblI2, n2lbl), ReplacementTransform(lblI3, n3lbl),
                  run_time=1.0)
        self.wait(0.4)

        io = VGroup(
            tex(r"\dfrac{5 - V_x}{5}", BLUE, 44),
            MathTex("=", font_size=44),
            tex(r"\dfrac{V_x}{1}", TEAL, 44),
            MathTex("+", font_size=44),
            tex(r"\dfrac{V_x - 2}{2}", ORANGE, 44),
        ).arrange(RIGHT, buff=0.28).move_to([0, -2.5, 0])
        self.play(Write(io), run_time=1.6)
        self.wait(0.5)
        ans2 = MathTex(r"V_x = 1.18\ \text{V}", color=YELLOW, font_size=50).move_to([0, -3.6, 0])
        box2 = SurroundingRectangle(ans2, color=YELLOW, buff=0.16)
        self.play(Write(ans2))
        self.play(Create(box2), Flash(ans2, color=YELLOW))
        self.wait(1.6)

        # ------------- BEAT 7: same node, however it's drawn (tracking arrows) -------------
        self.next_section("one_node")
        self.play(FadeOut(VGroup(dot5, dot2, dotg, dotx, lbl_vx, lbl_0v,
                                 arrL, arrM, arrR, lblI1, n2lbl, n3lbl, io, ans2, box2)))
        self.play(base.animate.set(height=5.6).move_to([0, 0.2, 0]), run_time=1.0)
        Pb = make_P(base, BASE_BBOX)
        ab = branch_arrows(Pb, BASE_SPECS)
        self.play(*[GrowArrow(p[0]) for p in ab], *[FadeIn(p[1]) for p in ab], run_time=1.2)
        self.wait(1.4)

        w1 = SVGMobject(str(CIRC / "wacky1.svg")).set_color(WHITE).set_stroke(WHITE, 2)
        w1.set(height=6.9).move_to([0, 0.1, 0])
        a1 = branch_arrows(make_P(w1, W1_BBOX), W1_SPECS)
        self.play(FadeTransform(base, w1), ReplacementTransform(ab, a1), run_time=1.8)
        self.wait(1.8)

        w2 = SVGMobject(str(CIRC / "wacky2.svg")).set_color(WHITE).set_stroke(WHITE, 2)
        w2.set(height=6.4).move_to([0, 0.2, 0])
        a2 = branch_arrows(make_P(w2, W2_BBOX), W2_SPECS)
        self.play(FadeTransform(w1, w2), ReplacementTransform(a1, a2), run_time=1.8)
        self.wait(2.2)

    # --------------------------------- helpers ---------------------------------
    def _arrow(self, tail, head, offset, color, tip_length=0.22):
        a = Arrow(np.array(tail) + offset, np.array(head) + offset, buff=0, color=color,
                  stroke_width=5, tip_length=tip_length, max_tip_length_to_length_ratio=0.14)
        a.set_z_index(3)
        return a

    def _branch(self, section, arrow, anchor, color, i_sub, src, R, full):
        self.next_section(section)
        self.play(GrowArrow(arrow))
        self.wait(0.3)
        s1, s2, s3, s4 = ohm_chain(color, i_sub, src, R)
        if full:
            self.play(Write(s1), run_time=0.9)
            self.wait(0.3)
            self.play(ReplacementTransform(s1, s2), run_time=1.0)
            self.wait(0.25)
            self.play(ReplacementTransform(s2, s3), run_time=1.0)
            self.wait(0.25)
            self.play(ReplacementTransform(s3, s4), run_time=1.1)
            self.wait(0.5)
        else:
            self.play(Write(s4), run_time=1.0)
            self.wait(0.4)
        s4.set_z_index(5)
        self.play(s4.animate.scale(0.5).move_to(anchor), run_time=0.9)
        self.wait(0.3)
        return s4

    def _row(self, fracs):
        parts = []
        for i, (t, c) in enumerate(fracs):
            if i:
                parts.append(MathTex("+", font_size=44))
            parts.append(tex(t, c, 44))
        parts.append(MathTex("=", "0", font_size=44))
        return VGroup(*parts).arrange(RIGHT, buff=0.22)


if __name__ == "__main__":
    config.media_dir = str(Path(__file__).resolve().parent.parent / "media")
    config.quality = "high_quality"  # low_quality | medium_quality | high_quality
    WhatIsANode().render()
