"""Loopback-only production asset server with MP4 byte-range seeking."""
import argparse
import functools
import re
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class AssetHandler(SimpleHTTPRequestHandler):
    def send_head(self):
        self.remaining = None
        requested = self.headers.get('Range')
        path = Path(self.translate_path(self.path))
        if not requested or not path.is_file():
            return super().send_head()
        # Browsers request a single byte range when seeking an MP4. Multiple
        # ranges are ignored, as permitted by HTTP, rather than misrepresented.
        match = re.fullmatch(r'bytes=(\d*)-(\d*)', requested.strip())
        if not match:
            return super().send_head()
        stream = path.open('rb')
        size = path.stat().st_size
        first, last = match.groups()
        if first:
            start = int(first)
            end = min(int(last), size - 1) if last else size - 1
        else:
            start = max(0, size - int(last or 0))
            end = size - 1
        if start > end or start >= size:
            stream.close()
            self.send_response(416)
            self.send_header('Content-Range', f'bytes */{size}')
            self.send_header('Content-Length', '0')
            self.end_headers()
            return None
        self.send_response(206)
        self.send_header('Content-type', self.guess_type(str(path)))
        self.send_header('Accept-Ranges', 'bytes')
        self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
        self.send_header('Content-Length', str(end - start + 1))
        self.send_header('Last-Modified', self.date_time_string(path.stat().st_mtime))
        self.end_headers()
        stream.seek(start)
        self.remaining = end - start + 1
        return stream

    def copyfile(self, source, outputfile):
        try:
            if self.remaining is None:
                return super().copyfile(source, outputfile)
            while self.remaining:
                block = source.read(min(256 * 1024, self.remaining))
                if not block:
                    break
                outputfile.write(block)
                self.remaining -= len(block)
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            pass  # Closing or seeking a browser video cancels its old request.


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=5176)
    args = parser.parse_args()
    handler = functools.partial(AssetHandler, directory=str(ROOT))
    with ThreadingHTTPServer(('127.0.0.1', args.port), handler) as server:
        print(f'RENALIS film: http://127.0.0.1:{args.port}/artifacts/submission-v05/player.html', flush=True)
        server.serve_forever()


if __name__ == '__main__':
    main()
