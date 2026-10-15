// Servidor local:  node servidor.js   ->  http://localhost:8080
// Sirve los archivos de esta carpeta y guarda targets.mind cuando lo envía compilar.html.
const http = require("http");
const fs = require("fs");
const path = require("path");

const RAIZ = __dirname;
const PUERTO = 8080;
const TIPOS = {
  ".html": "text/html; charset=utf-8", ".js": "text/javascript", ".png": "image/png",
  ".jpg": "image/jpeg", ".mp4": "video/mp4", ".webm": "video/webm", ".mind": "application/octet-stream",
  ".pdf": "application/pdf",
};

http.createServer((req, res) => {
  if (req.method === "POST" && req.url === "/guardar-targets") {
    const partes = [];
    req.on("data", (p) => partes.push(p));
    req.on("end", () => {
      fs.writeFileSync(path.join(RAIZ, "targets.mind"), Buffer.concat(partes));
      console.log("targets.mind guardado");
      res.end("ok");
    });
    return;
  }
  // Cuadros de la vista previa (para armar un GIF): POST /guardar-cuadro?n=12
  if (req.method === "POST" && req.url.startsWith("/guardar-cuadro")) {
    const n = parseInt(new URL(req.url, "http://x").searchParams.get("n"), 10) || 0;
    const partes = [];
    req.on("data", (p) => partes.push(p));
    req.on("end", () => {
      fs.mkdirSync(path.join(RAIZ, "capturas"), { recursive: true });
      fs.writeFileSync(path.join(RAIZ, "capturas", `cuadro${String(n).padStart(3, "0")}.png`), Buffer.concat(partes));
      res.end("ok");
    });
    return;
  }
  const url = decodeURIComponent(req.url.split("?")[0]);
  const archivo = path.join(RAIZ, url === "/" ? "index.html" : url);
  if (!archivo.startsWith(RAIZ) || !fs.existsSync(archivo) || fs.statSync(archivo).isDirectory()) {
    res.writeHead(404); res.end("No encontrado"); return;
  }
  const tam = fs.statSync(archivo).size;
  const tipo = TIPOS[path.extname(archivo).toLowerCase()] || "application/octet-stream";
  // Soporte de rangos para que el video se pueda reproducir/adelantar
  const rango = req.headers.range;
  if (rango) {
    const [ini, fin] = rango.replace("bytes=", "").split("-");
    const a = parseInt(ini, 10), b = fin ? parseInt(fin, 10) : tam - 1;
    res.writeHead(206, { "Content-Type": tipo, "Content-Range": `bytes ${a}-${b}/${tam}`, "Accept-Ranges": "bytes", "Content-Length": b - a + 1 });
    fs.createReadStream(archivo, { start: a, end: b }).pipe(res);
  } else {
    res.writeHead(200, { "Content-Type": tipo, "Content-Length": tam });
    fs.createReadStream(archivo).pipe(res);
  }
}).listen(PUERTO, () => console.log(`Abre http://localhost:${PUERTO}`));
