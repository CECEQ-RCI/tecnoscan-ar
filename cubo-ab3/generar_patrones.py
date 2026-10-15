"""Genera 6 patrones propios (uno por cara) y la plantilla imprimible del cubo.

Uso:  python generar_patrones.py [lado_cm]
      lado_cm = tamaño de cada cara impresa (por defecto 6 cm, cabe en hoja carta).

Los patrones son aleatorios pero reproducibles (semilla fija por cara) y tienen
muchas esquinas y alto contraste, que es lo que necesita el rastreo de imágenes.
"""
import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).parent
CARAS = BASE / "caras"
TAM = 1000                      # px de cada patrón (para compilar)
DPI = 300
LADO_CM = float(sys.argv[1]) if len(sys.argv) > 1 else 6.0
COLORES = ["#111111", "#e63946", "#1d3557", "#2a9d8f", "#f4a261", "#6a4c93", "#ffffff"]


def fuente(px):
    for nombre in ("arialbd.ttf", "Arial Bold.ttf", "DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(nombre, px)
        except OSError:
            pass
    return ImageFont.load_default()


def patron(n):
    rnd = random.Random(1000 + n)
    img = Image.new("RGB", (TAM, TAM), "white")
    d = ImageDraw.Draw(img)
    # Formas aleatorias superpuestas: muchas esquinas, nada simétrico ni repetido
    for _ in range(140):
        c = rnd.choice(COLORES)
        x, y = rnd.randint(-80, TAM), rnd.randint(-80, TAM)
        s = rnd.randint(25, 170)
        t = rnd.random()
        if t < 0.35:
            pts = [(x + rnd.randint(-s, s), y + rnd.randint(-s, s)) for _ in range(rnd.randint(3, 6))]
            d.polygon(pts, fill=c)
        elif t < 0.6:
            d.rectangle([x, y, x + s, y + rnd.randint(10, s)], fill=c)
        elif t < 0.8:
            d.ellipse([x, y, x + s, y + s], outline=c, width=rnd.randint(6, 20))
        else:
            ang = rnd.random() * math.pi
            d.line([x, y, x + s * 2 * math.cos(ang), y + s * 2 * math.sin(ang)], fill=c, width=rnd.randint(5, 18))
    # Número grande de la cara (ayuda a armar y a orientar)
    f = fuente(260)
    txt = str(n + 1)
    bx = d.textbbox((0, 0), txt, font=f)
    w, h = bx[2] - bx[0], bx[3] - bx[1]
    px, py = rnd.randint(80, TAM - w - 80), rnd.randint(80, TAM - h - 80)
    d.rectangle([px - 30, py - 20 - bx[1], px + w + 30, py + h + 20], fill="white", outline="black", width=12)
    d.text((px, py - bx[1]), txt, font=f, fill="black")
    # Marco negro
    d.rectangle([0, 0, TAM - 1, TAM - 1], outline="black", width=24)
    return img


def plantilla(caras, texto=None):
    """Desarrollo en cruz (3 x 4 caras) con pestañas, en hoja carta a 300 dpi."""
    lado = round(LADO_CM / 2.54 * DPI)
    W, H = round(8.5 * DPI), round(11 * DPI)
    hoja = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(hoja)
    ox, oy = (W - 3 * lado) // 2, (H - 4 * lado) // 2
    # posición (columna, fila) de cada cara en la cruz
    pos = [(1, 0), (0, 1), (1, 1), (2, 1), (1, 2), (1, 3)]
    pest = lado // 5
    gris = (200, 200, 200)
    # Una pestaña por cada una de las 7 aristas que se pegan:
    # caras laterales (izq./der.) arriba, abajo y su lado exterior, más la parte superior de la cara 1.
    pestanas = [((0, 1), (0, -1)), ((0, 1), (0, 1)), ((0, 1), (-1, 0)),
                ((2, 1), (0, -1)), ((2, 1), (0, 1)), ((2, 1), (1, 0)),
                ((1, 0), (0, -1))]
    for (c, r), (dc, dr) in pestanas:
        x, y = ox + c * lado, oy + r * lado
        if True:
            if dr == -1:
                poly = [(x, y), (x + pest, y - pest), (x + lado - pest, y - pest), (x + lado, y)]
            elif dr == 1:
                poly = [(x, y + lado), (x + pest, y + lado + pest), (x + lado - pest, y + lado + pest), (x + lado, y + lado)]
            elif dc == -1:
                poly = [(x, y), (x - pest, y + pest), (x - pest, y + lado - pest), (x, y + lado)]
            else:
                poly = [(x + lado, y), (x + lado + pest, y + pest), (x + lado + pest, y + lado - pest), (x + lado, y + lado)]
            # solo dibujar si no se sale de la hoja
            if all(0 <= px < W and 0 <= py < H for px, py in poly):
                d.polygon(poly, fill=gris, outline="black")
    for img, (c, r) in zip(caras, pos):
        hoja.paste(img.resize((lado, lado), Image.LANCZOS), (ox + c * lado, oy + r * lado))
    # Líneas finas de corte/doblez en el borde de cada cara (no forman parte de lo que se detecta)
    for (c, r) in pos:
        x, y = ox + c * lado, oy + r * lado
        d.rectangle([x, y, x + lado, y + lado], outline=(60, 60, 60), width=3)
    f = fuente(40)
    texto = texto or f"Cubo AR - imprimir al 100% (sin ajustar). Cara = {LADO_CM:g} cm. Gris = pestañas para pegar."
    d.text((60, H - 110), texto,
           font=f, fill="black")
    return hoja


if __name__ == "__main__":
    CARAS.mkdir(exist_ok=True)
    caras = []
    for i in range(6):
        img = patron(i)
        img.save(CARAS / f"cara{i + 1}.png")
        caras.append(img)
    hoja = plantilla(caras)
    hoja.save(BASE / "plantilla_cubo.png", dpi=(DPI, DPI))
    hoja.save(BASE / "plantilla_cubo.pdf", resolution=DPI)
    print("Listo: caras/cara1..6.png, plantilla_cubo.png y plantilla_cubo.pdf")
