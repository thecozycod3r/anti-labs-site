#!/usr/bin/env python3
"""Local dev server.

- Never lets the browser cache anything (Safari holds CSS/JS through a reload).
- Answers HTTP Range requests with 206 Partial Content. Safari will not play
  <video> from a server that can't, so without this the background video
  silently fails on localhost while working fine on GitHub Pages.
"""
import http.server, socketserver, sys, os, re

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8777
RANGE = re.compile(r'bytes=(\d*)-(\d*)')


class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Accept-Ranges', 'bytes')
        super().end_headers()

    def translate_path(self, path):
        # mirror GitHub Pages: /anti-light serves anti-light.html
        real = super().translate_path(path)
        if not os.path.exists(real) and os.path.exists(real + '.html'):
            return real + '.html'
        return real

    def send_head(self):
        m = RANGE.match(self.headers.get('Range', ''))
        path = self.translate_path(self.path)
        if not m or not os.path.isfile(path):
            return super().send_head()

        size = os.path.getsize(path)
        start = int(m.group(1)) if m.group(1) else max(0, size - int(m.group(2)))
        end = int(m.group(2)) if (m.group(1) and m.group(2)) else size - 1
        end = min(end, size - 1)
        if start > end:
            self.send_error(416, 'Requested Range Not Satisfiable')
            return None

        f = open(path, 'rb')
        f.seek(start)
        self._remaining = end - start + 1
        self.send_response(206)
        self.send_header('Content-Type', self.guess_type(path))
        self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
        self.send_header('Content-Length', str(self._remaining))
        self.end_headers()
        return f

    def copyfile(self, source, outputfile):
        remaining = getattr(self, '_remaining', None)
        if remaining is None:
            return super().copyfile(source, outputfile)
        while remaining > 0:
            chunk = source.read(min(64 * 1024, remaining))
            if not chunk:
                break
            outputfile.write(chunk)
            remaining -= len(chunk)
        self._remaining = None

    def log_message(self, *a):
        pass


class Server(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True


with Server(("", PORT), Handler) as httpd:
    print(f"serving {PORT}: no-store, byte ranges")
    httpd.serve_forever()
