#!/usr/bin/env python3
"""
Graphic Design & Generative Visual Engineering Nucleus Engine
Pure Python 3 standard library implementation (zero external dependencies).

Core Capabilities:
1. Color Science & WCAG 2.2 System (sRGB, CIE XYZ, CIELAB, CIELCh, HSL, Contrast Ratios, WCAG AAA validation)
2. Harmonious Palette Generator (Monochromatic, Analogous, Complementary, Triadic, Split-Complementary, Tetradic, Perceptual Gradient Scales)
3. Cubic Bézier Curve Geometry (Parametric evaluation, derivatives, normal, curvature, Gauss-Legendre arc length, De Casteljau subdivision, tight BBox)
4. Procedural 24px Grid Icon & Generative Geometric Poster Builders (Penpot/Lucide standard SVG generator)
5. 100% Deterministic Assert-based Verification Suite
"""

import sys
import math
from typing import List, Tuple, Dict, Any, Optional, Union

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


# ============================================================================
# 1. COLOR MATHEMATICS & WCAG 2.2 CONTRAST ENGINE
# ============================================================================

class Color:
    """
    Precision color representation with sRGB, CIE XYZ, CIELAB, CIELCh, and HSL support.
    Follows ITU-R BT.709 / CIE 1931 standard 2° observer under D65 illuminant.
    """
    # D65 standard illuminant reference white
    XN = 0.95047
    YN = 1.00000
    ZN = 1.08883

    def __init__(self, r: int, g: int, b: int, a: float = 1.0):
        self.r = max(0, min(255, int(round(r))))
        self.g = max(0, min(255, int(round(g))))
        self.b = max(0, min(255, int(round(b))))
        self.a = max(0.0, min(1.0, float(a)))

    @classmethod
    def from_hex(cls, hex_str: str) -> "Color":
        """Parse hex color (#RGB, #RGBA, #RRGGBB, #RRGGBBAA)."""
        s = hex_str.strip().lstrip("#")
        if len(s) == 3:
            r, g, b = [int(c * 2, 16) for c in s]
            return cls(r, g, b)
        elif len(s) == 4:
            r, g, b, a = [int(c * 2, 16) for c in s]
            return cls(r, g, b, a / 255.0)
        elif len(s) == 6:
            r = int(s[0:2], 16)
            g = int(s[2:4], 16)
            b = int(s[4:6], 16)
            return cls(r, g, b)
        elif len(s) == 8:
            r = int(s[0:2], 16)
            g = int(s[2:4], 16)
            b = int(s[4:6], 16)
            a = int(s[6:8], 16) / 255.0
            return cls(r, g, b, a)
        raise ValueError(f"Invalid hex color format: {hex_str}")

    @classmethod
    def from_hsl(cls, h: float, s: float, l: float, a: float = 1.0) -> "Color":
        """Construct Color from HSL (H in [0, 360), S in [0, 1], L in [0, 1])."""
        h = h % 360.0
        s = max(0.0, min(1.0, s))
        l = max(0.0, min(1.0, l))

        c = (1.0 - abs(2.0 * l - 1.0)) * s
        x = c * (1.0 - abs((h / 60.0) % 2.0 - 1.0))
        m = l - c / 2.0

        if 0.0 <= h < 60.0:
            rp, gp, bp = c, x, 0.0
        elif 60.0 <= h < 120.0:
            rp, gp, bp = x, c, 0.0
        elif 120.0 <= h < 180.0:
            rp, gp, bp = 0.0, c, x
        elif 180.0 <= h < 240.0:
            rp, gp, bp = 0.0, x, c
        elif 240.0 <= h < 300.0:
            rp, gp, bp = x, 0.0, c
        else:
            rp, gp, bp = c, 0.0, x

        return cls(round((rp + m) * 255.0), round((gp + m) * 255.0), round((bp + m) * 255.0), a)

    @classmethod
    def from_lab(cls, L: float, a: float, b: float, alpha: float = 1.0) -> "Color":
        """Construct Color from CIELAB (L* in [0, 100], a*, b* in [-128, 128])."""
        delta = 6.0 / 29.0
        fy = (L + 16.0) / 116.0
        fx = fy + (a / 500.0)
        fz = fy - (b / 200.0)

        def f_inv(t: float) -> float:
            if t > delta:
                return t ** 3
            return 3.0 * (delta ** 2) * (t - 4.0 / 29.0)

        X = cls.XN * f_inv(fx)
        Y = cls.YN * f_inv(fy)
        Z = cls.ZN * f_inv(fz)

        # CIE XYZ to Linear sRGB
        r_lin = 3.2404542 * X - 1.5371385 * Y - 0.4985314 * Z
        g_lin = -0.9692660 * X + 1.8760108 * Y + 0.0415560 * Z
        b_lin = 0.0556434 * X - 0.2040259 * Y + 1.0572252 * Z

        # Linear to gamma-corrected sRGB
        def compand(c: float) -> float:
            c = max(0.0, min(1.0, c))
            if c <= 0.0031308:
                return 12.92 * c
            return 1.055 * (c ** (1.0 / 2.4)) - 0.055

        return cls(round(compand(r_lin) * 255.0), round(compand(g_lin) * 255.0), round(compand(b_lin) * 255.0), alpha)

    @classmethod
    def from_lch(cls, L: float, C: float, h_deg: float, alpha: float = 1.0) -> "Color":
        """Construct Color from CIELCh (Cylindrical CIELAB)."""
        rad = math.radians(h_deg % 360.0)
        a = C * math.cos(rad)
        b = C * math.sin(rad)
        return cls.from_lab(L, a, b, alpha)

    def to_hex(self, include_alpha: bool = False) -> str:
        """Return uppercase hex string."""
        if include_alpha:
            return f"#{self.r:02X}{self.g:02X}{self.b:02X}{round(self.a * 255):02X}"
        return f"#{self.r:02X}{self.g:02X}{self.b:02X}"

    def to_rgb_tuple(self) -> Tuple[int, int, int]:
        return (self.r, self.g, self.b)

    def to_hsl(self) -> Tuple[float, float, float]:
        """Convert sRGB to HSL (H in [0, 360), S in [0, 1], L in [0, 1])."""
        r_norm, g_norm, b_norm = self.r / 255.0, self.g / 255.0, self.b / 255.0
        cmax = max(r_norm, g_norm, b_norm)
        cmin = min(r_norm, g_norm, b_norm)
        delta = cmax - cmin

        l = (cmax + cmin) / 2.0

        if delta == 0.0:
            h = 0.0
            s = 0.0
        else:
            s = delta / (1.0 - abs(2.0 * l - 1.0))
            if cmax == r_norm:
                h = 60.0 * (((g_norm - b_norm) / delta) % 6.0)
            elif cmax == g_norm:
                h = 60.0 * (((b_norm - r_norm) / delta) + 2.0)
            else:
                h = 60.0 * (((r_norm - g_norm) / delta) + 4.0)
            h = (h + 360.0) % 360.0

        return (round(h, 2), round(s, 4), round(l, 4))

    def to_lab(self) -> Tuple[float, float, float]:
        """Convert sRGB to CIELAB (L*, a*, b*)."""
        def linearize(c_byte: int) -> float:
            c = c_byte / 255.0
            if c <= 0.04045:
                return c / 12.92
            return ((c + 0.055) / 1.055) ** 2.4

        r_lin = linearize(self.r)
        g_lin = linearize(self.g)
        b_lin = linearize(self.b)

        # Linear sRGB to CIE XYZ
        X = 0.4124564 * r_lin + 0.3575761 * g_lin + 0.1804375 * b_lin
        Y = 0.2126729 * r_lin + 0.7151522 * g_lin + 0.0721750 * b_lin
        Z = 0.0193339 * r_lin + 0.1191920 * g_lin + 0.9503041 * b_lin

        # XYZ to LAB
        delta = 6.0 / 29.0
        delta3 = delta ** 3

        def f(t: float) -> float:
            if t > delta3:
                return t ** (1.0 / 3.0)
            return (t / (3.0 * delta ** 2)) + (4.0 / 29.0)

        fx = f(X / self.XN)
        fy = f(Y / self.YN)
        fz = f(Z / self.ZN)

        L = 116.0 * fy - 16.0
        a = 500.0 * (fx - fy)
        b = 200.0 * (fy - fz)

        return (round(L, 4), round(a, 4), round(b, 4))

    def to_lch(self) -> Tuple[float, float, float]:
        """Convert sRGB to CIELCh (L*, C*, h_deg)."""
        L, a, b = self.to_lab()
        C = math.sqrt(a * a + b * b)
        h_rad = math.atan2(b, a)
        h_deg = (math.degrees(h_rad) + 360.0) % 360.0
        return (round(L, 4), round(C, 4), round(h_deg, 2))

    def relative_luminance(self) -> float:
        """
        Calculate relative luminance according to WCAG 2.1/2.2 standard.
        Y = 0.2126 * R_lin + 0.7152 * G_lin + 0.0722 * B_lin.
        """
        def linearize(c_byte: int) -> float:
            c = c_byte / 255.0
            if c <= 0.04045:
                return c / 12.92
            return ((c + 0.055) / 1.055) ** 2.4

        r_lin = linearize(self.r)
        g_lin = linearize(self.g)
        b_lin = linearize(self.b)

        return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin

    def contrast_ratio(self, other: "Color") -> float:
        """
        Calculate WCAG contrast ratio between this color and another color.
        Formula: (L1 + 0.05) / (L2 + 0.05) where L1 >= L2.
        Result is in range [1.0, 21.0].
        """
        l1 = self.relative_luminance()
        l2 = other.relative_luminance()
        lighter = max(l1, l2)
        darker = min(l1, l2)
        return round((lighter + 0.05) / (darker + 0.05), 4)

    def wcag_compliance(self, other: "Color") -> Dict[str, bool]:
        """
        Evaluate WCAG 2.2 accessibility compliance against a background color.
        - AA Normal Text: >= 4.5:1
        - AA Large Text / UI Components: >= 3.0:1
        - AAA Normal Text: >= 7.0:1
        - AAA Large Text: >= 4.5:1
        """
        cr = self.contrast_ratio(other)
        return {
            "contrast_ratio": cr,
            "aa_normal": cr >= 4.5,
            "aa_large": cr >= 3.0,
            "aaa_normal": cr >= 7.0,
            "aaa_large": cr >= 4.5,
            "ui_component": cr >= 3.0
        }

    def lerp(self, other: "Color", t: float) -> "Color":
        """Perceptually smooth linear interpolation in CIELAB space."""
        t = max(0.0, min(1.0, t))
        l1, a1, b1 = self.to_lab()
        l2, a2, b2 = other.to_lab()
        return Color.from_lab(
            l1 + (l2 - l1) * t,
            a1 + (a2 - a1) * t,
            b1 + (b2 - b1) * t,
            self.a + (other.a - self.a) * t
        )

    def __repr__(self) -> str:
        return f"Color({self.to_hex()})"


class PaletteGenerator:
    """
    Harmonious color palette generator supporting classical color wheel (HSL)
    and perceptually uniform (CIELCh / CIELAB) palettes.
    """
    @staticmethod
    def monochromatic(base: Color, count: int = 5) -> List[Color]:
        """Generate a monochromatic ramp varying in Lightness."""
        h, s, _ = base.to_hsl()
        step = 0.80 / (count + 1)
        return [Color.from_hsl(h, s, 0.10 + (i + 1) * step) for i in range(count)]

    @staticmethod
    def analogous(base: Color, angle_step: float = 30.0, count: int = 5) -> List[Color]:
        """Generate analogous colors clustered around base hue."""
        h, s, l = base.to_hsl()
        half = count // 2
        palette = []
        for i in range(-half, -half + count):
            new_h = (h + i * angle_step) % 360.0
            palette.append(Color.from_hsl(new_h, s, l))
        return palette

    @staticmethod
    def complementary(base: Color) -> Tuple[Color, Color]:
        """Generate complementary color pair (180° offset)."""
        h, s, l = base.to_hsl()
        return (base, Color.from_hsl((h + 180.0) % 360.0, s, l))

    @staticmethod
    def triadic(base: Color) -> Tuple[Color, Color, Color]:
        """Generate triadic 3-color harmony (120° offsets)."""
        h, s, l = base.to_hsl()
        return (
            base,
            Color.from_hsl((h + 120.0) % 360.0, s, l),
            Color.from_hsl((h + 240.0) % 360.0, s, l)
        )

    @staticmethod
    def split_complementary(base: Color, angle: float = 150.0) -> Tuple[Color, Color, Color]:
        """Generate split-complementary harmony (base + 2 colors flanking complement)."""
        h, s, l = base.to_hsl()
        return (
            base,
            Color.from_hsl((h + angle) % 360.0, s, l),
            Color.from_hsl((h - angle + 360.0) % 360.0, s, l)
        )

    @staticmethod
    def tetradic(base: Color, angle: float = 60.0) -> Tuple[Color, Color, Color, Color]:
        """Generate tetradic rectangular 4-color harmony."""
        h, s, l = base.to_hsl()
        return (
            base,
            Color.from_hsl((h + angle) % 360.0, s, l),
            Color.from_hsl((h + 180.0) % 360.0, s, l),
            Color.from_hsl((h + 180.0 + angle) % 360.0, s, l)
        )

    @staticmethod
    def scale(colors: List[Color], steps: int = 10) -> List[Color]:
        """Generate multi-stop gradient scale interpolated in CIELAB space."""
        if len(colors) < 2:
            return colors * steps
        result = []
        num_segments = len(colors) - 1
        for i in range(steps):
            t_global = i / max(1, steps - 1)
            seg_idx = min(num_segments - 1, int(t_global * num_segments))
            t_local = (t_global * num_segments) - seg_idx
            c_lerp = colors[seg_idx].lerp(colors[seg_idx + 1], t_local)
            result.append(c_lerp)
        return result


# ============================================================================
# 2. 2D VECTOR & CUBIC BÉZIER CURVE ENGINE
# ============================================================================

class Vec2D:
    """Immutable 2D vector for visual geometry and coordinate transformations."""
    __slots__ = ('x', 'y')

    def __init__(self, x: float, y: float):
        self.x = float(x)
        self.y = float(y)

    def __add__(self, other: "Vec2D") -> "Vec2D":
        return Vec2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vec2D") -> "Vec2D":
        return Vec2D(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> "Vec2D":
        return Vec2D(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: float) -> "Vec2D":
        return Vec2D(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar: float) -> "Vec2D":
        if scalar == 0:
            raise ZeroDivisionError("Division by zero in Vec2D.")
        return Vec2D(self.x / scalar, self.y / scalar)

    def dot(self, other: "Vec2D") -> float:
        return self.x * other.x + self.y * other.y

    def cross(self, other: "Vec2D") -> float:
        """2D scalar cross product (z-component)."""
        return self.x * other.y - self.y * other.x

    def length(self) -> float:
        return math.hypot(self.x, self.y)

    def normalized(self) -> "Vec2D":
        l = self.length()
        if l == 0.0:
            return Vec2D(0.0, 0.0)
        return Vec2D(self.x / l, self.y / l)

    def perpendicular(self) -> "Vec2D":
        """Return 90-degree counter-clockwise normal vector."""
        return Vec2D(-self.y, self.x)

    def rotate(self, angle_rad: float) -> "Vec2D":
        c = math.cos(angle_rad)
        s = math.sin(angle_rad)
        return Vec2D(self.x * c - self.y * s, self.x * s + self.y * c)

    def distance_to(self, other: "Vec2D") -> float:
        return math.hypot(self.x - other.x, self.y - other.y)

    def to_tuple(self) -> Tuple[float, float]:
        return (round(self.x, 4), round(self.y, 4))

    def __repr__(self) -> str:
        return f"Vec2D({self.x:.3f}, {self.y:.3f})"


class CubicBezier:
    """
    Parametric Cubic Bézier Curve:
    B(t) = (1-t)^3 P0 + 3(1-t)^2 t P1 + 3(1-t) t^2 P2 + t^3 P3  for t in [0, 1].
    Includes velocity, normal, curvature, 5-point Gauss-Legendre arc length, and De Casteljau subdivision.
    """
    # 5-point Gauss-Legendre Quadrature abscissas and weights on [-1, 1]
    GAUSS_X = [
        0.0,
        -math.sqrt(5.0 - 2.0 * math.sqrt(10.0 / 7.0)) / 3.0,
        math.sqrt(5.0 - 2.0 * math.sqrt(10.0 / 7.0)) / 3.0,
        -math.sqrt(5.0 + 2.0 * math.sqrt(10.0 / 7.0)) / 3.0,
        math.sqrt(5.0 + 2.0 * math.sqrt(10.0 / 7.0)) / 3.0
    ]
    GAUSS_W = [
        128.0 / 225.0,
        (322.0 + 13.0 * math.sqrt(70.0)) / 900.0,
        (322.0 + 13.0 * math.sqrt(70.0)) / 900.0,
        (322.0 - 13.0 * math.sqrt(70.0)) / 900.0,
        (322.0 - 13.0 * math.sqrt(70.0)) / 900.0
    ]

    def __init__(self, p0: Vec2D, p1: Vec2D, p2: Vec2D, p3: Vec2D):
        self.p0 = p0
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3

    def eval(self, t: float) -> Vec2D:
        """Evaluate point at parameter t in [0, 1]."""
        t = max(0.0, min(1.0, t))
        mt = 1.0 - t
        mt2 = mt * mt
        mt3 = mt2 * mt
        t2 = t * t
        t3 = t2 * t
        return (mt3 * self.p0) + (3.0 * mt2 * t * self.p1) + (3.0 * mt * t2 * self.p2) + (t3 * self.p3)

    def velocity(self, t: float) -> Vec2D:
        """Evaluate first derivative B'(t) at parameter t."""
        t = max(0.0, min(1.0, t))
        mt = 1.0 - t
        return 3.0 * (mt * mt * (self.p1 - self.p0) + 2.0 * mt * t * (self.p2 - self.p1) + t * t * (self.p3 - self.p2))

    def acceleration(self, t: float) -> Vec2D:
        """Evaluate second derivative B''(t) at parameter t."""
        t = max(0.0, min(1.0, t))
        mt = 1.0 - t
        return 6.0 * (mt * (self.p2 - 2.0 * self.p1 + self.p0) + t * (self.p3 - 2.0 * self.p2 + self.p1))

    def tangent(self, t: float) -> Vec2D:
        """Unit tangent vector at parameter t."""
        return self.velocity(t).normalized()

    def normal(self, t: float) -> Vec2D:
        """Unit normal vector perpendicular to tangent at parameter t."""
        return self.tangent(t).perpendicular()

    def curvature(self, t: float) -> float:
        """
        Calculate signed curvature kappa(t) = (x' y'' - y' x'') / (x'^2 + y'^2)^(3/2).
        """
        v = self.velocity(t)
        a = self.acceleration(t)
        denom = (v.x * v.x + v.y * v.y) ** 1.5
        if denom < 1e-12:
            return 0.0
        return (v.x * a.y - v.y * a.x) / denom

    def arc_length(self, num_segments: int = 4) -> float:
        """
        Calculate high-precision arc length using composite 5-point Gauss-Legendre quadrature.
        """
        total_len = 0.0
        dt = 1.0 / num_segments
        for i in range(num_segments):
            t_start = i * dt
            t_end = (i + 1) * dt
            sub_len = 0.0
            for x_k, w_k in zip(self.GAUSS_X, self.GAUSS_W):
                t = t_start + 0.5 * (x_k + 1.0) * dt
                speed = self.velocity(t).length()
                sub_len += w_k * speed
            total_len += sub_len * 0.5 * dt
        return round(total_len, 6)

    def split(self, t: float = 0.5) -> Tuple["CubicBezier", "CubicBezier"]:
        """
        Split cubic Bézier into two curves at parameter t using De Casteljau's algorithm.
        """
        t = max(0.0, min(1.0, t))
        p01 = self.p0 + t * (self.p1 - self.p0)
        p12 = self.p1 + t * (self.p2 - self.p1)
        p23 = self.p2 + t * (self.p3 - self.p2)

        p012 = p01 + t * (p12 - p01)
        p123 = p12 + t * (p23 - p12)

        p0123 = p012 + t * (p123 - p012)

        left = CubicBezier(self.p0, p01, p012, p0123)
        right = CubicBezier(p0123, p123, p23, self.p3)
        return (left, right)

    def bounding_box(self) -> Tuple[float, float, float, float]:
        """
        Compute tight axis-aligned bounding box (min_x, min_y, max_x, max_y)
        considering endpoints and derivative root extrema.
        """
        x_pts = [self.p0.x, self.p3.x]
        y_pts = [self.p0.y, self.p3.y]

        # Solve for roots of B'(t).x = a t^2 + b t + c = 0
        def solve_extrema(p0: float, p1: float, p2: float, p3: float) -> List[float]:
            a = 3.0 * (-p0 + 3.0 * p1 - 3.0 * p2 + p3)
            b = 6.0 * (p0 - 2.0 * p1 + p2)
            c = 3.0 * (p1 - p0)
            roots = []
            if abs(a) < 1e-12:
                if abs(b) > 1e-12:
                    t = -c / b
                    if 0.0 < t < 1.0:
                        roots.append(t)
            else:
                disc = b * b - 4.0 * a * c
                if disc >= 0.0:
                    sq = math.sqrt(disc)
                    t1 = (-b + sq) / (2.0 * a)
                    t2 = (-b - sq) / (2.0 * a)
                    for t in (t1, t2):
                        if 0.0 < t < 1.0:
                            roots.append(t)
            return roots

        for t in solve_extrema(self.p0.x, self.p1.x, self.p2.x, self.p3.x):
            x_pts.append(self.eval(t).x)

        for t in solve_extrema(self.p0.y, self.p1.y, self.p2.y, self.p3.y):
            y_pts.append(self.eval(t).y)

        return (min(x_pts), min(y_pts), max(x_pts), max(y_pts))

    def to_svg_path_segment(self) -> str:
        """Format as SVG cubic Bézier command segment 'C p1.x p1.y, p2.x p2.y, p3.x p3.y'."""
        return f"C {self.p1.x:.2f} {self.p1.y:.2f}, {self.p2.x:.2f} {self.p2.y:.2f}, {self.p3.x:.2f} {self.p3.y:.2f}"


# ============================================================================
# 3. PROCEDURAL 24PX GRID ICON BUILDER (LUCIDE / PENPOT STANDARD)
# ============================================================================

class IconBuilder24:
    """
    Standardized 24x24 pixel grid SVG icon generator.
    Adheres to Lucide and Penpot design systems:
    - 24x24 viewBox with 2px stroke width
    - Round linecaps and round linejoins
    - Optical weight centering and pixel grid snapping
    """
    @staticmethod
    def _wrap_svg(paths_svg: str, title: str = "Icon") -> str:
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" '
            f'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">\n'
            f'  <title>{title}</title>\n'
            f'  {paths_svg}\n'
            f'</svg>'
        )

    @classmethod
    def shield_check(cls) -> str:
        """Security verified shield icon."""
        paths = (
            '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>\n'
            '  <path d="m9 12 2 2 4-4"/>'
        )
        return cls._wrap_svg(paths, "Shield Check")

    @classmethod
    def cpu_neural(cls) -> str:
        """High-performance CPU chip icon."""
        paths = (
            '<rect width="16" height="16" x="4" y="4" rx="2"/>\n'
            '  <rect width="6" height="6" x="9" y="9" rx="1"/>\n'
            '  <path d="M9 1v3M15 1v3M9 20v3M15 20v3M20 9h3M20 15h3M1 9h3M1 15h3"/>'
        )
        return cls._wrap_svg(paths, "CPU Neural")

    @classmethod
    def palette_vector(cls) -> str:
        """Vector color palette & bezier icon."""
        paths = (
            '<circle cx="13.5" cy="6.5" r=".5" fill="currentColor"/>\n'
            '  <circle cx="17.5" cy="10.5" r=".5" fill="currentColor"/>\n'
            '  <circle cx="8.5" cy="7.5" r=".5" fill="currentColor"/>\n'
            '  <circle cx="6.5" cy="12.5" r=".5" fill="currentColor"/>\n'
            '  <path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.926 0 1.648-.746 1.648-1.688 0-.437-.18-.835-.437-1.125-.29-.289-.438-.652-.438-1.125a1.64 1.64 0 0 1 1.668-1.668h1.996c3.051 0 5.563-2.512 5.563-5.563C22 6.5 17.5 2 12 2z"/>'
        )
        return cls._wrap_svg(paths, "Vector Palette")

    @classmethod
    def generative_sparkle(cls) -> str:
        """Generative AI sparkle & dynamic visual engine icon."""
        paths = (
            '<path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3Z"/>\n'
            '  <path d="M5 3v4M3 5h4M19 17v4M17 19h4"/>'
        )
        return cls._wrap_svg(paths, "Generative Sparkle")


# ============================================================================
# 4. GENERATIVE GEOMETRIC POSTER & VECTOR ARTWORK BUILDER
# ============================================================================

class GenerativePoster:
    """
    Algorithmic generative poster generator synthesizing:
    - Parametric Lissajous & Rose curves
    - Harmonious WCAG-compliant color palettes (CIELCh)
    - Golden-ratio grid composition & typography hierarchy
    """
    def __init__(self, width: int = 800, height: int = 1200, title: str = "AUTONOMOUS SYNTHESIS"):
        self.width = width
        self.height = height
        self.title = title

    def build_svg(self, base_color: Color = Color(18, 52, 86)) -> str:
        """
        Generate full SVG graphic poster with mathematical curves and layered depth.
        """
        # Create WCAG-compliant harmonious palette
        bg_dark = Color(10, 15, 26)
        comp_primary, comp_accent = PaletteGenerator.complementary(base_color)
        triad1, triad2, triad3 = PaletteGenerator.triadic(base_color)
        
        # Ensure high contrast text
        text_color = Color(245, 247, 250)
        assert text_color.contrast_ratio(bg_dark) >= 7.0, "Poster header must meet WCAG AAA"

        center_x = self.width / 2.0
        center_y = self.height * 0.48
        radius = min(self.width, self.height) * 0.32

        # 1. Generate Parametric 3D Lissajous & Harmonious Wave Mesh
        curves_svg = []
        steps = 180
        num_layers = 16

        for k in range(num_layers):
            fraction = k / float(num_layers)
            layer_color = triad1.lerp(triad2, fraction)
            opacity = 0.35 + 0.45 * math.sin(fraction * math.pi)
            
            # Parametric Lissajous trajectory: x = R*sin(a*t + d), y = R*cos(b*t)
            points = []
            a_freq = 3.0
            b_freq = 2.0
            phase = fraction * math.pi * 2.0

            for i in range(steps + 1):
                theta = (i / float(steps)) * math.pi * 2.0
                r_mod = radius * (0.65 + 0.35 * math.cos(3.0 * theta + phase))
                px = center_x + r_mod * math.sin(a_freq * theta + phase)
                py = center_y + r_mod * math.cos(b_freq * theta)
                points.append(f"{px:.2f},{py:.2f}")

            polyline_str = " ".join(points)
            curves_svg.append(
                f'  <polyline points="{polyline_str}" fill="none" stroke="{layer_color.to_hex()}" '
                f'stroke-width="1.8" stroke-opacity="{opacity:.3f}" stroke-linecap="round"/>'
            )

        # 2. Smooth Cubic Bézier Arc Ornaments
        bezier_svg = []
        for i in range(6):
            ang = (i / 6.0) * math.pi * 2.0
            p0 = Vec2D(center_x, center_y)
            p1 = p0 + Vec2D(radius * 0.5 * math.cos(ang), radius * 0.5 * math.sin(ang))
            p2 = p0 + Vec2D(radius * 1.1 * math.cos(ang + 0.8), radius * 1.1 * math.sin(ang + 0.8))
            p3 = p0 + Vec2D(radius * 1.3 * math.cos(ang + 1.6), radius * 1.3 * math.sin(ang + 1.6))
            bez = CubicBezier(p0, p1, p2, p3)
            
            p_start = bez.p0
            bez_path = f"M {p_start.x:.2f} {p_start.y:.2f} {bez.to_svg_path_segment()}"
            bezier_svg.append(
                f'  <path d="{bez_path}" fill="none" stroke="{triad3.to_hex()}" stroke-width="2.5" '
                f'stroke-opacity="0.75" stroke-dasharray="8 4"/>'
            )

        # 3. Combine SVG Assembly
        svg_content = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" height="{self.height}" viewBox="0 0 {self.width} {self.height}">',
            '  <defs>',
            f'    <radialGradient id="bgGrad" cx="50%" cy="45%" r="65%">',
            f'      <stop offset="0%" stop-color="#141E30" />',
            f'      <stop offset="100%" stop-color="{bg_dark.to_hex()}" />',
            '    </radialGradient>',
            f'    <linearGradient id="textGrad" x1="0%" y1="0%" x2="100%" y2="0%">',
            f'      <stop offset="0%" stop-color="{triad1.to_hex()}" />',
            f'      <stop offset="100%" stop-color="{triad3.to_hex()}" />',
            '    </linearGradient>',
            '  </defs>',
            '',
            f'  <!-- Background Canvas -->',
            f'  <rect width="{self.width}" height="{self.height}" fill="url(#bgGrad)" />',
            '',
            f'  <!-- Geometric Precision Grid -->',
            f'  <circle cx="{center_x}" cy="{center_y}" r="{radius * 1.25:.1f}" fill="none" stroke="#2A3B55" stroke-width="1" stroke-dasharray="4 8"/>',
            f'  <circle cx="{center_x}" cy="{center_y}" r="{radius * 0.75:.1f}" fill="none" stroke="#2A3B55" stroke-width="1"/>',
            f'  <line x1="{center_x}" y1="{center_y - radius * 1.35}" x2="{center_x}" y2="{center_y + radius * 1.35}" stroke="#2A3B55" stroke-width="1" stroke-dasharray="3 6"/>',
            f'  <line x1="{center_x - radius * 1.35}" y1="{center_y}" x2="{center_x + radius * 1.35}" y2="{center_y}" stroke="#2A3B55" stroke-width="1" stroke-dasharray="3 6"/>',
            '',
            f'  <!-- Parametric Lissajous Waves -->',
            "\n".join(curves_svg),
            '',
            f'  <!-- Cubic Bézier Orbits -->',
            "\n".join(bezier_svg),
            '',
            f'  <!-- Typography & Layout Hierarchy -->',
            f'  <text x="60" y="90" font-family="system-ui, -apple-system, sans-serif" font-size="14" font-weight="700" fill="{triad1.to_hex()}" letter-spacing="4">NEURAL DESIGN LAB</text>',
            f'  <text x="60" y="115" font-family="system-ui, -apple-system, sans-serif" font-size="11" font-weight="400" fill="#718096" letter-spacing="2">SERIES 055 // GENERATIVE ALGORITHMS</text>',
            f'  <text x="60" y="{self.height - 110}" font-family="system-ui, -apple-system, sans-serif" font-size="42" font-weight="900" fill="url(#textGrad)" letter-spacing="2">{self.title}</text>',
            f'  <text x="60" y="{self.height - 75}" font-family="system-ui, -apple-system, sans-serif" font-size="14" font-weight="400" fill="{text_color.to_hex()}" letter-spacing="1">PARAMETRIC CURVES • CIELAB COLOR DYNAMICS • WCAG 2.2 AAA COMPLIANT</text>',
            f'  <text x="{self.width - 60}" y="{self.height - 75}" text-anchor="end" font-family="monospace" font-size="12" fill="#718096">24PX ICON GRID // PENPOT SVG BOX-MODEL</text>',
            '</svg>'
        ]
        return "\n".join(svg_content)


# ============================================================================
# 5. DETERMINISTIC VERIFICATION & ASSERTION SUITE
# ============================================================================

def run_self_tests() -> bool:
    """
    Execute 100% deterministic test suite covering color math, WCAG contrast,
    Bézier arc length, De Casteljau subdivision, and SVG generator integrity.
    """
    print("=" * 70)
    print("🎨 RUNNING GRAPHIC DESIGN & VISUAL ENGINEERING SELF-TESTS")
    print("=" * 70)

    # 1. Color Hex & HSL Roundtrip
    c_white = Color.from_hex("#FFFFFF")
    c_black = Color.from_hex("#000000")
    c_blue = Color.from_hex("#0055FF")
    assert c_white.r == 255 and c_white.g == 255 and c_white.b == 255
    assert c_black.r == 0 and c_black.g == 0 and c_black.b == 0
    assert c_blue.to_hex() == "#0055FF"
    print("  [✓] Hex parsing and formatting validated.")

    # 2. WCAG 2.2 Relative Luminance & Contrast Ratios
    lum_white = c_white.relative_luminance()
    lum_black = c_black.relative_luminance()
    assert abs(lum_white - 1.0) < 1e-4, f"White luminance expected 1.0, got {lum_white}"
    assert abs(lum_black - 0.0) < 1e-4, f"Black luminance expected 0.0, got {lum_black}"

    cr_wb = c_white.contrast_ratio(c_black)
    assert abs(cr_wb - 21.0) < 0.01, f"Expected 21:1 contrast ratio for Black/White, got {cr_wb}"
    
    wcag_wb = c_white.wcag_compliance(c_black)
    assert wcag_wb["aa_normal"] and wcag_wb["aaa_normal"], "Black on white must pass WCAG AAA"
    print(f"  [✓] WCAG 2.2 Luminance & Max Contrast validated: {cr_wb}:1 (AAA Passed).")

    # 3. CIELAB & CIELCh Conversions
    lab_white = c_white.to_lab()
    assert abs(lab_white[0] - 100.0) < 0.1, f"White L* should be ~100, got {lab_white[0]}"
    
    lab_black = c_black.to_lab()
    assert abs(lab_black[0] - 0.0) < 0.1, f"Black L* should be ~0, got {lab_black[0]}"

    # Color reconstruction from LAB
    rebuilt_blue = Color.from_lab(*c_blue.to_lab())
    assert max(abs(rebuilt_blue.r - c_blue.r), abs(rebuilt_blue.g - c_blue.g), abs(rebuilt_blue.b - c_blue.b)) <= 2, \
        f"LAB roundtrip error exceeds tolerance: {rebuilt_blue} vs {c_blue}"
    print("  [✓] CIE XYZ / CIELAB / CIELCh perceptually uniform color space validated.")

    # 4. Color Palette Generation
    mono = PaletteGenerator.monochromatic(c_blue, count=5)
    assert len(mono) == 5, f"Expected 5 monochromatic shades, got {len(mono)}"
    
    comp1, comp2 = PaletteGenerator.complementary(c_blue)
    h1, _, _ = comp1.to_hsl()
    h2, _, _ = comp2.to_hsl()
    hue_diff = abs(h1 - h2)
    assert abs(hue_diff - 180.0) < 0.1, f"Complementary hue diff expected 180, got {hue_diff}"

    triad = PaletteGenerator.triadic(c_blue)
    assert len(triad) == 3
    t_h0, _, _ = triad[0].to_hsl()
    t_h1, _, _ = triad[1].to_hsl()
    t_h2, _, _ = triad[2].to_hsl()
    assert abs((t_h1 - t_h0) % 360.0 - 120.0) < 0.1
    assert abs((t_h2 - t_h0) % 360.0 - 240.0) < 0.1

    grad_scale = PaletteGenerator.scale([c_white, c_blue, c_black], steps=7)
    assert len(grad_scale) == 7
    print("  [✓] Harmonic palette generator (Monochromatic, Complementary, Triadic, Gradient Scale) validated.")

    # 5. 2D Vector Operations
    v1 = Vec2D(3.0, 4.0)
    assert abs(v1.length() - 5.0) < 1e-6
    v_norm = v1.normalized()
    assert abs(v_norm.length() - 1.0) < 1e-6
    v_rot = v1.rotate(math.pi / 2.0)
    assert abs(v1.dot(v_rot)) < 1e-6, "90-degree rotated vector must be orthogonal (dot product = 0)"
    print("  [✓] 2D Vector algebra & rotation verified.")

    # 6. Cubic Bézier Math & Arc Length
    p0 = Vec2D(0.0, 0.0)
    p1 = Vec2D(33.3333, 0.0)
    p2 = Vec2D(66.6667, 0.0)
    p3 = Vec2D(100.0, 0.0)
    line_bez = CubicBezier(p0, p1, p2, p3)
    
    # Endpoint and midpoint checks
    assert line_bez.eval(0.0).distance_to(p0) < 1e-4
    assert line_bez.eval(1.0).distance_to(p3) < 1e-4
    assert line_bez.eval(0.5).distance_to(Vec2D(50.0, 0.0)) < 1e-4
    
    # Arc length calculation
    straight_len = line_bez.arc_length()
    assert abs(straight_len - 100.0) < 0.01, f"Straight cubic bezier length expected 100.0, got {straight_len}"

    # Curved cubic bezier
    curved_bez = CubicBezier(Vec2D(0, 0), Vec2D(0, 50), Vec2D(100, 50), Vec2D(100, 0))
    curved_len = curved_bez.arc_length()
    assert curved_len > 100.0, f"Curved path length must be > chord length (100.0), got {curved_len}"

    # De Casteljau Subdivision
    left_bez, right_bez = curved_bez.split(0.5)
    assert left_bez.eval(1.0).distance_to(right_bez.eval(0.0)) < 1e-4, "Subdivided curves must meet continuously at midpoint"
    sub_combined_len = left_bez.arc_length() + right_bez.arc_length()
    assert abs(sub_combined_len - curved_len) < 0.05, f"Subdivided sum ({sub_combined_len}) must equal total length ({curved_len})"
    print(f"  [✓] Cubic Bézier & Gauss-Legendre Arc Length ({curved_len:.4f}px) & De Casteljau subdivision verified.")

    # 7. Procedural 24px Icon Builder
    shield_svg = IconBuilder24.shield_check()
    assert 'viewBox="0 0 24 24"' in shield_svg
    assert 'stroke-width="2"' in shield_svg
    assert '<svg' in shield_svg and '</svg>' in shield_svg

    cpu_svg = IconBuilder24.cpu_neural()
    assert 'rect width="16" height="16"' in cpu_svg
    print("  [✓] 24px Grid procedural icon builder (Lucide / Penpot standard) validated.")

    # 8. Generative Poster Synthesis
    poster_engine = GenerativePoster(width=600, height=900, title="VISUAL SYNTHESIS")
    poster_svg = poster_engine.build_svg(base_color=Color(20, 90, 160))
    assert '<svg xmlns="http://www.w3.org/2000/svg"' in poster_svg
    assert 'VISUAL SYNTHESIS' in poster_svg
    assert 'NEURAL DESIGN LAB' in poster_svg
    assert '</svg>' in poster_svg
    print("  [✓] Algorithmic generative poster builder produced valid SVG artwork.")

    print("=" * 70)
    print("✨ ALL GRAPHIC DESIGN & VISUAL ENGINEERING ASSERTIONS PASSED (100%)")
    print("=" * 70)
    return True


if __name__ == "__main__":
    success = run_self_tests()
    if not success:
        sys.exit(1)
