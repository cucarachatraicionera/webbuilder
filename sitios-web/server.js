import http from 'node:http'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const PORT = process.env.PORT || 4000
const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'application/javascript',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.webp': 'image/webp',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
}

function serve(res, filePath) {
  const ext = path.extname(filePath)
  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404, { 'Content-Type': 'text/html; charset=utf-8' })
      res.end('<h1>404 - No encontrado</h1>')
      return
    }
    res.writeHead(200, { 'Content-Type': MIME[ext] || 'application/octet-stream' })
    res.end(data)
  })
}

const server = http.createServer((req, res) => {
  let url = decodeURIComponent(req.url.split('?')[0])
  if (url === '/') url = '/index.html'

  // Route: /site-slug/... -> sitios-web/site-slug/dist/...
  const parts = url.split('/').filter(Boolean)
  if (parts.length >= 1) {
    // Check if first path part is a site directory
    const siteDir = path.join(__dirname, parts[0])
    if (fs.existsSync(siteDir) && fs.statSync(siteDir).isDirectory() && parts[0] !== 'informe-comercial.html') {
      const slug = parts[0]
      const rest = parts.slice(1).join('/') || 'index.html'
      const distPath = path.join(__dirname, slug, 'dist', rest)
      if (fs.existsSync(distPath)) {
        return serve(res, distPath)
      }
    }
  }

  // Fallback: serve from sitios-web root (hub page, report, etc.)
  const filePath = path.join(__dirname, url)
  if (fs.existsSync(filePath) && fs.statSync(filePath).isFile()) {
    return serve(res, filePath)
  }

  res.writeHead(404, { 'Content-Type': 'text/html; charset=utf-8' })
  res.end('<h1>404 - No encontrado</h1>')
})

server.listen(PORT, () => {
  console.log(`\n  🚀 Servidor desplegado en: http://localhost:${PORT}`)
  console.log(`  📋 Hub:        http://localhost:${PORT}/`)
  console.log(`  📊 Informe:    http://localhost:${PORT}/informe-comercial.html`)
  console.log(`  📱 Red local:  http://192.168.1.119:${PORT}/`)
  console.log(`  \n  Presiona Ctrl+C para detener\n`)
})
