import math
import turtle
from dataclasses import dataclass

@dataclass(frozen=True)
class Vec:
    x: float
    y: float
    def __add__(self, o): return Vec(self.x + o.x, self.y + o.y)
    def __sub__(self, o): return Vec(self.x - o.x, self.y - o.y)
    def __mul__(self, k: float): return Vec(self.x * k, self.y * k)

def rot(v: Vec, c: float, s: float) -> Vec:
    # rotate by angle with precomputed cos/sin
    return Vec(v.x * c - v.y * s, v.x * s + v.y * c)

def draw_poly(t: turtle.Turtle, pts: list[Vec]) -> None:
    t.penup()
    t.goto(pts[0].x, pts[0].y)
    t.pendown()
    for p in pts[1:]:
        t.goto(p.x, p.y)
    t.goto(pts[0].x, pts[0].y)

def pythagoras(t: turtle.Turtle, base_a: Vec, base_b: Vec, depth: int, c: float, s: float, min_size: float = 2.0) -> None:
    # base_a -> base_b is bottom side of square
    v = base_b - base_a
    size = math.hypot(v.x, v.y)
    if depth <= 0 or size < min_size:
        return

    # square points: a, b, c, d
    # perpendicular vector (rotate by +90): (-vy, vx)
    perp = Vec(-v.y, v.x)
    c1 = base_b + perp
    d1 = base_a + perp
    draw_poly(t, [base_a, base_b, c1, d1])

    # top edge: d1 -> c1
    top_v = c1 - d1  # same as v

    # For Pythagoras tree: build two squares on top edge, rotated by angle
    # Compute split point 'p' on top edge based on angle (classic construction)
    # left branch vector = rotate(top_v, -angle) scaled by cos(angle)
    # right branch vector = rotate(top_v, + (90-angle)) scaled by sin(angle) ... but easier:
    # We'll use a known vector construction:
    # Let u = top_v
    # left_u = rot(u, c, s) * c   (scale = cos)
    # right_u = rot(u, -s, c) * s  (rotate by (90 - angle)) and scale by sin
    # This yields a nice symmetric tree for 45°.
    left_u = rot(top_v, c, s) * c
    # right_u = rot(top_v, -s, c) * s

    p = d1 + left_u  # meeting point on the "roof"

    # Left square on segment d1 -> p
    pythagoras(t, d1, p, depth - 1, c, s, min_size)

    # Right square on segment p -> c1
    pythagoras(t, p, c1, depth - 1, c, s, min_size)

def main():
    level = int(input("Введіть рівень рекурсії (наприклад 10): ").strip() or "10")

    # default 45°
    angle = math.radians(45)
    c, s = math.cos(angle), math.sin(angle)

    screen = turtle.Screen()
    screen.title("Дерево Піфагора (45°)")
    screen.setup(width=900, height=600)
    screen.tracer(0, 0)

    t = turtle.Turtle(visible=False)
    t.speed(0)
    t.pensize(1)

    # стартовий квадрат (нижня сторона)
    size = 140
    a = Vec(-size/2, -270)
    b = Vec(size/2, -270)

    pythagoras(t, a, b, level, c, s, min_size=1.5)

    screen.update()
    turtle.done()

if __name__ == "__main__":
    main()
