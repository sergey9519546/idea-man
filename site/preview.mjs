import http from 'node:http';
import { readFile, stat } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
const root = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', 'docs');
const types = {'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'text/javascript; charset=utf-8','.png':'image/png','.webp':'image/webp','.svg':'image/svg+xml','.ico':'image/x-icon'};
const server = http.createServer(async (request, response) => {
  try {
    let file = path.resolve(root, '.' + decodeURIComponent(new URL(request.url, 'http://localhost').pathname));
    if (file !== root && !file.startsWith(root + path.sep)) throw new Error('Invalid path');
    if ((await stat(file)).isDirectory()) file = path.join(file, 'index.html');
    const content = await readFile(file);
    response.writeHead(200, {'Content-Type': types[path.extname(file)] || 'application/octet-stream'});
    response.end(content);
  } catch {
    response.writeHead(404, {'Content-Type':'text/plain'});
    response.end('Not found');
  }
});
server.listen(4317, '127.0.0.1', () => console.log('Local: http://127.0.0.1:4317'));
