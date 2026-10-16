"""Tarjeta profesional (9 x 5 cm, frente y reverso) con el QR del cubo (a+b)³.

Uso:  python generar_tarjeta.py
Crea:
  tarjeta_frente.png / tarjeta_reverso.png   una tarjeta (para compartir en digital)
  tarjetas_imprimir.pdf                       hoja carta con 10 tarjetas y marcas de corte:
                                              hoja 1 = frentes, hoja 2 = reversos (doble cara, borde largo)
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from generar_qr import codigo_qr

BASE = Path(__file__).parent
DPI = 300
A = 0.6                                     # tramo "a" del cubo (igual que en la animación)
NAVY_1, NAVY_2 = (7, 17, 36), (26, 50, 90)
NARANJA = (244, 162, 97)
COLORES = {3: (230, 57, 70), 2: (69, 123, 157), 1: (42, 157, 143), 0: (244, 162, 97)}   # por cantidad de "a"
FORMULA = "(a+b)³ = a³ + 3a²b + 3ab² + b³"


def cm(x):
    return round(x / 2.54 * DPI)


TW, TH = cm(9), cm(5)


def f(px, peso="b"):
    nombres = {"b": "segoeuib.ttf", "r": "segoeui.ttf", "l": "segoeuisl.ttf", "n": "arialbd.ttf"}[peso]
    try:
        return ImageFont.truetype(nombres, px)
    except OSError:
        return ImageFont.truetype("arialbd.ttf", px)


def degradado(w, h, c1, c2):
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    for x in range(w):
        t = x / (w - 1)
        d.line((x, 0, x, h), fill=tuple(round(a + (b - a) * t) for a, b in zip(c1, c2)))
    return img


def franja_colores(d, y, alto):
    paso = TW / 4
    for i, c in enumerate([COLORES[3], COLORES[2], COLORES[1], COLORES[0]]):
        d.rectangle((round(i * paso), y, round((i + 1) * paso), y + alto), fill=c)


def icono_rci(lado):
    logo = Image.open(BASE / "logo-rci.jpg").convert("RGB")
    w, h = logo.size
    logo = logo.crop((int(w * 0.28), int(h * 0.21), int(w * 0.72), int(h * 0.65))).resize((lado, lado), Image.LANCZOS)
    mascara = Image.new("L", (lado, lado), 0)
    ImageDraw.Draw(mascara).rounded_rectangle((0, 0, lado - 1, lado - 1), radius=lado // 5, fill=255)
    return logo, mascara


def cubo_isometrico(lado):
    """Cubo (a+b)³ armado en perspectiva isométrica, con las piezas de colores en las 3 caras visibles."""
    import math
    ex, ey = math.cos(math.radians(30)), math.sin(math.radians(30))
    s = lado / (2 * ex) * 0.98
    W_, H_ = lado, round(s * (2 * ey + 1)) + 4
    img = Image.new("RGBA", (W_, H_), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    ox, oy = W_ / 2, s * 2 * ey + 2          # proyección del punto (1,0,1): vértice inferior frontal

    def P(x, y, z):                          # x hacia la derecha-abajo, z hacia la izquierda-abajo, y arriba
        return (ox + (x - z) * ex * s, oy + ((x + z) * ey - 2 * ey - y) * s + 2 * ey * s - 2 * ey * s)

    def proy(x, y, z):
        return (W_ / 2 + (x - z) * ex * s, H_ - 2 - ((2 - x - z) * ey + y) * s - 0)

    def tramos():
        return [(0, A, "a"), (A, 1, "b")]

    def sombra(c, k):
        return tuple(round(v * k) for v in c)

    linea = (20, 30, 50)
    caras = [  # (función de esquinas, factor de luz)
        ("arriba", 1.0), ("izquierda", 0.86), ("derecha", 0.70),
    ]
    for nombre, luz in caras:
        for u0, u1, lu in tramos():
            for v0, v1, lv in tramos():
                if nombre == "arriba":       # y = 1, ejes x y z
                    q = [proy(u0, 1, v0), proy(u1, 1, v0), proy(u1, 1, v1), proy(u0, 1, v1)]
                elif nombre == "izquierda":  # z = 1, ejes x e y
                    q = [proy(u0, v0, 1), proy(u1, v0, 1), proy(u1, v1, 1), proy(u0, v1, 1)]
                else:                        # x = 1, ejes z e y
                    q = [proy(1, v0, u0), proy(1, v0, u1), proy(1, v1, u1), proy(1, v1, u0)]
                nA = [lu, lv, "b"].count("a")
                d.polygon(q, fill=sombra(COLORES[nA], luz) + (255,), outline=linea + (255,), width=3)
    return img


def frente(qr):
    img = degradado(TW, TH, NAVY_1, NAVY_2)
    d = ImageDraw.Draw(img)
    m = cm(0.42)
    # Marca RCI
    t = cm(0.62)
    ico, msk = icono_rci(t)
    img.paste(ico, (m, m), msk)
    d.text((m + t + cm(0.18), m + t * 0.08), "RED CENTRAL", font=f(27, "b"), fill=(225, 232, 245))
    d.text((m + t + cm(0.18), m + t * 0.52), "DE INFORMÁTICA", font=f(27, "r"), fill=(160, 178, 205))
    # Título
    y = m + t + cm(0.42)
    d.text((m, y), "Cubo de", font=f(42, "l"), fill=(205, 215, 232))
    d.text((m, y + 50), "Realidad Aumentada", font=f(56, "b"), fill="white")
    d.text((m, y + 122), "(a+b)³", font=f(70, "n"), fill=NARANJA)
    d.text((m, TH - cm(0.42) - 44), "Escanea  ·  Apunta  ·  Descubre", font=f(28, "r"), fill=(160, 178, 205))
    # Panel del QR
    lado = cm(2.75)
    pad = cm(0.16)
    px = TW - m - lado - 2 * pad
    py = m
    d.rounded_rectangle((px, py, px + lado + 2 * pad, py + lado + 2 * pad), radius=cm(0.22), fill="white")
    img.paste(qr.resize((lado, lado), Image.LANCZOS), (px + pad, py + pad))
    d.text((px + pad + lado / 2, py + lado + 2 * pad + cm(0.18)), "Escanea con tu celular", font=f(25, "b"),
           fill=(225, 232, 245), anchor="ma")
    franja_colores(d, TH - cm(0.12), cm(0.12))
    return img


def reverso():
    img = Image.new("RGB", (TW, TH), (247, 249, 252))
    d = ImageDraw.Draw(img)
    m = cm(0.42)
    cubo = cubo_isometrico(cm(2.9))
    img.paste(cubo, (m, (TH - cm(0.12) - cubo.size[1]) // 2), cubo)
    x = m + cm(2.9) + cm(0.45)
    y = m + cm(0.05)
    d.text((x, y), "La fórmula, en 3D", font=f(36, "b"), fill=NAVY_2)
    d.text((x, y + 52), FORMULA, font=f(31, "n"), fill=(60, 72, 95))
    y += 120
    pasos = ["Arma el cubo con la plantilla", "Escanea el código QR", "Apunta a cualquier cara del cubo"]
    r = 19
    for i, p in enumerate(pasos):
        c = [COLORES[3], COLORES[2], COLORES[1]][i]
        d.ellipse((x, y, x + 2 * r, y + 2 * r), fill=c)
        d.text((x + r, y + r), str(i + 1), font=f(25, "b"), fill="white", anchor="mm")
        d.text((x + 2 * r + 16, y + r), p, font=f(27, "r"), fill=(40, 48, 66), anchor="lm")
        y += 2 * r + 16
    d.text((TW - m, TH - cm(0.12) - cm(0.3)), "Proyecto STEAM · CECEQ", font=f(22, "r"), fill=(130, 140, 160), anchor="rb")
    franja_colores(d, TH - cm(0.12), cm(0.12))
    return img


def hoja(tarjeta):
    """10 tarjetas (2 x 5) centradas en hoja carta, con marcas de corte en los márgenes."""
    W, H = round(8.5 * DPI), round(11 * DPI)
    h = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(h)
    cols, filas = 2, 5
    ox, oy = (W - cols * TW) // 2, (H - filas * TH) // 2
    for r in range(filas):
        for c in range(cols):
            h.paste(tarjeta, (ox + c * TW, oy + r * TH))
    gris, largo, sep = (120, 120, 120), cm(0.5), cm(0.15)
    for c in range(cols + 1):
        x = ox + c * TW
        d.line((x, oy - sep - largo, x, oy - sep), fill=gris, width=2)
        d.line((x, oy + filas * TH + sep, x, oy + filas * TH + sep + largo), fill=gris, width=2)
    for r in range(filas + 1):
        y = oy + r * TH
        d.line((ox - sep - largo, y, ox - sep, y), fill=gris, width=2)
        d.line((ox + cols * TW + sep, y, ox + cols * TW + sep + largo, y), fill=gris, width=2)
    return h


if __name__ == "__main__":
    qr = codigo_qr(cm(6))
    fr, rv = frente(qr), reverso()
    fr.save(BASE / "tarjeta_frente.png", dpi=(DPI, DPI))
    rv.save(BASE / "tarjeta_reverso.png", dpi=(DPI, DPI))
    h1, h2 = hoja(fr), hoja(rv)
    h1.save(BASE / "tarjetas_imprimir.pdf", resolution=DPI, save_all=True, append_images=[h2])
    print("Listo: tarjeta_frente.png, tarjeta_reverso.png y tarjetas_imprimir.pdf")
