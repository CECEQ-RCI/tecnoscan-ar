import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";

// ---------------- Configuración ----------------
const ARCHIVO_PINTURA = "pintura.jpg";
const ARCHIVO_DINO = "dinosaurio.glb";
const ALTURA_DINO = 3;        // en "cubos": 3 = tres veces más alto que el cubo
const A = 0.6, B = 0.4;       // tamaños de a y b en la fórmula (a + b = 1 = lado del cubo)

export const reloj = new THREE.Clock();
export const actualizaciones = [];   // funciones que se llaman en cada cuadro

// Recorta una textura al centro para que quede cuadrada
function recortarCuadrado(tex, w, h) {
  const a = w / h;
  if (a > 1) { tex.repeat.set(1 / a, 1); tex.offset.set((1 - 1 / a) / 2, 0); }
  else       { tex.repeat.set(1, a);     tex.offset.set(0, (1 - a) / 2); }
}

// Etiqueta de texto que siempre mira a la cámara
function etiqueta(texto, { color = "#fff", fondo = "rgba(0,0,0,.65)", alto = 0.14 } = {}) {
  const c = document.createElement("canvas");
  const ctx = c.getContext("2d");
  const fuente = "bold 96px 'Segoe UI', Arial, sans-serif";
  ctx.font = fuente;
  const ancho = Math.ceil(ctx.measureText(texto).width) + 60;
  c.width = ancho; c.height = 140;
  ctx.font = fuente;
  ctx.fillStyle = fondo;
  ctx.beginPath(); ctx.roundRect(0, 0, c.width, c.height, 30); ctx.fill();
  ctx.fillStyle = color; ctx.textAlign = "center"; ctx.textBaseline = "middle";
  ctx.fillText(texto, c.width / 2, c.height / 2 + 4);
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  const sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex, depthTest: false, transparent: true }));
  sprite.scale.set(alto * c.width / c.height, alto, 1);
  sprite.renderOrder = 10;
  return sprite;
}

// ---------------- Modo: cubo con textura (video o pintura) ----------------
function cuboConTextura(textura) {
  const material = new THREE.MeshBasicMaterial({ map: textura });
  const geometria = new THREE.BoxGeometry(1.02, 1.02, 1.02);
  return () => new THREE.Mesh(geometria, material);
}

export function prepararVideo(video) {
  const tex = new THREE.VideoTexture(video);
  tex.colorSpace = THREE.SRGBColorSpace;
  video.addEventListener("loadedmetadata", () => recortarCuadrado(tex, video.videoWidth, video.videoHeight));
  video.addEventListener("error", () => alert("No encontré video.mp4 en la carpeta."));
  return { crear: cuboConTextura(tex), alEncontrar: () => video.play(), alPerder: () => video.pause() };
}

export async function prepararPintura() {
  const tex = await new THREE.TextureLoader().loadAsync(ARCHIVO_PINTURA)
    .catch(() => { throw new Error(`No encontré ${ARCHIVO_PINTURA} en la carpeta.`); });
  tex.colorSpace = THREE.SRGBColorSpace;
  recortarCuadrado(tex, tex.image.width, tex.image.height);
  return { crear: cuboConTextura(tex) };
}

// ---------------- Modo: dinosaurio (modelo .glb) ----------------
export async function prepararDino() {
  const gltf = await new GLTFLoader().loadAsync(ARCHIVO_DINO)
    .catch(() => { throw new Error(`No encontré ${ARCHIVO_DINO} en la carpeta.`); });
  // Escalar para que mida ALTURA_DINO cubos y apoyarlo sobre su base
  const caja = new THREE.Box3().setFromObject(gltf.scene);
  const tam = caja.getSize(new THREE.Vector3());
  const escala = ALTURA_DINO / tam.y;
  return {
    crear: () => {
      const dino = gltf.scene.clone(true);
      dino.scale.setScalar(escala);
      const centro = caja.getCenter(new THREE.Vector3());
      // Parado sobre la cara de arriba del cubo (y = 0.5), sin importar qué cara vea la cámara
      dino.position.set(-centro.x * escala, 0.5 - caja.min.y * escala, -centro.z * escala);
      if (gltf.animations.length) {
        const mixer = new THREE.AnimationMixer(dino);
        mixer.clipAction(gltf.animations[0]).play();
        actualizaciones.push((dt) => mixer.update(dt));
      }
      const g = new THREE.Group();
      g.add(dino);
      return g;
    },
  };
}

// ---------------- Modo: fórmula (a+b)³ ----------------
const COLORES = { 3: 0xe63946, 2: 0x457b9d, 1: 0x2a9d8f, 0: 0xf4a261 };   // por cantidad de "a"
const NOMBRES = { 3: "a³", 2: "a²b", 1: "ab²", 0: "b³" };

export function prepararFormula() {
  // Las 8 piezas: en cada eje el tramo puede ser "a" (lado negativo) o "b" (lado positivo)
  const piezas = [];
  for (const x of ["a", "b"]) for (const y of ["a", "b"]) for (const z of ["a", "b"]) {
    const dims = [x, y, z].map((t) => (t === "a" ? A : B));
    const centro = [x, y, z].map((t) => (t === "a" ? -0.5 + A / 2 : 0.5 - B / 2));
    const dir = [x, y, z].map((t) => (t === "a" ? -1 : 1));
    const nA = [x, y, z].filter((t) => t === "a").length;
    piezas.push({ dims, centro, dir, nA });
  }

  const ease = (t) => (t < 0.5 ? 2 * t * t : 1 - (-2 * t + 2) ** 2 / 2);
  const CICLO = 10;
  // 0–1.5 armado · 1.5–3 se separa · 3–7 separado con etiquetas · 7–8.5 se arma · 8.5–10 armado
  function separacion(t) {
    if (t < 1.5) return 0;
    if (t < 3) return ease((t - 1.5) / 1.5);
    if (t < 7) return 1;
    if (t < 8.5) return 1 - ease((t - 7) / 1.5);
    return 0;
  }

  return {
    crear: () => {
      const g = new THREE.Group();
      const etiquetas = [];
      for (const p of piezas) {
        const geo = new THREE.BoxGeometry(...p.dims);
        const malla = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ color: COLORES[p.nA], roughness: 0.5 }));
        malla.add(new THREE.LineSegments(new THREE.EdgesGeometry(geo), new THREE.LineBasicMaterial({ color: 0x111111 })));
        malla.position.set(...p.centro);
        g.add(malla);
        const et = etiqueta(NOMBRES[p.nA], { fondo: "#" + COLORES[p.nA].toString(16).padStart(6, "0") });
        g.add(et);
        etiquetas.push({ p, malla, et });
      }
      actualizaciones.push(() => {
        const t = reloj.elapsedTime % CICLO;
        const s = separacion(t);
        for (const { p, malla, et } of etiquetas) {
          const desp = p.dir.map((d) => d * 0.35 * s);
          malla.position.set(p.centro[0] + desp[0], p.centro[1] + desp[1], p.centro[2] + desp[2]);
          et.position.copy(malla.position);
          et.material.opacity = s;
          et.visible = s > 0.01;
        }
      });
      return g;
    },
    // En la cámara el título es un letrero fijo arriba de la pantalla (index.html)
    titulo: "(a+b)³ = a³ + 3a²b + 3ab² + b³",
    // En la vista previa va flotando arriba del cubo (en coordenadas de la cara)
    crearTitulo: () => {
      const titulo = etiqueta("(a+b)³ = a³ + 3a²b + 3ab² + b³", { alto: 0.16 });
      titulo.position.set(0, 1.25, 0);
      return titulo;
    },
  };
}


// ---------------- Orientación de cada cara ----------------
// Cómo queda cada cara impresa al doblar la plantilla en cruz: u = derecha de la imagen,
// v = arriba de la imagen, n = hacia afuera, en coordenadas del cubo (x derecha, y arriba,
// z al frente; el lado "a" de cada eje está en lo negativo). Igual que BASES en generar_formula.py.
const X = [1, 0, 0], Y = [0, 1, 0], Z = [0, 0, 1];
const neg = (v) => v.map((c) => -c);
export const BASES_CARAS = [
  [X, neg(Z), Y],        // cara 1: arriba
  [Z, Y, neg(X)],        // cara 2: izquierda
  [X, Y, Z],             // cara 3: frente
  [neg(Z), Y, X],        // cara 4: derecha
  [X, Z, neg(Y)],        // cara 5: abajo
  [X, neg(Y), neg(Z)],   // cara 6: atrás
];

// Coloca un objeto hecho en coordenadas del cubo dentro del ancla de la cara i (0..5):
// lo gira para que coincida con el cubo de papel y lo mete media unidad hacia adentro.
export function orientarEnCara(objeto, i) {
  const [u, v, n] = BASES_CARAS[i].map((c) => new THREE.Vector3(...c));
  const cuboAAncla = new THREE.Matrix4().makeBasis(u, v, n).transpose();
  objeto.setRotationFromMatrix(cuboAAncla);
  objeto.position.set(0, 0, -0.5);
  return objeto;
}
