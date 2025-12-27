from __future__ import annotations

import math
import turtle
from dataclasses import dataclass


@dataclass(frozen=True)
class Vec:
    x: float
    y: float

    def __add__(self, other: "Vec") -> "Vec":
        return Vec(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vec") -> "Vec":
        return Vec(self.x - other.x, self.y - other.y)

    def __mul__(self, k: float) -> "Vec":
        return Vec(self.x * k, self.y * k)

    def length(self) -> float:
        return math.hypot(self.x, self.y)


def rotate(v: Vec, cos_a: float, sin_a: float) -> Vec:
    """Поворот вектора v на кут, заданий cos/sin."""
    return Vec(v.x * cos_a - v.y * sin_a, v.x * sin_a + v.y * cos_a)


def draw_poly(t: turtle.Turtle, pts: list[Vec]) -> None:
    """Намалювати замкнений багатокутник."""
    t.penup()
    t.goto(pts[0].x, pts[0].y)
    t.pendown()
    for p in pts[1:]:
        t.goto(p.x, p.y)
    t.goto(pts[0].x, pts[0].y)


def draw_segment(t: turtle.Turtle, a: Vec, b: Vec) -> None:
    """Намалювати відрізок між двома точками."""
    t.penup()
    t.goto(a.x, a.y)
    t.pendown()
    t.goto(b.x, b.y)


def pythagoras_tree(
    t: turtle.Turtle,
    a: Vec,
    b: Vec,
    depth: int,
    cos45: float,
    sin45: float,
    min_size: float,
    bare: bool,
) -> None:
    if depth <= 0:
        return

    v = b - a
    size = v.length()
    if size < min_size:
        return

    # Перпендикуляр до основи (поворот на +90°)
    perp = Vec(-v.y, v.x)

    # Вершини квадрату (якщо він потрібен)
    c = b + perp
    d = a + perp

    # Точка вершини "даху" (для 45°)
    top = c - d
    p = d + rotate(top, cos45, sin45) * cos45

    if bare:
        # ОГОЛЕНЕ ДЕРЕВО:
        # Малюємо лише "Y"-подібні гілки:
        # 1) стовбур: середина основи -> середина верху
        mid_base = Vec((a.x + b.x) / 2, (a.y + b.y) / 2)
        mid_top  = Vec((d.x + c.x) / 2, (d.y + c.y) / 2)
        draw_segment(t, mid_base, mid_top)

        # 2) дві гілки: з вершини "даху" до країв верхньої сторони
        #draw_segment(t, d, p)
        #draw_segment(t, p, c)

    else:
        # ЗВИЧАЙНЕ ДЕРЕВО:
        # Малюємо квадрат повністю
        draw_poly(t, [a, b, c, d])

    # Рекурсія (ВАЖЛИВО: bare прокидуємо далі)
    pythagoras_tree(t, d, p, depth - 1, cos45, sin45, min_size, bare)
    pythagoras_tree(t, p, c, depth - 1, cos45, sin45, min_size, bare)


def main() -> None:
    level_str = input("Рівень рекурсії (наприклад 10): ").strip() or "10"
    level = int(level_str)

    bare_str = input("Оголене дерево? (y/n): ").strip().lower()
    bare = (bare_str == "y")

    angle = math.radians(45)
    cos45, sin45 = math.cos(angle), math.sin(angle)

    screen = turtle.Screen()
    screen.title("Дерево Піфагора (оголене)" if bare else "Дерево Піфагора (квадрати)")
    screen.setup(width=1000, height=700)
    screen.tracer(0, 0)  # швидше малювання (оновимо вручну)

    t = turtle.Turtle(visible=False)
    t.speed(0)
    t.pensize(2)

    # Центрування: стартова основа по центру внизу
    base_size = 180
    y = -280
    a = Vec(-base_size / 2, y)
    b = Vec(base_size / 2, y)

    pythagoras_tree(
        t=t,
        a=a,
        b=b,
        depth=level,
        cos45=cos45,
        sin45=sin45,
        min_size=3.0,
        bare=bare,
    )

    screen.update()
    turtle.done()


if __name__ == "__main__":
    main()
