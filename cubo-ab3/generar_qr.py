"""Hoja para docentes con el código QR del cubo (a+b)³ + tarjetas recortables.

Uso:  python generar_qr.py [ruta_logo]
Crea qr_cubo.png (solo el código) y hoja_qr_docentes.pdf (2 hojas carta):
  1) guía para el docente con QR grande, pasos y actividad
  2) 6 tarjetas recortables con el QR para repartir
"""
import sys
from pathlib import Path

import qrcode
from qrcode.constants import ERROR_CORRECT_H
from PIL import Image, ImageDraw

from generar_patrones import fuente

BASE = Path(__file__).parent
URL = "https://ceceq-rci.github.io/tecnoscan-ar/cubo-ab3/?modo=formula"
LOGO = Path(sys.argv[1]) if len(sys.argv) > 1 else BASE / "logo-rci.jpg"
DPI = 300
W, H = round(8.5 * DPI), round(11 * DPI)
AZUL = (29, 53, 87)
GRIS = (90, 90, 90)
SUAVE = (234, 240, 248)
COLORES = [(230, 57, 70), (69, 123, 157), (42, 157, 143), (244, 162, 97)]
FORMULA = "(a+b)³ = a³ + 3a²b + 3ab² + b³"


def cm(x):
    return round(x / 2.54 * DPI)


def codigo_qr(lado):
    qr = qrcode.QRCode(error_correction=ERROR_CORRECT_H, box_size=20, border=2)
    qr.add_data(URL)
    qr.make(fit=True)
    img = qr.make_image(fill_color=AZUL, back_color="white").convert("RGB")
    # Ícono de RCI al centro (≈20 % del ancho; la corrección H tolera hasta 30 %)
    if LOGO.exists():
        logo = Image.open(LOGO).convert("RGB")
        w, h = logo.size
        logo = logo.crop((int(w * 0.28), int(h * 0.21), int(w * 0.72), int(h * 0.65)))  # solo el ícono
        t = int(img.size[0] * 0.20)
        logo = logo.resize((t, t), Image.LANCZOS)
        mascara = Image.new("L", (t, t), 0)
        ImageDraw.Draw(mascara).rounded_rectangle((0, 0, t - 1, t - 1), radius=t // 5, fill=255)
        borde = t // 12
        fondo = Image.new("RGB", (t + 2 * borde, t + 2 * borde), "white")
        mf = Image.new("L", fondo.size, 0)
        ImageDraw.Draw(mf).rounded_rectangle((0, 0, fondo.size[0] - 1, fondo.size[1] - 1), radius=t // 4, fill=255)
        c = (img.size[0] - fondo.size[0]) // 2
        img.paste(fondo, (c, c), mf)
        img.paste(logo, (c + borde, c + borde), mascara)
    return img.resize((lado, lado), Image.LANCZOS)


def cubitos(d, x, y, t):
    """Cuatro cuadritos de colores (a³, a²b, ab², b³) como adorno."""
    for i, c in enumerate(COLORES):
        d.rounded_rectangle((x + i * (t + t // 3), y, x + i * (t + t // 3) + t, y + t), radius=t // 5, fill=c)


def texto_parrafo(d, x, y, ancho, texto, f, color=(30, 30, 30), interlineado=1.35):
    palabras, linea = texto.split(), ""
    alto = f.size * interlineado
    for p in palabras:
        prueba = (linea + " " + p).strip()
        if d.textlength(prueba, font=f) > ancho and linea:
            d.text((x, y), linea, font=f, fill=color)
            y += alto
            linea = p
        else:
            linea = prueba
    if linea:
        d.text((x, y), linea, font=f, fill=color)
        y += alto
    return y


def hoja_docente(qr_img, vista):
    hoja = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(hoja)
    m = cm(1.6)
    # Encabezado
    d.rectangle((0, 0, W, cm(3.4)), fill=SUAVE)
    cubitos(d, m, cm(0.9), cm(0.55))
    d.text((m, cm(1.7)), "Cubo de realidad aumentada  (a+b)³", font=fuente(92), fill=AZUL)
    d.text((W - m, cm(1.0)), "Guía para el docente", font=fuente(44), fill=GRIS, anchor="ra")
    # QR + vista previa
    y = cm(4.3)
    lado_qr = cm(8.5)
    hoja.paste(qr_img, (m, y))
    d.text((m + lado_qr // 2, y + lado_qr + cm(0.3)), "Escanea con la cámara del celular", font=fuente(40),
           fill=AZUL, anchor="ma")
    xv = m + lado_qr + cm(1.0)
    ancho_v = W - m - xv
    v = vista.resize((ancho_v, round(vista.size[1] * ancho_v / vista.size[0])), Image.LANCZOS)
    d.rounded_rectangle((xv - 6, y - 6, xv + v.size[0] + 6, y + v.size[1] + 6), radius=24, outline=(200, 205, 215), width=4)
    hoja.paste(v, (xv, y))
    yv = y + v.size[1] + cm(0.4)
    yv = texto_parrafo(d, xv, yv, ancho_v,
                       "Al apuntar al cubo de papel aparece el cubo en 3D: se separa en sus 8 piezas y se vuelve a armar.",
                       fuente(38), GRIS)
    d.text((xv, yv + cm(0.2)), FORMULA, font=fuente(46), fill=AZUL)
    # Pasos
    y = y + lado_qr + cm(1.6)
    d.text((m, y), "Cómo usarlo", font=fuente(60), fill=AZUL)
    y += cm(1.0)
    pasos = [
        "Imprime la plantilla del cubo (plantilla_formula_v2.pdf) al 100 %, en cartulina mate. Recorta, dobla por las líneas finas y pega las pestañas grises.",
        "Abre la cámara del celular y apunta a este código QR. Toca el enlace que aparece.",
        "Permite el uso de la cámara cuando el navegador lo pida.",
        "Apunta a cualquier cara del cubo a unos 20–30 cm, con buena luz. ¡Gíralo: el cubo virtual lo sigue por todos lados!",
    ]
    f = fuente(40)
    for i, p in enumerate(pasos, 1):
        r = cm(0.42)
        d.ellipse((m, y, m + 2 * r, y + 2 * r), fill=COLORES[(i - 1) % 4])
        d.text((m + r, y + r), str(i), font=fuente(36), fill="white", anchor="mm")
        y = max(texto_parrafo(d, m + 2 * r + cm(0.4), y + 4, W - 2 * m - 2 * r - cm(0.4), p, f), y + 2 * r) + cm(0.3)
    # Actividad
    y += cm(0.4)
    caja_y = y
    y += cm(0.5)
    d.text((m + cm(0.6), y), "Actividad sugerida", font=fuente(54), fill=AZUL)
    y += cm(0.95)
    act = [
        "Predice: con el cubo armado, ¿cuántas piezas hay y de qué tamaños?",
        "Observa: cuenta las piezas de cada color cuando el cubo se separa (1 roja, 3 azules, 3 verdes, 1 naranja).",
        "Comprueba con números: si a = 3 y b = 1, (3+1)³ = 64 y 27 + 27 + 9 + 1 = 64.",
        "Discute: ¿por qué (a+b)³ no es igual a a³ + b³? ¿Qué piezas faltarían?",
    ]
    for p in act:
        d.text((m + cm(0.6), y), "•", font=f, fill=AZUL)
        y = texto_parrafo(d, m + cm(1.2), y, W - 2 * m - cm(1.8), p, f) + cm(0.1)
    d.rounded_rectangle((m, caja_y, W - m, y + cm(0.3)), radius=30, outline=(200, 205, 215), width=5)
    # Pie
    texto_parrafo(d, m, H - cm(2.0), W - 2 * m,
                  "Funciona en Android y iPhone, sin instalar apps. Si la página ya se había abierto antes, recárgala. "
                  "Sin cámara (para proyectar): " + URL.replace("?modo=formula", "vista_previa.html"),
                  fuente(32), GRIS)
    return hoja


def hoja_tarjetas(qr_img):
    hoja = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(hoja)
    cols, filas = 2, 3
    mx, my = cm(1.0), cm(1.2)
    tw, th = (W - 2 * mx) // cols, (H - 2 * my) // filas
    lado = cm(5.6)
    q = qr_img.resize((lado, lado), Image.LANCZOS)
    for r in range(filas):
        for c in range(cols):
            x, y = mx + c * tw, my + r * th
            # línea de corte punteada
            for k in range(0, tw, 40):
                d.line((x + k, y, x + min(k + 20, tw), y), fill=(170, 170, 170), width=3)
                d.line((x + k, y + th, x + min(k + 20, tw), y + th), fill=(170, 170, 170), width=3)
            for k in range(0, th, 40):
                d.line((x, y + k, x, y + min(k + 20, th)), fill=(170, 170, 170), width=3)
                d.line((x + tw, y + k, x + tw, y + min(k + 20, th)), fill=(170, 170, 170), width=3)
            cx = x + tw // 2
            cubitos(d, cx - cm(1.25), y + cm(0.55), cm(0.42))
            d.text((cx, y + cm(1.25)), "Cubo AR  (a+b)³", font=fuente(56), fill=AZUL, anchor="ma")
            hoja.paste(q, (cx - lado // 2, y + cm(2.15)))
            d.text((cx, y + cm(2.15) + lado + cm(0.25)), "Escanea y apunta al cubo", font=fuente(40), fill=GRIS, anchor="ma")
    return hoja


if __name__ == "__main__":
    qr_img = codigo_qr(cm(8.5))
    qr_img.save(BASE / "qr_cubo.png", dpi=(DPI, DPI))
    vista = Image.open(BASE / "capturas" / "cuadro060.png").convert("RGB") if (BASE / "capturas" / "cuadro060.png").exists() \
        else Image.open(BASE / "animacion_formula.gif").convert("RGB")
    h1, h2 = hoja_docente(qr_img, vista), hoja_tarjetas(qr_img)
    h1.save(BASE / "hoja_qr_docentes.pdf", resolution=DPI, save_all=True, append_images=[h2])
    h1.save(BASE / "hoja_qr_docentes_1.png", dpi=(DPI, DPI))
    h2.save(BASE / "hoja_qr_docentes_2.png", dpi=(DPI, DPI))
    print("Listo: qr_cubo.png y hoja_qr_docentes.pdf (2 hojas)")
