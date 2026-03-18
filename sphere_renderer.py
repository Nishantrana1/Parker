"""
sphere_renderer.py — 3D particle sphere with voice-reactive scatter effect.

Renders ~500 particles arranged on a sphere surface using Fibonacci distribution.
The sphere slowly rotates.  When voice is detected the particles scatter outward
randomly and shimmer; when silent they smoothly reform into the sphere shape.
"PARKER" is displayed at the centre in a cyberpunk Orbitron font.
"""

import math
import os
import random
import pygame

# ── Paths ─────────────────────────────────────────────────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(_HERE, "assets", "Orbitron.ttf")

# ── Colours ───────────────────────────────────────────────────────────
BG_COLOR       = (5, 5, 15)
CYAN           = (0, 200, 255)
CYAN_BRIGHT    = (0, 255, 255)
CYAN_DIM       = (0, 60, 100)
WHITE_GLOW     = (180, 230, 255)
STATUS_ACTIVE  = (0, 255, 200)
STATUS_IDLE    = (0, 90, 140)
GREETING_COLOR = (0, 220, 255)
TEXT_DIM       = (0, 80, 130)

# ── Window / Sphere ──────────────────────────────────────────────────
WIDTH, HEIGHT   = 800, 800
FPS             = 60
CX, CY         = WIDTH // 2, HEIGHT // 2
SPHERE_RADIUS   = 160
NUM_PARTICLES   = 500
PERSPECTIVE     = 600        # perspective projection depth
SCATTER_FORCE   = 120        # max scatter distance
RETURN_SPEED    = 0.04       # how fast particles re-form


class _Particle:
    """A single point on the sphere surface."""

    __slots__ = ("home_x", "home_y", "home_z",
                 "x", "y", "z",
                 "scatter_x", "scatter_y", "scatter_z",
                 "size")

    def __init__(self, hx, hy, hz):
        self.home_x, self.home_y, self.home_z = hx, hy, hz
        self.x, self.y, self.z = hx, hy, hz
        self.scatter_x = 0.0
        self.scatter_y = 0.0
        self.scatter_z = 0.0
        self.size = random.uniform(1.2, 2.5)


class SphereRenderer:
    """Pygame renderer for a 3D particle sphere."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Parker — Voice-Reactive Sphere")
        self.clock = pygame.time.Clock()

        # Fonts
        try:
            self.font_big   = pygame.font.Font(FONT_PATH, 38)
            self.font_med   = pygame.font.Font(FONT_PATH, 16)
            self.font_small = pygame.font.Font(FONT_PATH, 12)
            self.font_greet = pygame.font.Font(FONT_PATH, 18)
        except Exception:
            self.font_big   = pygame.font.SysFont("Consolas", 38, bold=True)
            self.font_med   = pygame.font.SysFont("Consolas", 16)
            self.font_small = pygame.font.SysFont("Consolas", 12)
            self.font_greet = pygame.font.SysFont("Consolas", 18)

        # State
        self._tick       = 0
        self._active     = False
        self._pulse      = 0.0          # 0→1 smoothed
        self._rot_y      = 0.0          # Y-axis rotation angle
        self._rot_x      = 0.3          # slight tilt
        self._greeting   = ""           # shown at bottom while visible
        self._greet_alpha = 0           # fade counter

        # Generate particles on sphere using Fibonacci distribution
        self._particles = self._make_sphere_particles(NUM_PARTICLES, SPHERE_RADIUS)

    # ── public API ────────────────────────────────────────────────────

    def set_active(self, active: bool) -> None:
        self._active = active

    def show_greeting(self, text: str) -> None:
        """Display greeting text that fades after a few seconds."""
        self._greeting = text
        self._greet_alpha = 255

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

    # ── particle generation ──────────────────────────────────────────

    @staticmethod
    def _make_sphere_particles(n, radius):
        """Fibonacci sphere point distribution."""
        particles = []
        golden = math.pi * (3.0 - math.sqrt(5.0))
        for i in range(n):
            y = 1 - (i / float(n - 1)) * 2       # y goes from 1 to -1
            r = math.sqrt(1 - y * y)
            theta = golden * i
            x = math.cos(theta) * r
            z = math.sin(theta) * r
            particles.append(_Particle(x * radius, y * radius, z * radius))
        return particles

    # ── update logic ─────────────────────────────────────────────────

    def _update_pulse(self):
        target = 1.0 if self._active else 0.0
        speed  = 0.12 if self._active else 0.03
        self._pulse += (target - self._pulse) * speed

    def _update_particles(self):
        p = self._pulse

        # Rotate the sphere
        base_speed = 0.004
        self._rot_y += base_speed + p * 0.012

        cos_ry = math.cos(self._rot_y)
        sin_ry = math.sin(self._rot_y)
        cos_rx = math.cos(self._rot_x)
        sin_rx = math.sin(self._rot_x)

        for pt in self._particles:
            # Rotate home position to get current target
            # Y rotation
            rx = pt.home_x * cos_ry + pt.home_z * sin_ry
            rz = -pt.home_x * sin_ry + pt.home_z * cos_ry
            ry = pt.home_y
            # X rotation (tilt)
            ry2 = ry * cos_rx - rz * sin_rx
            rz2 = ry * sin_rx + rz * cos_rx

            if self._active:
                # Generate new scatter offset occasionally
                if random.random() < 0.08:
                    pt.scatter_x = random.uniform(-SCATTER_FORCE, SCATTER_FORCE) * p
                    pt.scatter_y = random.uniform(-SCATTER_FORCE, SCATTER_FORCE) * p
                    pt.scatter_z = random.uniform(-SCATTER_FORCE * 0.5, SCATTER_FORCE * 0.5) * p
            else:
                # Decay scatter back to zero
                pt.scatter_x *= 0.92
                pt.scatter_y *= 0.92
                pt.scatter_z *= 0.92

            pt.x = rx + pt.scatter_x
            pt.y = ry2 + pt.scatter_y
            pt.z = rz2 + pt.scatter_z

    # ── drawing ──────────────────────────────────────────────────────

    def _draw(self):
        self.screen.fill(BG_COLOR)
        p = self._pulse

        # ── background glow ───────────────────────────────────────
        glow_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        glow_r = int(220 + p * 80)
        for i in range(glow_r, 0, -6):
            alpha = int((4 + p * 6) * (i / glow_r))
            c = (0, int(40 + p * 60), int(80 + p * 60), alpha)
            pygame.draw.circle(glow_surf, c, (CX, CY), i)
        self.screen.blit(glow_surf, (0, 0))

        # ── project & sort particles by depth ─────────────────────
        projected = []
        for pt in self._particles:
            z_off = pt.z + 400       # shift so all z > 0
            if z_off < 10:
                z_off = 10
            scale = PERSPECTIVE / z_off
            sx = int(CX + pt.x * scale)
            sy = int(CY + pt.y * scale)
            depth = z_off
            projected.append((sx, sy, depth, pt.size, pt.z))

        # Sort far-to-near so nearer particles draw on top
        projected.sort(key=lambda q: q[2])

        # ── draw particles ────────────────────────────────────────
        particle_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for sx, sy, depth, base_size, raw_z in projected:
            # Brightness by depth — nearer = brighter
            norm_z = (raw_z + SPHERE_RADIUS) / (2 * SPHERE_RADIUS + 1)
            brightness = 0.3 + 0.7 * max(0, min(1, norm_z))

            r_c = int(0)
            g_c = int((140 + p * 100) * brightness)
            b_c = int((200 + p * 55) * brightness)
            alpha = int((120 + p * 135) * brightness)

            size = max(1, int(base_size * (0.8 + 0.5 * brightness) * (1.0 + p * 0.4)))

            # Glow around particle
            if size >= 2:
                glow_a = int(alpha * 0.3)
                pygame.draw.circle(particle_surf, (r_c, g_c, b_c, glow_a),
                                   (sx, sy), size + 2)
            pygame.draw.circle(particle_surf, (r_c, g_c, b_c, alpha),
                               (sx, sy), size)

        self.screen.blit(particle_surf, (0, 0))

        # ── "PARKER" text at centre ───────────────────────────────
        text_alpha = int(180 + p * 75)
        title_surf = pygame.Surface((300, 60), pygame.SRCALPHA)
        tc = (0, int(180 + p * 75), int(230 + p * 25), text_alpha)
        title = self.font_big.render("PARKER", True, tc[:3])
        title.set_alpha(tc[3])
        title_rect = title.get_rect(center=(150, 30))
        title_surf.blit(title, title_rect)
        self.screen.blit(title_surf, (CX - 150, CY - 30))

        # ── status label ──────────────────────────────────────────
        if self._active:
            status_text  = "[ LISTENING ]"
            status_color = STATUS_ACTIVE
        else:
            status_text  = "[ STANDBY ]"
            status_color = STATUS_IDLE

        status = self.font_med.render(status_text, True, status_color)
        self.screen.blit(status, (CX - status.get_width() // 2, CY + 230))

        # ── greeting text (fades) ─────────────────────────────────
        if self._greet_alpha > 0:
            greet = self.font_greet.render(self._greeting, True, GREETING_COLOR)
            greet.set_alpha(self._greet_alpha)
            self.screen.blit(greet, (CX - greet.get_width() // 2, CY + 270))
            self._greet_alpha = max(0, self._greet_alpha - 0.4)

        # ── corner HUD labels ─────────────────────────────────────
        corners = [
            ("SYS ONLINE", 20, 18),
            ("MIC: ACTIVE" if self._active else "MIC: IDLE", 20, HEIGHT - 35),
            ("PARKER v1.0", WIDTH - 160, HEIGHT - 35),
        ]
        for text, x, y in corners:
            lbl = self.font_small.render(text, True, TEXT_DIM)
            self.screen.blit(lbl, (x, y))

        pygame.display.flip()
