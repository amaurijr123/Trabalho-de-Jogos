"""Geometria da bola e dos obstáculos; independente do Pygame."""

import math


def point_in_polygon(point, vertices):
    x, y = point
    inside = False
    for a, b in zip(vertices, vertices[1:] + vertices[:1]):
        if (a[1] > y) != (b[1] > y):
            crossing = a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1])
            if x < crossing:
                inside = not inside
    return inside


def entered_region(previous, current, vertices):
    return not point_in_polygon(previous, vertices) and point_in_polygon(current, vertices)


def circle_polygon_contact(center, radius, vertices):
    """Retorna normal de separação e profundidade para um círculo e polígono."""
    closest = None
    best_d2 = float('inf')
    for a, b in zip(vertices, vertices[1:] + vertices[:1]):
        dx, dy = b[0] - a[0], b[1] - a[1]
        length2 = dx * dx + dy * dy
        t = max(0.0, min(1.0, ((center[0] - a[0]) * dx + (center[1] - a[1]) * dy) / length2))
        point = (a[0] + t * dx, a[1] + t * dy)
        d2 = (center[0] - point[0]) ** 2 + (center[1] - point[1]) ** 2
        if d2 < best_d2:
            best_d2, closest = d2, point

    inside = point_in_polygon(center, vertices)
    distance = math.sqrt(best_d2)
    if not inside and distance >= radius:
        return None
    if distance < 1e-9:
        # Centro exatamente sobre a borda: direção do centro do polígono para a bola.
        cx = sum(p[0] for p in vertices) / len(vertices)
        cy = sum(p[1] for p in vertices) / len(vertices)
        vx, vy = center[0] - cx, center[1] - cy
        size = math.hypot(vx, vy) or 1
        normal = (vx / size, vy / size)
    else:
        sign = -1 if inside else 1
        normal = (sign * (center[0] - closest[0]) / distance,
                  sign * (center[1] - closest[1]) / distance)
    return normal, radius + distance if inside else radius - distance


def reflect(velocity, normal):
    dot = velocity[0] * normal[0] + velocity[1] * normal[1]
    if dot >= 0:
        return velocity
    return (velocity[0] - 2 * dot * normal[0],
            velocity[1] - 2 * dot * normal[1])
