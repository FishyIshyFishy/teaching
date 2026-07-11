# Filter Sweep Demo — Gain & Phase Equations

For a lowpass filter of order *n*, the gain and phase come from the transfer function magnitude and argument.

## Normalized frequency

Let $x = \omega/\omega_0 = f/f_0$ where $f_0$ is the cutoff. Everything below is in terms of $x$ so it's dimensionless and easy to sweep.

## Passive filters (RC ladders, real poles)

An *n*-th order passive lowpass built from cascaded (buffered) identical RC stages, or the simplest real-pole model:

**Gain (linear, 0→1):**

$$f_n(x) = \frac{1}{\left(1 + x^2\right)^{n/2}} = \frac{1}{\left(\sqrt{1+x^2}\right)^{n}}$$

**Phase (radians):**

$$g_n(x) = -n \arctan(x)$$

So:

- $f_1 = \dfrac{1}{\sqrt{1+x^2}}, \quad g_1 = -\arctan x$
- $f_2 = \dfrac{1}{1+x^2}, \quad g_2 = -2\arctan x$
- $f_3 = \dfrac{1}{(1+x^2)^{3/2}}, \quad g_3 = -3\arctan x$

This is the "real poles all at $\omega_0$" case — gentle knee, no peaking, phase asymptotes to $-n\cdot 90°$. Physically what you get from RC stages.

## Sallen-Key (Butterworth, complex-conjugate poles)

Sallen-Key gives you a **2nd-order section** per op-amp. The right model is the Butterworth response — maximally flat, poles on a circle. For order *n*:

**Gain (linear):**

$$f_n(x) = \frac{1}{\sqrt{1 + x^{2n}}}$$

**Phase (radians):** sum over the Butterworth pole pairs — a product of second-order sections. For each section *k* (of $\lfloor n/2 \rfloor$ sections), the pole angle is

$$\theta_k = \frac{(2k-1)\pi}{2n}, \quad k = 1 \dots \lfloor n/2 \rfloor$$

with damping $\zeta_k = \cos\theta_k$, so the section coefficient is $2\zeta_k = 2\cos\theta_k$. Each 2nd-order section contributes

$$g_k(x) = -\arctan\!\left(\frac{2\zeta_k\, x}{1 - x^2}\right)$$

evaluated with the correct quadrant (add $-\pi$ when $x>1$ so phase is continuous). If *n* is odd there's one extra real pole contributing $-\arctan(x)$.

Total phase:

$$g_n(x) = \sum_k g_k(x) \;\;(+\,\text{real-pole term if } n \text{ odd})$$

The Butterworth section coefficients $a_k = 2\zeta_k$ (the coefficient of $x$ in the denominator $1 + a_k x + x^2$ of each section) for reference:

| n | section coefficients $a_k = 2\zeta_k$ |
|---|------------------------|
| 1 | (real pole: $1+x$) |
| 2 | $\sqrt{2} \approx 1.414$ |
| 3 | $1.000$ + real pole |
| 4 | $0.765,\ 1.848$ |
| 5 | $0.618,\ 1.618$ + real pole |

Check: $n=2$ gives $\theta_1 = 45°$, so $2\cos 45° = \sqrt{2}$ ✓.

## The key visual contrast

The whole point of the demo — plot both on the same axes:

- **Passive (real poles):** $f_n = (1+x^2)^{-n/2}$ droops *early*. At $x=1$ (cutoff), $f_1 = 0.707$ but $f_2 = 0.5$, $f_3 = 0.354$ — each order pulls the passband down sooner. Rounded, sagging knee.
- **Sallen-Key (Butterworth):** $f_n = (1+x^{2n})^{-1/2}$ stays *flat* then drops sharply. At $x=1$ every order gives exactly $0.707$ regardless of *n*; the rolloff steepens with *n* past cutoff. Sharp knee.

Both asymptote to the same $-n \cdot 20$ dB/decade slope far out, and both hit $-n\cdot 90°$ total phase — but the Butterworth holds its magnitude flat and pays for it with a more abrupt phase transition near $x=1$.

## For input/output plotting

With input $v_{in}(t) = A\cos(2\pi f t)$, the steady-state output at normalized frequency $x = f/f_0$ is:

$$v_{out}(t) = A\cdot f_n(x)\cdot \cos\!\big(2\pi f t + g_n(x)\big)$$

Same amplitude $A$ going in, scaled by $f_n(x)$ and shifted by $g_n(x)$ coming out. As you sweep $x$ from below cutoff to above, students watch the output shrink (gain rolloff) and lag (phase delay) — and the *difference in how fast* it shrinks between the passive and Sallen-Key curves is the lesson.
