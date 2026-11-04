#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=====================================================================
  HAPPY DIWALI 2026  -  Cinematic Diwali Animation  (pure Python)
  by  Coding with Vishesh   |   @codingwithvishesh
=====================================================================
  Fixed: Clear, Solid, Perfect Shape Text Engine
=====================================================================
"""
import argparse
import math
import random
import sys

import pygame

try:
    import numpy as np
except Exception:
    np = None

TAU = math.tau
rnd = random.random
ADD = pygame.BLEND_RGB_ADD
SUB = pygame.BLEND_RGB_SUB
MULT = pygame.BLEND_RGB_MULT


def clamp(x, a=0.0, b=1.0):
    return a if x < a else (b if x > b else x)


def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def lerp(a, b, t):
    return a + (b - a) * t


def mix(c1, c2, t):
    return (int(c1[0] + (c2[0] - c1[0]) * t),
            int(c1[1] + (c2[1] - c1[1]) * t),
            int(c1[2] + (c2[2] - c1[2]) * t))


def scol(c, k):
    return (min(255, max(0, int(c[0] * k))),
            min(255, max(0, int(c[1] * k))),
            min(255, max(0, int(c[2] * k))))


GOLD = (255, 195, 60)
WARM = (255, 238, 200)
RED = (255, 55, 45)
ORANGE = (255, 115, 25)
MAGENTA = (255, 60, 170)
GREEN = (80, 255, 140)
BLUE = (70, 140, 255)
VIOLET = (175, 90, 255)
SILVER = (220, 235, 255)
EMBER = (255, 70, 15)

SHELL_COLORS = [[GOLD], [RED, ORANGE], [MAGENTA, VIOLET], [GREEN, WARM],
                [BLUE, SILVER], [ORANGE, GOLD], [RED, GOLD], [SILVER, BLUE]]

_glow_cache = {}


def glow_sprite(rx, ry, color, level):
    key = (rx, ry, color, level)
    s = _glow_cache.get(key)
    if s is not None:
        return s
    k = (level + 1) / 16.0
    surf = pygame.Surface((rx * 2 + 1, ry * 2 + 1))
    surf.fill((0, 0, 0))
    steps = max(6, min(max(rx, ry), 64))
    for i in range(steps):
        f = 1.0 - i / steps
        inten = ((i + 1) / steps) ** 2.4 * k
        c = (int(color[0] * inten), int(color[1] * inten), int(color[2] * inten))
        w = max(1, int(2 * rx * f) + 1)
        h = max(1, int(2 * ry * f) + 1)
        pygame.draw.ellipse(surf, c, (rx - w // 2, ry - h // 2, w, h))
    _glow_cache[key] = surf
    return surf


def add_glow(dst, x, y, rx, ry, color, b):
    level = int(clamp(b) * 15)
    if level <= 0 or rx < 1 or ry < 1:
        return
    s = glow_sprite(int(rx), int(ry), color, level)
    dst.blit(s, (int(x - rx), int(y - ry)), special_flags=ADD)


def make_sounds(sr=44100):
    rng = np.random.default_rng(2026)

    def lp(x, k):
        return np.convolve(x, np.ones(k) / k, mode='same')

    def fin(x, gain=0.9):
        x = x / (np.max(np.abs(x)) + 1e-9) * gain
        st = np.stack([x, x], axis=1) * 32767
        return pygame.sndarray.make_sound(np.ascontiguousarray(st.astype(np.int16)))

    out = {}
    booms = []
    for v in range(3):
        n = int(sr * (2.3 + 0.4 * v))
        t = np.arange(n) / sr
        noise = rng.normal(size=n)
        rumble = lp(noise, 60 + 40 * v) * np.exp(-t * (2.0 + v * 0.4)) * 6
        f = 62 - 8 * v
        thump = np.sin(2 * np.pi * np.cumsum(f * np.exp(-t * 2.5) + 28) / sr) * np.exp(-t * 3.2)
        crack = lp(noise, 3) * np.exp(-t * 35) * 1.4
        booms.append(fin(rumble + thump * 1.3 + crack, 0.95))
    out['boom'] = booms

    n = int(sr * 1.4)
    t = np.arange(n) / sr
    noise = rng.normal(size=n)
    env = np.minimum(1, t / 0.05) * np.exp(-t * 2.0)
    hp = noise - lp(noise, 12)
    whistle = np.sin(2 * np.pi * np.cumsum(900 + 1700 * (t / 1.4)) / sr) * 0.08 * env
    out['launch'] = [fin(hp * env * 0.6 + whistle, 0.55)]

    cr = []
    for v in range(2):
        n = int(sr * 0.9)
        x = np.zeros(n)
        for p in np.sort((rng.random(70) ** 1.8 * (n - 300)).astype(int)):
            L = int(rng.integers(40, 170))
            x[p:p + L] += rng.normal(size=L) * np.exp(-np.arange(L) / (L / 4)) * rng.uniform(0.3, 1)
        cr.append(fin(x, 0.5))
    out['crackle'] = cr

    n = int(sr * 0.5)
    t = np.arange(n) / sr
    noise = rng.normal(size=n)
    out['pop'] = [fin(lp(noise, 5) * np.exp(-t * 18), 0.5)]
    return out


class Audio:
    def __init__(self, enabled):
        self.ok = False
        self.muted = False
        self.snd = {}
        if not enabled or np is None:
            return
        try:
            pygame.mixer.init(44100, -16, 2, 512)
            pygame.mixer.set_num_channels(40)
            self.snd = make_sounds()
            self.ok = True
        except Exception as e:
            print("[audio off]", e)

    def play(self, name, pan=0.5, vol=1.0):
        if not self.ok or self.muted:
            return
        s = random.choice(self.snd[name])
        ch = s.play()
        if ch:
            ch.set_volume(vol * min(1.0, 2 * (1 - pan)), vol * min(1.0, 2 * pan))


class Spark:
    __slots__ = ('x', 'y', 'px', 'py', 'vx', 'vy', 'age', 'life', 'col', 'end',
                 'drag', 'grav', 'r', 'twk', 'kids', 'tx', 'ty', 'tconv', 'hold',
                 'crk', 'trail', 'b', 'ph', 'fall')

    def __init__(s, x, y, vx, vy, life, col, drag=0.97, grav=60.0, r=1,
                 end=True, twk=False, kids=0.0, trail=True, crk=0):
        s.x = s.px = x
        s.y = s.py = y
        s.vx, s.vy = vx, vy
        s.age = 0.0
        s.life = life
        s.col = col
        s.drag, s.grav, s.r = drag, grav, r
        s.end, s.twk, s.kids, s.trail, s.crk = end, twk, kids, trail, crk
        s.tx = s.ty = None
        s.tconv = 0.0
        s.hold = 1e9
        s.b = 1.0
        s.ph = rnd() * TAU
        s.fall = False

    def step(s, dt, w):
        s.px, s.py = s.x, s.y
        s.age += dt
        if s.tx is not None:
            if s.age < s.tconv:
                f = s.drag ** (dt * 60)
                s.vx *= f
                s.vy *= f
            else:
                # Strong exact snapping to target shape
                s.vx += ((s.tx - s.x) * 90.0 - s.vx * 18.0) * dt
                s.vy += ((s.ty - s.y) * 90.0 - s.vy * 18.0) * dt
            if w.t >= s.hold:
                s.tx = None
                s.fall = True
                s.age = 0.0
                s.life = lerp(2.4, 4.2, rnd())
                s.drag = 0.984
                s.grav = 62.0 * w.S
                s.vx += (rnd() - 0.5) * 14 * w.S
                s.vy += rnd() * 10 * w.S
        else:
            f = s.drag ** (dt * 60)
            s.vx *= f
            s.vy *= f
            s.vy += s.grav * dt
        s.x += s.vx * dt
        s.y += s.vy * dt
        if s.kids and rnd() < s.kids:
            w.child(s)
        if s.tx is not None:
            s.b = min(1.0, s.age * 6.0)
            return True
        t = s.age / s.life
        if t >= 1.0 or s.y > w.hy + 30 * w.S:
            if s.crk:
                w.crackle_at(s.x, s.y, s.crk)
            return False
        b = (1.0 - t) ** (0.8 if s.fall else 0.7)
        if s.twk and t > 0.35:
            b *= 0.35 + 0.65 * rnd()
        if s.fall:
            b *= 0.55 + 0.45 * rnd()
        s.b = b
        return True


class Rocket:
    def __init__(self, w, x0, y0, tx, ty, kind, pal, sz=1.0, dur=1.3, data=None):
        self.x = self.px = x0
        self.y = self.py = y0
        self.x0, self.y0, self.tx, self.ty = x0, y0, tx, ty
        self.kind, self.pal, self.sz, self.dur, self.data = kind, pal, sz, dur, data
        self.u = 0.0
        self.ph = rnd() * TAU
        self.n = 0
        w.sfx('launch', x0, 0.0, 0.5)

    def step(self, dt, w):
        S = w.S
        self.u += dt / self.dur
        u = min(self.u, 1.0)
        e = 1 - (1 - u) ** 2.2
        self.px, self.py = self.x, self.y
        self.x = self.x0 + (self.tx - self.x0) * e + math.sin(u * 14 + self.ph) * 2.5 * S * (1 - u)
        self.y = self.y0 + (self.ty - self.y0) * e
        dx, dy = self.x - self.px, self.y - self.py
        for _ in range(3):
            w.add(Spark(self.x, self.y, -dx * 6 + (rnd() - 0.5) * 50 * S,
                        -dy * 6 + (rnd() - 0.5) * 50 * S, lerp(0.3, 0.7, rnd()),
                        (255, 170, 70), 0.9, 40 * S, 1, True, False, 0.0, False), force=False)
        self.n += 1
        if self.n % 4 == 0:
            w.add_smoke(self.x, self.y, 0.35)
        if self.u >= 1.0:
            w.explode(self.x, self.y, self.kind, self.pal, self.sz, self.data)
            return False
        return True


class Anar:
    def __init__(self, x, y, S):
        self.x, self.y, self.S = x, y, S
        self.heat = 0.0

    def step(self, dt, w, active):
        self.heat = min(1.0, self.heat + dt * 1.6) if active else max(0.0, self.heat - dt * 1.2)
        if self.heat <= 0.01:
            return
        S = self.S
        n = int(4 * self.heat) + (1 if rnd() < 0.5 else 0)
        for _ in range(n):
            a = -math.pi / 2 + random.gauss(0, 0.26)
            sp = lerp(280, 540, rnd()) * S * (0.55 + 0.45 * self.heat)
            w.add(Spark(self.x, self.y, math.cos(a) * sp, math.sin(a) * sp,
                        lerp(0.9, 1.7, rnd()), random.choice([GOLD, WARM, ORANGE, SILVER, GOLD]),
                        0.99, 520 * S, 1, True, False, 0.0, True), force=False)
        if rnd() < 0.05 * self.heat:
            w.sfx('crackle', self.x, 0.0, 0.18)


_body_cache = {}


def make_diya_body(w, flip):
    key = (w, flip)
    if key in _body_cache:
        return _body_cache[key]
    h = int(w * 0.62)
    bw = int(w * 1.25)
    surf = pygame.Surface((bw, h + 4), pygame.SRCALPHA)
    for k in range(10):
        f = k / 9.0
        col = mix((62, 24, 13), (158, 76, 38), f)
        shrink = f * 0.34
        rw, rh = w * (1 - shrink), h * 0.74 * (1 - shrink * 0.7)
        pygame.draw.ellipse(surf, col, (w * 0.5 - rw / 2 - w * 0.03 * f, h * 0.28 + (h * 0.74 - rh) * 0.25,
                                        rw, rh))
    pygame.draw.ellipse(surf, (132, 62, 30), (0, 0, w, h * 0.52))
    pygame.draw.ellipse(surf, (22, 11, 6), (w * 0.09, h * 0.07, w * 0.82, h * 0.38))
    pygame.draw.ellipse(surf, (88, 58, 28), (w * 0.28, h * 0.12, w * 0.3, h * 0.1))
    pygame.draw.polygon(surf, (126, 58, 28), [(w * 0.86, h * 0.14), (w * 1.20, h * 0.02), (w * 1.05, h * 0.34)])
    pygame.draw.circle(surf, (24, 16, 12), (int(w * 1.16), int(h * 0.05)), max(1, int(w * 0.035)))
    if flip:
        surf = pygame.transform.flip(surf, True, False)
    _body_cache[key] = surf
    return surf


class Diya:
    def __init__(self, x, y, sc, t_on, S, flip):
        self.x, self.y, self.sc, self.t_on = x, y, sc, t_on
        self.w = max(10, int(44 * S * sc))
        self.h = int(self.w * 0.62)
        self.flip = flip
        self.body = make_diya_body(self.w, flip)
        self.bx = int(x - self.body.get_width() / 2)
        self.by = int(y - self.h)
        bw = self.body.get_width()
        off = self.w * 1.16
        self.wx = self.bx + (bw - off if flip else off)
        self.wy = self.by + self.h * 0.06
        self.seed = rnd() * 100
        self.a = 0.0

    def update(self, t):
        u = (t - self.t_on) / 3.2
        self.a = smooth(u) if u > 0 else 0.0

    def flick(self, t):
        return 0.86 + 0.14 * math.sin(t * 17 + self.seed) * math.sin(t * 5.3 + self.seed * 2) + 0.05 * (rnd() - 0.5)


def teardrop(x, y, h, w, sway, n=14):
    pts_l, pts_r = [], []
    for i in range(n + 1):
        u = i / n
        hw = w * math.sin(math.pi * u ** 1.5)
        yy = y - h + u * h
        xx = x + sway * (1 - u) ** 2
        pts_l.append((xx - hw, yy))
        pts_r.append((xx + hw, yy))
    return pts_l + pts_r[::-1]


FLAME_LAYERS = [((200, 55, 8), 1.0), ((255, 95, 14), 0.88), ((255, 150, 35), 0.74),
                ((255, 205, 90), 0.58), ((255, 238, 170), 0.42), ((255, 252, 235), 0.26)]


def draw_flame(layer, d, t, S):
    a = d.a
    if a <= 0.001:
        return
    fl = d.flick(t)
    h = d.w * 1.05 * (a ** 0.7) * fl
    wd = d.w * 0.2 * (0.55 + 0.45 * a)
    sway = (math.sin(t * 7.3 + d.seed) + 0.6 * math.sin(t * 12.1 + d.seed * 2)) * 0.13 * d.w * a
    x, y = d.wx, d.wy
    pygame.draw.ellipse(layer, scol((50, 80, 255), 0.55 * a), (x - wd * 0.7, y - h * 0.22, wd * 1.4, h * 0.26))
    for col, f in FLAME_LAYERS:
        pygame.draw.polygon(layer, scol(col, min(1.0, a * 1.05)), teardrop(x, y, h * f, wd * f, sway * f))
    add_glow(layer, x + sway * 0.4, y - h * 0.4, int(d.w * 0.95), int(d.w * 1.15), (255, 140, 45), 0.62 * a * fl)


class Rangoli:
    def __init__(self, cx, cy, rx, squash, t0):
        self.cx, self.cy, self.R, self.sq = cx, cy, int(rx), squash
        R = self.R
        self.flat = pygame.Surface((2 * R, 2 * R), pygame.SRCALPHA)
        self.elems = []
        self.drawn = 0
        self.dirty = False
        self.img = None
        self.last = None
        self.last_t = -9.0
        self.noise = None
        self._build(t0)

    def P(self, ang, r):
        return (self.R + math.cos(ang) * r, self.R + math.sin(ang) * r)

    def petal(self, ang, r0, length, width):
        n = 14
        side = []
        for i in range(n + 1):
            u = i / n
            side.append((r0 + u * length, math.sin(math.pi * u ** 0.8) * width * 0.5))
        pts = side + [(a, -b) for a, b in side[::-1]]
        ca, sa = math.cos(ang), math.sin(ang)
        return [(self.R + a * ca - b * sa, self.R + a * sa + b * ca) for a, b in pts]

    def _build(self, t0):
        R = self.R
        P = self.P
        layers = []
        L = []
        for i in range(96):
            L.append(('c', P(i / 96 * TAU, 0.955 * R), max(1.6, 0.013 * R * (1 if i % 2 else 0.7)), (240, 240, 232)))
        layers.append(L)
        L = []
        for i in range(36):
            a = i / 36 * TAU
            col = [(255, 150, 20), (232, 38, 118), (255, 205, 40)][i % 3]
            L.append(('c', P(a, 0.885 * R), 0.052 * R, col))
            L.append(('c', P(a, 0.885 * R), 0.02 * R, (250, 245, 235)))
        layers.append(L)
        L = []
        for i in range(24):
            a = i / 24 * TAU
            da = TAU / 24 * 0.44
            col = (225, 28, 98) if i % 2 else (255, 140, 20)
            pts = [P(a - da, 0.70 * R), P(a + da, 0.70 * R), P(a, 0.835 * R)]
            L.append(('p', pts, col, (245, 240, 230)))
            L.append(('c', P(a, 0.78 * R), 0.014 * R, (250, 250, 240)))
        layers.append(L)
        L = []
        for i in range(16):
            a = i / 16 * TAU
            col = (190, 18, 92) if i % 2 else (255, 118, 18)
            L.append(('p', self.petal(a, 0.30 * R, 0.40 * R, 0.27 * R), col, (246, 240, 230)))
        for i in range(16):
            a = i / 16 * TAU
            col = (255, 214, 60) if i % 2 else (248, 240, 228)
            L.append(('p', self.petal(a, 0.35 * R, 0.25 * R, 0.13 * R), col, None))
        layers.append(L)
        L = []
        star = []
        for i in range(32):
            r = 0.30 * R if i % 2 == 0 else 0.20 * R
            star.append(P(i / 32 * TAU, r))
        L.append(('p', star, (14, 140, 135), (250, 245, 235)))
        L.append(('c', (R, R), 0.19 * R, (196, 24, 44)))
        L.append(('c', (R, R), 0.15 * R, (255, 205, 50)))
        L.append(('c', (R, R), 0.125 * R, (28, 84, 158)))
        for i in range(8):
            L.append(('p', self.petal(i / 8 * TAU, 0.02 * R, 0.10 * R, 0.06 * R), (255, 125, 25), None))
        L.append(('c', (R, R), 0.04 * R, (255, 215, 80)))
        L.append(('c', (R, R), 0.016 * R, (255, 255, 250)))
        layers.append(L)
        starts = [0.0, 1.2, 2.4, 3.8, 5.8, 7.4]
        durs = [1.3, 1.7, 1.5, 2.3, 1.4, 1.3]
        for li, L in enumerate(layers):
            n = len(L)
            for j, e in enumerate(L):
                self.elems.append((t0 + starts[li] + j / n * durs[li], e))
        self.elems.sort(key=lambda z: z[0])
        self.end_t = t0 + starts[-1] + durs[-1]
        self.noise = None

    def update(self, t):
        R = self.R
        while self.drawn < len(self.elems) and self.elems[self.drawn][0] <= t:
            e = self.elems[self.drawn][1]
            if e[0] == 'c':
                pygame.draw.circle(self.flat, e[3], (int(e[1][0]), int(e[1][1])), max(1, int(e[2])))
                self.last = e[1]
            else:
                pygame.draw.polygon(self.flat, e[2], e[1])
                if e[3]:
                    pygame.draw.polygon(self.flat, e[3], e[1], max(1, int(R * 0.007)))
                self.last = e[1][len(e[1]) // 2]
            self.last_t = t
            self.drawn += 1
            self.dirty = True
        if self.dirty:
            h = int(2 * R * self.sq)
            img = pygame.transform.smoothscale(self.flat, (2 * R, h))
            if self.noise is None or self.noise.get_size() != (2 * R, h):
                rng = random.Random(5)
                nz = pygame.Surface((2 * R, h))
                nz.fill((236, 236, 236))
                for _ in range(2 * R * h // 6):
                    v = rng.randint(185, 255)
                    nz.set_at((rng.randrange(2 * R), rng.randrange(h)), (v, v, v))
                self.noise = nz
            img.blit(self.noise, (0, 0), special_flags=MULT)
            img.fill((92, 88, 98, 255), special_flags=pygame.BLEND_RGBA_MULT)
            self.img = img
            self.dirty = False

    def draw(self, screen):
        if self.img is not None:
            screen.blit(self.img, (self.cx - self.R, self.cy - self.img.get_height() // 2))

    def screen_pos(self, p):
        return (self.cx + p[0] - self.R, self.cy + (p[1] - self.R) * self.sq)


def build_city(W, H, hy, S):
    band = int(0.30 * H)
    oy = hy - band
    far = pygame.Surface((W, band + 8), pygame.SRCALPHA)
    near = pygame.Surface((W, band + 8), pygame.SRCALPHA)
    mask = pygame.Surface((W, band + 8), pygame.SRCALPHA)
    rng = random.Random(11)
    x = -10
    while x < W + 10:
        w = rng.randint(int(30 * S), int(80 * S))
        h = rng.randint(int(28 * S), int(0.115 * H))
        pygame.draw.rect(far, (20, 20, 40, 255), (x, band - h, w, h + 8))
        x += w + rng.randint(0, int(5 * S))
    ops = []
    lights = []
    temples = [(0.17, 0.205, 0.066), (0.84, 0.115, 0.04)]
    x = 0
    while x < W:
        w = rng.randint(int(26 * S), int(62 * S))
        h = rng.randint(int(0.03 * H), int(0.095 * H))
        cxr = (x + w / 2) / W
        if any(abs(cxr - t[0]) < t[2] * 1.5 for t in temples):
            h = int(0.025 * H)
        ops.append(('r', (x, band - h, w, h + 8)))
        for lx in range(x + 3, x + w - 2, max(6, int(11 * S))):
            lights.append((lx, oy + band - h, rng.choice([(255, 170, 60), (255, 200, 90), (255, 90, 40), (255, 215, 130)]),
                           rng.random() * TAU, rng.uniform(1.5, 4.5), 1, rng.random()))
        for _ in range(rng.randint(0, 5)):
            lights.append((x + rng.randint(3, max(4, w - 4)), oy + band - rng.randint(4, max(5, h - 4)),
                           (255, 205, 120), rng.random() * TAU, rng.uniform(0.5, 1.2), 1, rng.random()))
        x += w + rng.randint(0, int(4 * S))
    for xc, ht, hw0 in temples:
        cx = int(xc * W)
        Ht = ht * H
        hw0 = hw0 * W
        right, left = [], []
        N = 46
        for i in range(N + 1):
            tt = i / N
            hw = max(1.0, hw0 * (1 - tt ** 1.25) * (1 + 0.07 * math.sin(tt * 34)))
            y = band - tt * Ht
            right.append((cx + hw, y))
            left.append((cx - hw, y))
        poly = right + left[::-1]
        ops.append(('p', poly))
        ops.append(('r', (cx - hw0 * 1.4, band - 0.02 * H, hw0 * 2.8, 0.02 * H + 8)))
        ops.append(('c', (cx, band - Ht - 4 * S), 5 * S))
        ops.append(('r', (cx - S, band - Ht - 14 * S, 2 * S, 10 * S)))
        for side in (right, left):
            for a, b in zip(side[:-1], side[1:]):
                dist = math.hypot(b[0] - a[0], b[1] - a[1])
                k = max(1, int(dist / (9 * S)))
                for j in range(k):
                    f = j / k
                    lights.append((a[0] + (b[0] - a[0]) * f, oy + a[1] + (b[1] - a[1]) * f,
                                   rng.choice([(255, 165, 55), (255, 120, 40), (255, 200, 90)]),
                                   rng.random() * TAU, rng.uniform(2, 5), 1, rng.random()))
    for surf, col in ((near, (7, 6, 12, 255)), (mask, (255, 255, 255, 255))):
        for op in ops:
            if op[0] == 'r':
                pygame.draw.rect(surf, col, op[1])
            elif op[0] == 'p':
                pygame.draw.polygon(surf, col, op[1])
            else:
                pygame.draw.circle(surf, col, (int(op[1][0]), int(op[1][1])), max(1, int(op[2])))
    return far, near, mask, oy, lights


TEXT0 = 18.0
PERIOD = 54.0
MAXP = 5200


class Show:
    def __init__(self, W, H, audio, tag):
        self.W, self.H = W, H
        self.S = S = min(W / 720.0, H / 1280.0)
        self.hy = hy = int(H * 0.77)
        self.audio = audio
        self.tag = tag
        self.t = 0.0
        self.sparks, self.rockets, self.flashes, self.smoke = [], [], [], []
        self.timed, self.audio_q = [], []
        self.flash = [0.0, 0.0, 0.0]
        self.next_launch = 2.0
        self.next_text = TEXT0
        self.text_until = -1.0
        self.finale_from = self.finale_until = -1.0
        self.sub_from = self.sub_until = -1.0
        self.glow = pygame.Surface((W, H)).convert()
        self.flm = pygame.Surface((W, H)).convert()
        self.glow.fill((0, 0, 0))
        self._build_sky()
        self.far, self.near, self.near_mask, self.city_oy, self.city_lights = build_city(W, H, hy, S)
        self._build_ground()
        self._build_vignette()
        self._build_smoke()
        self._build_text()
        self._build_fonts()
        cx, cy = W // 2, int(H * 0.875)
        self.rangoli = Rangoli(cx, cy, 0.40 * W, 0.30, 3.2)
        self._build_diyas(cx, cy)
        self.anars = [Anar(0.13 * W, H * 0.905, S), Anar(0.87 * W, H * 0.905, S)]

    def _build_sky(self):
        W, hy = self.W, self.hy
        sky = pygame.Surface((W, hy + 2)).convert()
        stops = [(0.0, (2, 3, 10)), (0.55, (8, 10, 30)), (0.86, (26, 18, 46)), (1.0, (74, 40, 44))]
        for y in range(hy + 2):
            u = y / hy
            for (u0, c0), (u1, c1) in zip(stops[:-1], stops[1:]):
                if u0 <= u <= u1:
                    sky.fill(mix(c0, c1, (u - u0) / (u1 - u0)), (0, y, W, 1))
                    break
            else:
                sky.fill(stops[-1][1], (0, y, W, 1))
        rng = random.Random(3)
        for _ in range(260):
            x, y = rng.randrange(W), rng.randrange(int(hy * 0.85))
            v = rng.randint(55, 160)
            sky.set_at((x, y), (v, v, min(255, v + 20)))
        self.sky = sky
        self.dstars = [(rng.randrange(W), rng.randrange(int(hy * 0.8)), rng.random() * TAU,
                        rng.uniform(1, 4), rng.randint(110, 230)) for _ in range(90)]

    def _build_ground(self):
        W, H, hy = self.W, self.H, self.hy
        g = pygame.Surface((W, H - hy)).convert()
        gh = H - hy
        for y in range(gh):
            g.fill(mix((18, 13, 13), (9, 7, 8), y / gh), (0, y, W, 1))
        rng = random.Random(8)
        for _ in range(W * gh // 70):
            v = rng.randint(22, 52)
            g.set_at((rng.randrange(W), rng.randrange(gh)), (v, int(v * 0.85), int(v * 0.8)))
        vx, vy = W / 2, -0.35 * H
        line = (30, 23, 23)
        for i in range(-14, 15):
            xb = W / 2 + i * W * 0.17
            pygame.draw.line(g, line, (vx + (xb - vx) * (0 - vy + hy) / (hy + gh - vy + hy) * 0, 0), (xb, gh), 1)
        yy = 0.0
        step = 6.0 * self.S
        while yy < gh:
            pygame.draw.line(g, line, (0, int(yy)), (W, int(yy)), 1)
            step *= 1.33
            yy += step
        self.ground = g

    def _build_vignette(self):
        W, H = self.W, self.H
        v = pygame.Surface((W, H)).convert()
        v.fill((120, 116, 128))
        steps = 36
        for i in range(steps):
            f = 1.55 - i / steps * 1.25
            c = int(120 + 135 * smooth(i / (steps - 1)))
            col = (c, min(255, c - 2 + 2), min(255, c + 4))
            rw, rh = W * f, H * f * 0.95
            pygame.draw.ellipse(v, col, (W / 2 - rw / 2, H / 2 - rh / 2, rw, rh))
        self.vig = v

    def _build_smoke(self):
        self.smoke_sprites = []
        for sz in (40, 60, 80, 110, 150, 200):
            sz = max(8, int(sz * self.S))
            surf = pygame.Surface((sz, sz), pygame.SRCALPHA)
            steps = 18
            for i in range(steps):
                r = sz / 2 * (1 - i / steps)
                al = int(255 * ((i + 1) / steps) ** 2 * 0.5)
                pygame.draw.circle(surf, (72, 68, 84, al), (sz // 2, sz // 2), max(1, int(r)))
            self.smoke_sprites.append(surf)

    def _build_fonts(self):
        S = self.S
        names = "georgia,garamond,timesnewroman,dejavuserif,serif"
        self.f_sub = pygame.font.SysFont(names, max(14, int(46 * S)), italic=True)
        self.f_sub2 = pygame.font.SysFont(names, max(10, int(26 * S)), italic=True)
        self.f_tag = pygame.font.SysFont("arial,dejavusans,helvetica", max(10, int(20 * S)), bold=True)
        self.sub1 = self.f_sub.render("~  Shubh Deepawali  ~", True, (255, 214, 130))
        self.sub2 = self.f_sub2.render("Light  .  Love  .  Prosperity", True, (255, 190, 110))
        self.tagimg = self.f_tag.render(self.tag, True, (255, 200, 120)) if self.tag else None

    def _build_text(self):
        W, H, S = self.W, self.H, self.S
        spec = [("HAPPY", 0.78, 0.200), ("DIWALI", 0.84, 0.335), ("ALL OF YOU", 0.72, 0.455)]
        names = "arial,impact,arialblack,helvetica,dejavusans"
        self.text_pts = []
        self.text_cy = []
        
        # Exact pixel sampling for ultra-sharp letters
        e = max(2, int(round(3 * S)))
        
        for text, wf, cyf in spec:
            size = 100
            font = pygame.font.SysFont(names, size, bold=True)
            scale = (wf * W) / max(1, font.size(text)[0])
            size = max(20, int(size * scale))
            font = pygame.font.SysFont(names, size, bold=True)
            
            surf = font.render(text, True, (255, 255, 255))
            m = pygame.mask.from_surface(surf, 120)
            w, h = m.get_size()
            ox, oy = W / 2 - w / 2, cyf * H - h / 2

            pts = []
            for y in range(0, h, e):
                for x in range(0, w, e):
                    if m.get_at((x, y)):
                        pts.append((ox + x, oy + y, True))
            self.text_pts.append(pts)
            self.text_cy.append(cyf * H)

    def _build_diyas(self, cx, cy):
        W, H, S, hy = self.W, self.H, self.S, self.hy
        rx, ry = 0.40 * W * 1.14, 0.40 * W * 0.30 * 1.22
        n = 18
        items = []
        for i in range(n):
            a = i / n * TAU + 0.1
            x, y = cx + math.cos(a) * rx, cy + math.sin(a) * ry + 12 * S
            sc = lerp(0.72, 1.18, clamp((y - hy) / (H - hy)))
            items.append((abs(math.sin(a - math.pi / 2)) * 0 + abs(((a - math.pi / 2 + math.pi) % TAU) - math.pi), x, y, sc))
        items.sort(key=lambda z: z[0])
        self.diyas = []
        for rank, (_, x, y, sc) in enumerate(items):
            self.diyas.append(Diya(x, y, sc, 1.3 + rank * 0.42, S, rnd() < 0.5))
        self.diyas_draw = sorted(self.diyas, key=lambda d: d.y)

    def add(self, s, force=True):
        if force or len(self.sparks) < MAXP:
            self.sparks.append(s)

    def at(self, t, fn, *a):
        self.timed.append((t, fn, a))

    def sfx(self, name, x, delay, vol):
        self.audio_q.append((self.t + delay, name, clamp(x / self.W), vol))

    def add_flash(self, col, k):
        for i in range(3):
            self.flash[i] = min(1.0, self.flash[i] + col[i] / 255.0 * k)

    def add_smoke(self, x, y, k):
        if len(self.smoke) < 90:
            S = self.S
            self.smoke.append([x, y, (rnd() - 0.5) * 8 * S, -rnd() * 5 * S, 0.0, lerp(3.0, 5.5, rnd()),
                               int(rnd() * 3 + (2 if k > 0.5 else 0)), lerp(10, 20, rnd()) * (0.6 + k)])

    def child(self, p):
        S = self.S
        self.add(Spark(p.x, p.y, p.vx * 0.05 + random.gauss(0, 9) * S, p.vy * 0.05 + random.gauss(0, 9) * S,
                       lerp(0.5, 1.0, rnd()), p.col, 0.95, 45 * S, 1, True, False, 0.0, False), force=False)

    def crackle_at(self, x, y, n):
        S = self.S
        for _ in range(n):
            a = rnd() * TAU
            sp = lerp(40, 130, rnd()) * S
            self.add(Spark(x, y, math.cos(a) * sp, math.sin(a) * sp, lerp(0.2, 0.42, rnd()), (255, 255, 235),
                           0.9, 0, 1, False, False, 0.0, True), force=False)
        if rnd() < 0.015:
            self.sfx('pop', x, 0.0, 0.25)

    def explode(self, x, y, kind, pal, sz=1.0, data=None):
        S = self.S
        q = 1.0 if len(self.sparks) < 3200 else 0.6
        self.add_flash(pal[0], (0.6 if kind == 'text' else 0.30 * sz))
        self.flashes.append([x, y, 0.0, sz, pal[0] if kind != 'text' else (255, 230, 150)])
        self.sfx('boom', x, lerp(0.30, 0.65, rnd()) if kind != 'text' else 0.35, 0.55 * min(1.2, sz) + (0.2 if kind == 'text' else 0))
        for _ in range(3 if kind != 'text' else 6):
            self.add_smoke(x + random.gauss(0, 20 * S), y + random.gauss(0, 20 * S), 1.0)

        def sphere():
            a = rnd() * TAU
            z = rnd() * 2 - 1
            r = math.sqrt(1 - z * z)
            return math.cos(a) * r, math.sin(a) * r

        ch = random.choice
        if kind in ('peony', 'double'):
            n = int(125 * sz * q)
            base = lerp(235, 285, rnd()) * S * sz
            for _ in range(n):
                dx, dy = sphere()
                sp = base * (0.88 + 0.12 * rnd())
                self.add(Spark(x, y, dx * sp, dy * sp, lerp(1.6, 2.3, rnd()), ch(pal), 0.965, 60 * S, 1, True, False, 0.0, True))
            if kind == 'double':
                for _ in range(int(70 * sz * q)):
                    dx, dy = sphere()
                    sp = base * 0.52 * (0.9 + 0.1 * rnd())
                    self.add(Spark(x, y, dx * sp, dy * sp, lerp(1.3, 1.9, rnd()), pal[-1], 0.962, 55 * S, 1, True, False, 0.0, True))
        elif kind == 'chrys':
            for _ in range(int(175 * sz * q)):
                dx, dy = sphere()
                sp = lerp(0.5, 1.0, rnd()) * 255 * S * sz
                self.add(Spark(x, y, dx * sp, dy * sp, lerp(2.3, 3.1, rnd()), ch(pal), 0.968, 55 * S, 1, True, True, 0.10, True))
        elif kind == 'willow':
            for _ in range(int(110 * sz * q)):
                dx, dy = sphere()
                sp = lerp(120, 230, rnd()) * S * sz
                self.add(Spark(x, y, dx * sp, dy * sp, lerp(3.4, 4.4, rnd()), ch([GOLD, GOLD, WARM]), 0.962, 100 * S, 1, True, False, 0.45, True))
        elif kind == 'palm':
            n = 12
            for i in range(n):
                a = i / n * TAU + rnd() * 0.25
                sp = lerp(280, 340, rnd()) * S * sz
                self.add(Spark(x, y, math.cos(a) * sp, math.sin(a) * sp, lerp(2.3, 2.8, rnd()), ch([GOLD, WARM]),
                               0.975, 40 * S, 2, True, False, 0.9, True))
        elif kind == 'ring':
            tilt = lerp(0.25, 1.0, rnd())
            rot = rnd() * TAU
            cr, sr = math.cos(rot), math.sin(rot)
            for i in range(int(96 * q)):
                a = i / 96 * TAU
                sp = lerp(230, 262, rnd()) * S * sz
                vx, vy = math.cos(a) * sp, math.sin(a) * sp * tilt
                self.add(Spark(x, y, vx * cr - vy * sr, vx * sr + vy * cr, lerp(1.8, 2.2, rnd()), pal[0], 0.972, 50 * S, 1, True, False, 0.0, True))
        elif kind == 'crackle':
            self.sfx('crackle', x, 0.9, 0.5)
            for _ in range(int(140 * sz * q)):
                dx, dy = sphere()
                sp = lerp(0.6, 1.0, rnd()) * 265 * S * sz
                self.add(Spark(x, y, dx * sp, dy * sp, lerp(1.6, 2.0, rnd()), ch([SILVER, GOLD, WARM]), 0.968, 60 * S, 1, True, True, 0.0, True, crk=2))
        elif kind == 'text':
            i, rel = data
            particle_r = max(2, int(round(2.0 * S)))
            for (tx, ty, _) in self.text_pts[i]:
                # Minimal burst spread to preserve crisp shape edges
                dx, dy = sphere()
                sp = lerp(100, 220, rnd()) * S
                col = random.choice([(255, 245, 190), (255, 230, 130), (255, 195, 70)])
                s = Spark(x, y, dx * sp, dy * sp, 99.0, col, 0.95, 0.0, particle_r, False, False, 0.0, True)
                s.tx, s.ty = tx, ty
                s.tconv = lerp(0.25, 0.40, rnd())
                s.hold = rel + rnd() * 1.5
                self.sparks.append(s)

    def launch_text_shell(self, i, rel):
        W, H, hy = self.W, self.H, self.hy
        x0 = W / 2 + (rnd() - 0.5) * 0.15 * W
        self.rockets.append(Rocket(self, x0, hy - 5, W / 2, self.text_cy[i], 'text', [GOLD], 1.4, 1.5, (i, rel)))

    def start_text(self, t0):
        gap = 3.2
        rel = t0 + gap * 2 + 1.55 + 7.0
        self.text_until = t0 + 19.5
        self.finale_from, self.finale_until = t0 + 21.0, t0 + 34.0
        self.sub_from, self.sub_until = t0 + gap * 2 + 1.55 + 2.6, rel
        for i in range(3):
            self.at(t0 + i * gap, self.launch_text_shell, i, rel)

    def launch_random(self, big=False):
        W, H, hy = self.W, self.H, self.hy
        sx = lerp(0.12, 0.88, rnd()) * W
        bx = clamp(sx + (rnd() - 0.5) * 0.35 * W, 0.1 * W, 0.9 * W)
        sz = 1.0
        if self.t < self.text_until:
            by = H * (lerp(0.06, 0.14, rnd()) if rnd() < 0.5 else lerp(0.62, 0.70, rnd()))
            sz = 0.72
        else:
            by = H * lerp(0.12, 0.52, rnd() ** 0.9)
        if big:
            sz = 1.22
        kind = random.choices(['peony', 'chrys', 'willow', 'ring', 'palm', 'crackle', 'double'],
                              [22, 22, 15, 10, 10, 10, 11])[0]
        pal = random.choice(SHELL_COLORS)
        if kind in ('willow', 'palm'):
            pal = [GOLD]
        dur = lerp(0.95, 1.6, clamp((hy - by) / (0.7 * H)))
        self.rockets.append(Rocket(self, sx, hy - 5, bx, by, kind, pal, sz, dur))

    def volley(self, n=5):
        for i in range(n):
            self.at(self.t + i * 0.18, self.launch_random, False)

    def update(self, dt):
        self.t += dt
        t, S = self.t, self.S
        if t >= self.next_text:
            self.start_text(self.next_text)
            self.next_text += PERIOD
        if self.timed:
            due = [x for x in self.timed if x[0] <= t]
            if due:
                self.timed = [x for x in self.timed if x[0] > t]
                for _, fn, a in due:
                    fn(*a)
        if t > 7.0 and len(self.sparks) < MAXP - 600:
            self.next_launch -= dt
            if self.next_launch <= 0:
                fin = self.finale_from <= t < self.finale_until
                base = 0.14 if fin else lerp(1.7, 0.45, smooth((t - 7.0) / 35.0))
                self.next_launch = base * lerp(0.6, 1.4, rnd())
                n = 1 + (1 if fin and rnd() < 0.6 else 0) + (1 if rnd() < 0.12 else 0)
                for _ in range(n):
                    self.launch_random(big=fin and rnd() < 0.25)
        self.rockets = [r for r in self.rockets if r.step(dt, self)]
        self.sparks = [s for s in self.sparks if s.step(dt, self)]
        for f in self.flashes:
            f[2] += dt
        self.flashes = [f for f in self.flashes if f[2] < 0.38]
        for p in self.smoke:
            p[0] += p[2] * dt
            p[1] += p[3] * dt
            p[4] += dt
        self.smoke = [p for p in self.smoke if p[4] < p[5]]
        k = 0.06 ** dt
        self.flash = [c * k for c in self.flash]
        fin_anar = (self.next_text - PERIOD + 10.0 <= t < self.next_text - PERIOD + 44.0) and t > TEXT0
        for a in self.anars:
            a.step(dt, self, fin_anar)
        self.rangoli.update(t)
        for d in self.diyas:
            d.update(t)
        if self.audio_q:
            rest = []
            for item in self.audio_q:
                if item[0] <= t:
                    self.audio.play(item[1], item[2], item[3])
                else:
                    rest.append(item)
            self.audio_q = rest

    def render(self, screen):
        W, H, hy, S, t = self.W, self.H, self.hy, self.S, self.t
        screen.blit(self.sky, (0, 0))
        for (x, y, ph, sp, v) in self.dstars:
            c = int(v * (0.45 + 0.55 * math.sin(t * sp + ph) ** 2)) + 10
            screen.set_at((x, y), (c, c, min(255, c + 25)))
        fl = self.flash
        fmax = max(fl)
        if fmax > 0.01:
            screen.fill(tuple(int(clamp(c * 0.55) * 255) for c in fl), (0, 0, W, hy + 2), special_flags=ADD)
        for p in self.smoke:
            u = p[4] / p[5]
            spr = self.smoke_sprites[min(5, p[6] + int(u * 2))]
            spr.set_alpha(int(p[7] * math.sin(math.pi * min(1.0, u)) ** 0.6))
            screen.blit(spr, (p[0] - spr.get_width() / 2, p[1] - spr.get_height() / 2))
        screen.blit(self.far, (0, self.city_oy))
        screen.blit(self.near, (0, self.city_oy))
        if fmax > 0.02:
            tmp = self.near_mask.copy()
            tmp.fill(tuple(int(clamp(c * 0.42) * 255) for c in fl) + (255,), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(tmp, (0, self.city_oy), special_flags=ADD)
        screen.blit(self.ground, (0, hy))
        self.rangoli.draw(screen)
        for d in self.diyas:
            if d.a > 0:
                f = d.flick(t)
                add_glow(screen, d.wx, d.y + 3 * S, int(150 * S * d.sc), int(58 * S * d.sc), (255, 120, 40), 0.40 * d.a * f)
        for a in self.anars:
            if a.heat > 0.02:
                add_glow(screen, a.x, a.y, int(170 * S), int(70 * S), (255, 170, 80), 0.45 * a.heat * (0.8 + 0.2 * rnd()))
        for d in self.diyas_draw:
            screen.blit(d.body, (d.bx, d.by))
            if d.a > 0:
                add_glow(screen, d.wx, d.wy + d.h * 0.25, int(d.w * 1.1), int(d.w * 0.75), (255, 130, 50), 0.55 * d.a * d.flick(t))
        flm = self.flm
        flm.fill((0, 0, 0))
        on = smooth((t - 0.8) / 7.0)
        for (x, y, col, ph, sp, r, thr) in self.city_lights:
            if on > thr:
                b = (0.55 + 0.45 * math.sin(t * sp + ph)) * min(1.0, (on - thr) * 6)
                c = scol(col, b)
                flm.set_at((int(x), int(y)), c)
                if b > 0.6:
                    flm.set_at((int(x) + 1, int(y)), scol(col, b * 0.5))
        for d in self.diyas:
            draw_flame(flm, d, t, S)
        rg = self.rangoli
        if t - rg.last_t < 0.22 and rg.last:
            sx, sy = rg.screen_pos(rg.last)
            add_glow(flm, sx, sy, int(14 * S) + 2, int(9 * S) + 2, (255, 210, 120), 1.0 - (t - rg.last_t) / 0.22)
        g = self.glow
        g.fill((11, 11, 11), special_flags=SUB)
        for r in self.rockets:
            pygame.draw.line(g, (255, 225, 170), (r.px, r.py), (r.x, r.y), 2)
            pygame.draw.circle(g, (255, 245, 220), (int(r.x), int(r.y)), max(1, int(2 * S)))
        for s in self.sparks:
            b = s.b
            if b <= 0.03:
                continue
            col = s.col
            if s.end:
                u = s.age / s.life
                col = mix(col, EMBER, min(1.0, u * u * 0.8))
            c = (int(col[0] * b), int(col[1] * b), int(col[2] * b))
            if s.trail and (s.vx * s.vx + s.vy * s.vy) > 900:
                pygame.draw.line(g, c, (s.px, s.py), (s.x, s.y), 2 if s.r > 1 else 1)
            pygame.draw.circle(g, c, (int(s.x), int(s.y)), s.r)
        for f in self.flashes:
            b = (1 - f[2] / 0.38) ** 2
            rad = max(20, int(round(130 * S * f[3] / 20.0)) * 20)
            add_glow(g, f[0], f[1], rad, rad, mix(f[4], (255, 255, 255), 0.5), b * 0.9)
        bright = g.copy()
        bright.blit(flm, (0, 0), special_flags=ADD)
        screen.blit(bright, (0, 0), special_flags=ADD)
        s1 = pygame.transform.smoothscale(bright, (max(2, W // 4), max(2, H // 4)))
        screen.blit(pygame.transform.smoothscale(s1, (W, H)), (0, 0), special_flags=ADD)
        s2 = pygame.transform.smoothscale(s1, (max(2, W // 12), max(2, H // 12)))
        big = pygame.transform.smoothscale(s2, (W, H))
        screen.blit(big, (0, 0), special_flags=ADD)
        screen.blit(big, (0, 0), special_flags=ADD)
        if fmax > 0.02:
            screen.fill(tuple(int(clamp(c * 0.30) * 255) for c in fl), (0, hy, W, H - hy), special_flags=ADD)
        if self.sub_from < t < self.sub_until + 1.5:
            a = smooth((t - self.sub_from) / 1.6) * (1 - smooth((t - self.sub_until) / 1.5))
            if a > 0.01:
                for img, yy in ((self.sub1, 0.56), (self.sub2, 0.60)):
                    img.set_alpha(int(255 * a))
                    screen.blit(img, (W // 2 - img.get_width() // 2, int(yy * H)))
        if self.tagimg is not None:
            ta = smooth((t - 2.0) / 3.0)
            self.tagimg.set_alpha(int(150 * ta))
            screen.blit(self.tagimg, (W // 2 - self.tagimg.get_width() // 2, int(H * 0.972)))
        screen.blit(self.vig, (0, 0), special_flags=MULT)


def main():
    ap = argparse.ArgumentParser(description="Happy Diwali 2026 - cinematic python animation")
    ap.add_argument('--w', type=int, default=720)
    ap.add_argument('--h', type=int, default=1280)
    ap.add_argument('--fps', type=int, default=60)
    ap.add_argument('--mute', action='store_true')
    ap.add_argument('--record', type=str, default='')
    ap.add_argument('--seconds', type=float, default=60.0)
    ap.add_argument('--tag', type=str, default='@codingwithvishesh')
    ap.add_argument('--seed', type=int, default=2026)
    a = ap.parse_args()
    random.seed(a.seed)

    pygame.init()
    pygame.display.set_caption("Happy Diwali 2026 - Coding with Vishesh")
    info = pygame.display.Info()
    sc = min(1.0, (info.current_h * 0.88) / a.h) if info.current_h > 0 else 0.7
    win = (max(240, int(a.w * sc)), max(320, int(a.h * sc)))
    screen = pygame.display.set_mode(win, pygame.RESIZABLE)
    canvas = pygame.Surface((a.w, a.h)).convert()
    audio = Audio(not a.mute and not a.record)
    show = Show(a.w, a.h, audio, a.tag)

    writer = None
    if a.record:
        try:
            import imageio
            writer = imageio.get_writer(a.record, fps=a.fps, codec='libx264', quality=8,
                                        pixelformat='yuv420p', macro_block_size=1)
        except Exception as e:
            print("Recording ke liye:  pip install imageio imageio-ffmpeg   ->", e)
            sys.exit(1)

    dt = 1.0 / a.fps
    clock = pygame.time.Clock()
    acc = 0.0
    frames = int(a.seconds * a.fps)
    n = 0
    running = True
    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    running = False
                elif ev.key == pygame.K_SPACE:
                    show = Show(a.w, a.h, audio, a.tag)
                elif ev.key == pygame.K_r:
                    show.volley(6)
                elif ev.key == pygame.K_m:
                    audio.muted = not audio.muted
            elif ev.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode(ev.size, pygame.RESIZABLE)
        if writer:
            show.update(dt)
        else:
            acc += min(clock.tick(a.fps) / 1000.0, 0.1)
            steps = 0
            while acc >= dt and steps < 3:
                show.update(dt)
                acc -= dt
                steps += 1
        show.render(canvas)
        if writer:
            arr = pygame.surfarray.array3d(canvas)
            writer.append_data(np.ascontiguousarray(np.transpose(arr, (1, 0, 2))))
            n += 1
            if n % a.fps == 0:
                print("  recorded %ds / %ds" % (n // a.fps, a.seconds), end="\r")
            if n >= frames:
                break
        sw, sh = screen.get_size()
        k = min(sw / a.w, sh / a.h)
        tw, th = max(2, int(a.w * k)), max(2, int(a.h * k))
        screen.fill((0, 0, 0))
        screen.blit(pygame.transform.smoothscale(canvas, (tw, th)), ((sw - tw) // 2, (sh - th) // 2))
        pygame.display.flip()
    if writer:
        writer.close()
        print("\nSaved ->", a.record)
    pygame.quit()


if __name__ == "__main__":
    main()