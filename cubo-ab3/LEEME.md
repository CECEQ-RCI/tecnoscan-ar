# Cubo AR con video (proyecto STEM)

## Archivos
| Archivo | Para qué |
|---|---|
| `plantilla_cubo.pdf` | Imprimir y armar el cubo (carta, **al 100 %**, caras de 6 cm) |
| `plantilla_formula_v2.pdf` | **Cubo (a+b)³**: cada cara muestra las piezas a³, a²b, ab², b³ en su lugar real (fórmula en la cara 1 y al pie) |
| `generar_formula.py` | Genera las caras/plantilla del cubo (a+b)³ (`python generar_formula.py`) |
| `caras/cara1..6.png` | Las 6 caras que se compilan (las del último script que corriste) |
| `targets_patrones_aleatorios.mind` | Respaldo de los objetivos compilados para `plantilla_cubo.pdf` (patrones aleatorios) |
| `generar_patrones.py` | Vuelve a generar patrones/plantilla. `python generar_patrones.py 7` = caras de 7 cm |
| `compilar.html` | Convierte las 6 caras en `targets.mind` (lo que la cámara reconoce) |
| `index.html` | La experiencia AR. Modos: **Fórmula (a+b)³**, Video, Pintura, Dinosaurio (también `?modo=formula`) |
| `contenido.js` | El contenido de cada modo (tamaños de a y b, altura del dinosaurio, nombres de archivos) |
| `tarjetas_imprimir.pdf` | **Tarjetas con QR** (10 por hoja, frente y reverso, imprimir a doble cara por el borde largo) |
| `hoja_qr_docentes.pdf` | Guía para el docente con QR grande, pasos y actividad + 6 tarjetas sencillas |
| `generar_tarjeta.py` / `generar_qr.py` | Regeneran tarjetas y guía (el QR apunta a ceceq-rci.github.io/.../cubo-ab3/?modo=formula) |
| `vista_previa.html` | Ver cualquier modo **sin cámara** y girarlo con el mouse (útil para proyectar en clase) |

> ⚠️ `targets.mind` tiene que corresponder al cubo impreso. Si usas `plantilla_formula_v2.pdf`, compila
> después de `generar_formula.py`. Para volver al cubo de patrones aleatorios, copia
> `targets_patrones_aleatorios.mind` como `targets.mind`.

### Archivos opcionales según el modo
- **Video**: `video.mp4`
- **Pintura**: `pintura.jpg` (se recorta al centro y se pone en las 6 caras)
- **Dinosaurio**: `dinosaurio.glb` (modelo 3D gratuito, p. ej. de poly.pizza o Sketchfab con licencia CC; si trae animación, se reproduce). Mide 3 cubos de alto y sale de la cara que ve la cámara.
| `servidor.js` | Servidor local (`node servidor.js` → http://localhost:8080) |

## Pasos
1. **Imprimir** `plantilla_cubo.pdf` en cartulina, mate, al 100 %. Recortar, doblar y pegar las pestañas grises.
2. **Poner el video**: copiar tu video a esta carpeta con el nombre `video.mp4` (MP4/H.264, ideal < 20 MB, cuadrado o 16:9; se recorta al centro).
3. **Compilar** (solo una vez, o cada vez que cambien los patrones):
   `node servidor.js`, abrir http://localhost:8080/compilar.html en Chrome, clic en **Compilar** y esperar "¡Listo!".
   Debe aparecer el archivo `targets.mind`.
4. **Probar en la PC**: abrir http://localhost:8080, clic en **Iniciar** y mostrar el cubo a la webcam.
5. **Usar en celulares**: la cámara solo funciona con **https**. Lo más fácil:
   - Netlify Drop (app.netlify.com/drop): arrastrar la carpeta completa → da un link https.
   - o GitHub Pages.
   Luego generar un código QR con ese link para que los estudiantes lo abran.

## Consejos
- Buena luz, sin reflejos (no plastificar brillante).
- Mantener el cubo a 20–40 cm de la cámara.
- Si el video "tiembla", subir `filterMinCF` en `index.html` lo hace más estable (pero más lento en seguir).
- Si cambias los patrones, hay que recompilar `targets.mind` y reimprimir.

## Si al escanear "no pasa nada"
- Las 6 caras deben ser **distintas entre sí**: si comparten elementos idénticos (marcos, la misma
  franja de texto), MindAR confunde una cara con otra y el cubo queda mal ubicado. Por eso en la v2
  la fórmula solo va en la cara 1 y no hay marcos negros.
- `targets.mind` tiene que estar compilado con **las mismas caras que imprimiste**
  (`plantilla_formula.pdf` de la versión 1 ya no sirve con el `targets.mind` actual).
- Acerca la cámara: cada cara debe ocupar al menos ~1/4 de la pantalla, con buena luz y sin reflejos.
