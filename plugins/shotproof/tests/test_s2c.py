"""Self-checks for s2c.py. Run: python3 -m unittest discover -s plugins/shotproof/tests"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "skills/shotproof/scripts/s2c.py"
sys.path.insert(0, str(SCRIPT.parent))
import s2c  # noqa: E402

import numpy as np  # noqa: E402

GOOD_PROOF = """<!doctype html><html><head><meta charset="utf-8">
<meta name="robots" content="noindex,nofollow"><style>.hero{background:url('assets/hero.png')}</style></head>
<body><div data-private-proof>PRIVATE concept, not live.</div><img src="assets/logo.png" alt="Logo">
<a href="#contact">Contact</a></body></html>"""


class Scoring(unittest.TestCase):
    def test_identical_images_score_one(self):
        x = np.random.default_rng(1).uniform(0, 255, (60, 80))
        self.assertAlmostEqual(float(s2c.ssim_map(x, x).mean()), 1.0, places=6)

    def test_different_images_score_lower(self):
        rng = np.random.default_rng(2)
        x, y = rng.uniform(0, 255, (60, 80)), rng.uniform(0, 255, (60, 80))
        self.assertLess(float(s2c.ssim_map(x, y).mean()), 0.2)


    def test_band_shift_finds_content_moved_down(self):
        ref = np.full((400, 100), 255.0)
        for y in range(20, 380, 30):
            ref[y:y + 8, 10:90] = 0  # fake text lines
        cand = np.full_like(ref, 255.0)
        cand[6:] = ref[:-6]  # everything 6px lower
        self.assertEqual(s2c.band_shifts(ref, cand, bands=4)[1:3], [6, 6])


class ProofContract(unittest.TestCase):
    def test_good_proof_passes(self):
        self.assertEqual(s2c.proof_problems(GOOD_PROOF), [])

    def test_each_unsafe_pattern_is_caught(self):
        cases = {
            "<script>": GOOD_PROOF.replace("</body>", "<script>x()</script></body>"),
            "<iframe>": GOOD_PROOF.replace("</body>", "<iframe src=a.html></iframe></body>"),
            "<form>": GOOD_PROOF.replace("</body>", "<form></form></body>"),
            "event handler": GOOD_PROOF.replace("<img ", '<img onerror="x()" '),
            "non-relative URI": GOOD_PROOF.replace("assets/logo.png", "https://evil.test/a.png"),
            "protocol-relative": GOOD_PROOF.replace("assets/logo.png", "//evil.test/a.png"),
            "data URI": GOOD_PROOF.replace("assets/logo.png", "data:image/png;base64,AAAA"),
            "css url remote": GOOD_PROOF.replace("assets/hero.png", "http://x.test/h.png"),
            "@import": GOOD_PROOF.replace("<style>", "<style>@import 'x.css';"),
            "entity-encoded scheme": GOOD_PROOF.replace("assets/logo.png", "&#104;ttps://x.test/a.png"),
            "parent path": GOOD_PROOF.replace("assets/logo.png", "../secret.png"),
            "missing robots": GOOD_PROOF.replace('name="robots"', 'name="x"'),
            "missing banner": GOOD_PROOF.replace("data-private-proof", "data-x"),
            "dollar": GOOD_PROOF.replace("not live.", "not live. Save $500"),
            "meta refresh": GOOD_PROOF.replace("<head>", '<head><meta http-equiv="refresh" content="0;url=x">'),
        }
        for label, doc in cases.items():
            with self.subTest(label):
                self.assertTrue(s2c.proof_problems(doc), f"{label} not caught")


class Palette(unittest.TestCase):
    def test_palette_reports_dominant_and_sampled_colors(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as d:
            img = Image.new("RGB", (100, 100), "#ffffff")
            img.paste(Image.new("RGB", (100, 25), "#112233"), (0, 0))
            path = Path(d) / "p.png"
            img.save(path)
            out = subprocess.run([sys.executable, str(SCRIPT), "palette", str(path), "--at", "5,5", "5,90"],
                                 capture_output=True, text=True)
            data = json.loads(out.stdout)
            self.assertEqual(data["samples"], {"5,5": "#112233", "5,90": "#ffffff"})
            self.assertEqual(data["dominant"][0], {"hex": "#ffffff", "share": 0.75})


class EndToEnd(unittest.TestCase):
    def test_verify_page_against_its_own_render(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            page = d / "p.html"
            page.write_text("<!doctype html><body style='margin:0;font:20px sans-serif'>"
                            "<h1 style='background:#123;color:#fff;padding:40px'>Hello</h1><p>Body copy</p></body>")
            ref = d / "ref.png"
            s2c.render(str(page), ref, 400, 300)
            out = subprocess.run([sys.executable, str(SCRIPT), "verify", str(ref), str(page),
                                  "--out-dir", str(d / "v")], capture_output=True, text=True)
            report = json.loads(out.stdout)
            self.assertEqual(out.returncode, 0, out.stderr)
            self.assertGreater(report["ssim"], 0.99)
            self.assertTrue((d / "v/side-by-side.png").is_file())

    def test_console_error_fails_verify(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            page = d / "p.html"
            page.write_text("<!doctype html><body><script>console.error('boom')</script>Hi</body>")
            ref = d / "ref.png"
            s2c.render(str(page), ref, 200, 100)
            out = subprocess.run([sys.executable, str(SCRIPT), "verify", str(ref), str(page),
                                  "--out-dir", str(d / "v")], capture_output=True, text=True)
            self.assertEqual(out.returncode, 1)
            self.assertIn("boom", json.loads(out.stdout)["console_errors"][0])


if __name__ == "__main__":
    unittest.main()
