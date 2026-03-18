"""
sphere_renderer.py — 3D particle sphere with multi-state voice-reactive effects.

States:
    STANDBY   — calm blue sphere, slow rotation
    LISTENING — particles scatter, cyan/bright
    THINKING  — particles orbit tightly, amber pulse
    SPEAKING  — particles pulse rhythmically, green tint
"""

import math
import os
import random
import pygame

# ── Paths ─────────────────────────────────────────────────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(_HERE, "assets", "Orbitron.ttf")

# ── State constants ───────────────────────────────────────────────────
STATE_STANDBY   = "standby"
STATE_LISTENING = "listening"
STATE_THINKING  = "thinking"
STATE_SPEAKING  = "speaking"

# ── Colour palettes per state ─────────────────────────────────────────
PALETTES = {
    STATE_STANDBY:   {"core": (0, 100, 180),  "glow": (0, 40, 80),   "label": (0, 90, 140),  "text": "[ STANDBY ]"},
    STATE_LISTENING: {"core": (0, 220, 255),  "glow": (0, 80, 140),  "label": (0, 255, 200), "text": "[ LISTENING ]"},
    STATE_THINKING:  {"core": (255, 180, 40), "glow": (80, 60, 10),  "label": (255, 200, 60),"text": "[ THINKING... ]"},
    STATE_SPEAKING:  {"core": (0, 255, 120),  "glow": (0, 80, 40),   "label": (0, 255, 160), "text": "[ SPEAKING ]"},
}

# ── Window / Sphere ──────────────────────────────────────────────────
BG_COLOR        = (5, 5, 15)
WIDTH, HEIGHT   = 800, 800
FPS             = 60
CX, CY         = WIDTH // 2, HEIGHT // 2
SPHERE_RADIUS   = 160
NUM_PARTICLES   = 500
PERSPECTIVE     = 600
SCATTER_FORCE   = 120
TEXT_DIM        = (0, 80, 130)
RESPONSE_COLOR  = (0, 255, 200)


class _Particle:
    __slots__ = ("home_x", "home_y", "home_z",
                 "x", "y", "z",
                 "scatter_x", "scatter_y", "scatter_z",
                 "size")

    def __init__(self, hx, hy, hz):
        self.home_x, self.home_y, self.home_z = hx, hy, hz
        self.x, self.y, self.z = hx, hy, hz
        self.scatter_x = self.scatter_y = self.scatter_z = 0.0
        self.size = random.uniform(1.2, 2.5)


class SphereRenderer:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Parker — Voice-Reactive Sphere")
        self.clock = pygame.time.Clock()

        try:
            self.font_big   = pygame.font.Font(FONT_PATH, 38)
            self.font_med   = pygame.font.Font(FONT_PATH, 16)
            self.font_small = pygame.font.Font(FONT_PATH, 12)
            self.font_resp  = pygame.font.Font(FONT_PATH, 15)
        except Exception:
            self.font_big   = pygame.font.SysFont("Consolas", 38, bold=True)
            self.font_med   = pygame.font.SysFont("Consolas", 16)
            self.font_small = pygame.font.SysFont("Consolas", 12)
            self.font_resp  = pygame.font.SysFont("Consolas", 15)

        self._tick      = 0
        self._state     = STATE_STANDBY
        self._pulse     = 0.0
        self._rot_y     = 0.0
        self._rot_x     = 0.3

        # Response text display
        self._response_text  = ""
        self._response_alpha = 0

        # Greeting text display
        self._greeting       = ""
        self._greet_alpha    = 0

        # User transcription display
        self._user_text      = ""
        self._user_alpha     = 0

        self._particles = self._make_sphere(NUM_PARTICLES, SPHERE_RADIUS)

    # ── public API ────────────────────────────────────────────────

    def set_state(self, state: str) -> None:
        self._state = state

    def show_greeting(self, text: str) -> None:
        self._greeting = text
        self._greet_alpha = 255

    def show_response(self, text: str) -> None:
        self._response_text = text
        self._response_alpha = 255

    def show_user_text(self, text: str) -> None:
        self._user_text = f'You: "{text}"'
        self._user_alpha = 255

    def tick(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return False
        self._tick += 1
        self._update_pulse()
        self._update_particles()
        self._draw()
        self.clock.tick(FPS)
        return True

    def quit(self) -> None:
        pygame.quit()

    # ── internals ─────────────────────────────────────────────────

    @staticmethod
    def _make_sphere(n, radius):
        particles = []
        golden = math.pi * (3.0 - math.sqrt(5.0))
        for i in range(n):
            y = 1 - (i / float(n - 1)) * 2
            r = math.sqrt(1 - y * y)
            theta = golden * i
            x = math.cos(theta) * r
            z = math.sin(theta) * r
            particles.append(_Particle(x * radius, y * radius, z * radius))
        return particles

    def _update_pulse(self):
        targets = {STATE_STANDBY: 0.0, STATE_LISTENING: 1.0,
                   STATE_THINKING: 0.7, STATE_SPEAKING: 0.85}
        target = targets.get(self._state, 0.0)
        speed  = 0.10 if target > self._pulse else 0.04
        self._pulse += (target - self._pulse) * speed

    def _update_particles(self):
        p = self._pulse
        state = self._state

        # Rotation speed varies by state
        if state == STATE_THINKING:
            self._rot_y += 0.025       # fast tight spin
        elif state == STATE_SPEAKING:
            self._rot_y += 0.008 + math.sin(self._tick * 0.1) * 0.005
        elif state == STATE_LISTENING:
            self._rot_y += 0.016
        else:
            self._rot_y += 0.004

        cos_ry = math.cos(self._rot_y)
        sin_ry = math.sin(self._rot_y)
        cos_rx = math.cos(self._rot_x)
        sin_rx = math.sin(self._rot_x)

        for pt in self._particles:
            rx  = pt.home_x * cos_ry + pt.home_z * sin_ry
            rz  = -pt.home_x * sin_ry + pt.home_z * cos_ry
            ry  = pt.home_y
            ry2 = ry * cos_rx - rz * sin_rx
            rz2 = ry * sin_rx + rz * cos_rx

            if state == STATE_LISTENING:
                if random.random() < 0.08:
                    pt.scatter_x = random.uniform(-SCATTER_FORCE, SCATTER_FORCE) * p
                    pt.scatter_y = random.uniform(-SCATTER_FORCE, SCATTER_FORCE) * p
                    pt.scatter_z = random.uniform(-SCATTER_FORCE * 0.5, SCATTER_FORCE * 0.5) * p
            elif state == STATE_THINKING:
                # Particles pull inward slightly and jitter
                pt.scatter_x = pt.scatter_x * 0.85 + random.uniform(-3, 3)
                pt.scatter_y = pt.scatter_y * 0.85 + random.uniform(-3, 3)
                pt.scatter_z = pt.scatter_z * 0.85
            elif state == STATE_SPEAKING:
                # Rhythmic pulse outward
                pulse_off = math.sin(self._tick * 0.15) * 15 * p
                pt.scatter_x = pt.scatter_x * 0.9 + random.uniform(-2, 2)
                pt.scatter_y = pt.scatter_y * 0.9 + pulse_off * 0.05
                pt.scatter_z = pt.scatter_z * 0.9
            else:
                pt.scatter_x *= 0.92
                pt.scatter_y *= 0.92
                pt.scatter_z *= 0.92

            pt.x = rx + pt.scatter_x
            pt.y = ry2 + pt.scatter_y
            pt.z = rz2 + pt.scatter_z

    def _draw(self):
        self.screen.fill(BG_COLOR)
        p = self._pulse
        pal = PALETTES.get(self._state, PALETTES[STATE_STANDBY])
        core_c = pal["core"]
        glow_c = pal["glow"]

        # ── background glow ───────────────────────────────────────
        glow_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        glow_r = int(220 + p * 80)
        for i in range(glow_r, 0, -6):
            frac = i / glow_r
            alpha = int((4 + p * 6) * frac)
            c = (*glow_c, alpha)
            pygame.draw.circle(glow_surf, c, (CX, CY), i)
        self.screen.blit(glow_surf, (0, 0))

        # ── project & draw particles ──────────────────────────────
        projected = []
        for pt in self._particles:
            z_off = pt.z + 400
            if z_off < 10:
                z_off = 10
            scale = PERSPECTIVE / z_off
            sx = int(CX + pt.x * scale)
            sy = int(CY + pt.y * scale)
            norm_z = (pt.z + SPHERE_RADIUS) / (2 * SPHERE_RADIUS + 1)
            projected.append((sx, sy, z_off, pt.size, max(0, min(1, norm_z))))

        projected.sort(key=lambda q: q[2])

        p_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for sx, sy, _, base_size, brightness in projected:
            b = 0.3 + 0.7 * brightness
            r_c = int(core_c[0] * b)
            g_c = int(core_c[1] * b)
            b_c = int(core_c[2] * b)
            alpha = int((120 + p * 135) * b)
            size = max(1, int(base_size * (0.8 + 0.5 * b) * (1.0 + p * 0.4)))
            if size >= 2:
                pygame.draw.circle(p_surf, (r_c, g_c, b_c, int(alpha * 0.3)),
                                   (sx, sy), size + 2)
            pygame.draw.circle(p_surf, (r_c, g_c, b_c, alpha), (sx, sy), size)
        self.screen.blit(p_surf, (0, 0))

        # ── "PARKER" centre text ──────────────────────────────────
        t_alpha = int(180 + p * 75)
        tc = core_c
        title = self.font_big.render("PARKER", True, tc)
        title.set_alpha(t_alpha)
        tr = title.get_rect(center=(CX, CY))
        self.screen.blit(title, tr)

        # ── status label ──────────────────────────────────────────
        status = self.font_med.render(pal["text"], True, pal["label"])
        self.screen.blit(status, (CX - status.get_width() // 2, CY + 230))

        # ── user text (what they said) ────────────────────────────
        if self._user_alpha > 0:
            ut = self.font_resp.render(self._user_text, True, (150, 200, 255))
            ut.set_alpha(int(self._user_alpha))
            self.screen.blit(ut, (CX - ut.get_width() // 2, CY + 260))
            self._user_alpha = max(0, self._user_alpha - 0.5)

        # ── response text ─────────────────────────────────────────
        if self._response_alpha > 0:
            # Word-wrap long responses
            words = self._response_text.split()
            lines = []
            line = ""
            for w in words:
                test = f"{line} {w}".strip()
                if self.font_resp.size(test)[0] > WIDTH - 100:
                    lines.append(line)
                    line = w
                else:
                    line = test
            if line:
                lines.append(line)

            for i, ln in enumerate(lines):
                rt = self.font_resp.render(ln, True, RESPONSE_COLOR)
                rt.set_alpha(int(self._response_alpha))
                self.screen.blit(rt, (CX - rt.get_width() // 2, CY + 290 + i * 24))
            self._response_alpha = max(0, self._response_alpha - 0.3)

        # ── greeting text ─────────────────────────────────────────
        if self._greet_alpha > 0:
            gt = self.font_resp.render(self._greeting, True, RESPONSE_COLOR)
            gt.set_alpha(int(self._greet_alpha))
            self.screen.blit(gt, (CX - gt.get_width() // 2, CY + 270))
            self._greet_alpha = max(0, self._greet_alpha - 0.4)

        # ── corner HUD ────────────────────────────────────────────
        corners = [
            ("SYS ONLINE", 20, 18),
            ("MIC: ACTIVE" if self._state != STATE_STANDBY else "MIC: IDLE", 20, HEIGHT - 35),
            ("PARKER v1.0", WIDTH - 160, HEIGHT - 35),
        ]
        for text, x, y in corners:
            lbl = self.font_small.render(text, True, TEXT_DIM)
            self.screen.blit(lbl, (x, y))

        pygame.display.flip()
