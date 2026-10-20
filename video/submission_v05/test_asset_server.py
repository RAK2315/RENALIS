"""Exercise actual HTTP ranges used by the film player, without media fixtures."""
import functools
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path
from video.submission_v05.serve_assets import AssetHandler


class RangeTest(unittest.TestCase):
    def test_browser_ranges_and_download(self):
        with tempfile.TemporaryDirectory() as folder:
            payload = bytes(range(256)) * 16
            Path(folder, 'movie.mp4').write_bytes(payload)
            handler = functools.partial(AssetHandler, directory=folder)
            with ThreadingHTTPServer(('127.0.0.1', 0), handler) as server:
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                url = f'http://127.0.0.1:{server.server_port}/movie.mp4'
                try:
                    for value, start, end in [('bytes=0-1023', 0, 1023),
                                              ('bytes=3000-', 3000, 4095),
                                              ('bytes=-256', 3840, 4095)]:
                        req = urllib.request.Request(url, headers={'Range': value})
                        with urllib.request.urlopen(req) as response:
                            self.assertEqual(response.status, 206)
                            self.assertEqual(response.headers['Content-Range'], f'bytes {start}-{end}/4096')
                            self.assertEqual(response.read(), payload[start:end + 1])
                    with urllib.request.urlopen(url) as response:
                        self.assertEqual(response.read(), payload)
                    with self.assertRaises(urllib.error.HTTPError) as error:
                        urllib.request.urlopen(urllib.request.Request(url, headers={'Range': 'bytes=4096-'}))
                    self.assertEqual(error.exception.code, 416)
                finally:
                    server.shutdown()
                    thread.join()


if __name__ == '__main__':
    unittest.main()
