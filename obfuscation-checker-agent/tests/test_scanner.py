import unittest
from pathlib import Path
import tempfile
import os

# Add src to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scanner import Scanner
from config import Config

class TestScanner(unittest.TestCase):
    def setUp(self):
        self.config = Config()
        self.scanner = Scanner(self.config)

    def test_should_ignore(self):
        # Test ignore patterns
        self.assertTrue(self.scanner.should_ignore(Path("node_modules/file.js")))
        self.assertFalse(self.scanner.should_ignore(Path("src/main.py")))

    def test_should_scan_file(self):
        # Create a temp file
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as f:
            f.write(b"print('test')")
            temp_path = Path(f.name)

        self.assertTrue(self.scanner.should_scan_file(temp_path))

        # Cleanup
        os.unlink(temp_path)

    def test_scan_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            py_file = Path(temp_dir) / "test.py"
            py_file.write_text("print('hello')")

            js_file = Path(temp_dir) / "test.js"
            js_file.write_text("console.log('hello')")

            ignore_dir = Path(temp_dir) / "node_modules"
            ignore_dir.mkdir()
            ignored_file = ignore_dir / "ignored.js"
            ignored_file.write_text("console.log('ignored')")

            files = self.scanner.scan_directory(temp_dir)
            file_names = [f.name for f in files]

            self.assertIn("test.py", file_names)
            self.assertIn("test.js", file_names)
            self.assertNotIn("ignored.js", file_names)

if __name__ == '__main__':
    unittest.main()
