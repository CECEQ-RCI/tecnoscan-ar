"""Plantilla del cubo (a+b)³: cada cara muestra las piezas que se ven desde ese lado.

Uso:  python generar_formula.py [lado_cm]

Sobrescribe caras/cara1..6.png (hay que volver a compilar targets.mind) y crea
plantilla_formula.png / .pdf. Al doblar la plantilla, los colores de las caras
coinciden con el cubo armado de la animación.

Orientación de cada cara al doblar la cruz (u = derecha de la imagen, v = arriba,
n = hacia afuera), en coordenadas del cubo: x derecha, y arriba, z hacia el frente.
El lado "a" de cada eje está en las coordenadas negativas. Debe coincidir con
BASES_CARAS en contenido.js.
"""
import random

from PIL import Image, ImageDraw

from generar_patrones import BASE, CARAS, TAM, fuente, plantilla

A, B = 0.6, 0.4
X, Y, Z = (1, 0, 0), (0, 1, 0), (0, 0, 1)
neg = lambda v: tuple(-c for c in v)
BASES = {   # cara: (u, v, n)
    1: (X, neg(Z), Y),        # arriba
    2: (Z, Y, neg(X)),        # izquierda
    3: (X, Y, Z),             # frente
    4: (neg(Z), Y, X),        # derecha
    5: (X, Z, neg(Y)),        # abajo
    6: (X, neg(Y), neg(Z)),   # atrás
}
COLORES = {3: (230, 57, 70), 2: (69, 123, 157), 1: (42, 157, 143), 0: (244, 162, 97)}  # por cantidad de "a"
NOMBRES = {3: "a³", 2: "a²b", 1: "ab²", 0: "b³"}
FORMULA = "(a+b)³ = a³ + 3a²b + 3ab² + b³"


def tramos(eje):
    """Divide [-0.5, 0.5] de la imagen en los tramos a/b según hacia dónde apunta el eje."""
    signo = sum(eje)
    corte = -0.5 + A if signo > 0 else 0.5 - A
    izq, der = ("a", "b") if signo > 0 else ("b", "a")
    return [(-0.5, corte, izq), (corte, 0.5, der)]


def mezclar(c, otro, t):
    return tuple(round(a + (b - a) * t) for a, b in zip(c, otro))


def cara(n):
    u, v, nrm = BASES[n]
    letra_normal = "b" if sum(nrm) > 0 else "a"
    rnd = random.Random(500 + n)
    img = Image.new("RGB", (TAM, TAM), "white")
    d = ImageDraw.Draw(img)
    px = lambda s: round((s + 0.5) * TAM)          # s de la imagen -> píxel x
    py = lambda t: round((0.5 - t) * TAM)          # t de la imagen -> píxel y
    regiones = []
    for s0, s1, ls in tramos(u):
        for t0, t1, lt in tramos(v):
            nA = [ls, lt, letra_normal].count("a")
            caja = (px(s0), py(t1), px(s1), py(t0))
            d.rectangle(caja, fill=COLORES[nA])
            regiones.append((caja, nA))
    # Textura con muchas esquinas para el rastreo, en tonos de cada pieza
    for (x0, y0, x1, y1), nA in regiones:
        base = COLORES[nA]
        tonos = [mezclar(base, (0, 0, 0), 0.45), mezclar(base, (255, 255, 255), 0.45), (255, 255, 255), (20, 20, 20)]
        for _ in range(int(320 * (x1 - x0) * (y1 - y0) / TAM ** 2) + 40):
            c = rnd.choice(tonos)
            x, y, s = rnd.randint(x0, x1), rnd.randint(y0, y1), rnd.randint(18, 80)
            k = rnd.random()
            if k < 0.45:
                d.polygon([(x + rnd.randint(-s, s), y + rnd.randint(-s, s)) for _ in range(3)], fill=c)
            elif k < 0.75:
                d.ellipse([x, y, x + s, y + s], outline=c, width=rnd.randint(4, 9))
            else:
                d.line([x, y, x + rnd.randint(-2 * s, 2 * s), y + rnd.randint(-2 * s, 2 * s)], fill=c, width=rnd.randint(4, 10))
    # Nombre de cada pieza, en un lugar distinto en cada cara para que no se parezcan entre sí.
    # (Sin bordes negros ni marco: dan las mismas esquinas en todas las caras y MindAR las confunde.)
    for (x0, y0, x1, y1), nA in regiones:
        tam = (150 if min(x1 - x0, y1 - y0) > 450 else 110) + rnd.randint(-15, 15)
        cx = (x0 + x1) / 2 + rnd.uniform(-0.18, 0.18) * (x1 - x0)
        cy = (y0 + y1) / 2 + rnd.uniform(-0.18, 0.18) * (y1 - y0)
        d.text((cx, cy), NOMBRES[nA], font=fuente(tam), anchor="mm",
               fill="white", stroke_width=10, stroke_fill=(17, 17, 17))
    # Medidas a y b en el borde inferior y en el izquierdo
    f = fuente(64)
    for s0, s1, l in tramos(u):
        d.text(((px(s0) + px(s1)) / 2, TAM - 70), l, font=f, anchor="mm", fill="black",
               stroke_width=8, stroke_fill="white")
    for t0, t1, l in tramos(v):
        d.text((70, (py(t0) + py(t1)) / 2), l, font=f, anchor="mm", fill="black",
               stroke_width=8, stroke_fill="white")
    # Fórmula solo en la cara 1: si se repite en todas, MindAR confunde las caras entre sí
    if n == 1:
        formula(d)
    d.text((TAM - 60, TAM - 60), str(n), font=fuente(48), anchor="mm", fill="black",
           stroke_width=6, stroke_fill="white")
    return img


def formula(d):
    fb = fuente(54)
    caja = d.textbbox((TAM / 2, 80), FORMULA, font=fb, anchor="mm")
    d.rounded_rectangle((caja[0] - 24, caja[1] - 16, caja[2] + 24, caja[3] + 16), radius=20,
                        fill="white", outline="black", width=6)
    d.text((TAM / 2, 80), FORMULA, font=fb, anchor="mm", fill="black")


if __name__ == "__main__":
    CARAS.mkdir(exist_ok=True)
    caras = []
    for n in range(1, 7):
        img = cara(n)
        img.save(CARAS / f"cara{n}.png")
        caras.append(img)
    hoja = plantilla(caras, f"{FORMULA}   ·   Imprimir al 100% (sin ajustar). Gris = pestañas.")
    hoja.save(BASE / "plantilla_formula_v2.png", dpi=(300, 300))
    hoja.save(BASE / "plantilla_formula_v2.pdf", resolution=300)
    print("Listo: caras/cara1..6.png, plantilla_formula_v2.png y .pdf  ->  vuelve a compilar targets.mind")
