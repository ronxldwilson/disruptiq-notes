import unittest
from pathlib import Path
import tempfile
import os

# Add src to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from analyzer import Analyzer
from config import Config

class TestAnalyzer(unittest.TestCase):
    def setUp(self):
        self.config = Config()
        self.analyzer = Analyzer(self.config)

    def test_analyze_file_single_char_vars(self):
        # Create a temp file with single char var
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode='w') as f:
            f.write("a = 1\n")
            temp_path = Path(f.name)

        findings = self.analyzer.analyze_file(temp_path)
        self.assertTrue(len(findings) > 0)
        self.assertEqual(findings[0].obfuscation_type, "single_char_vars")

        # Cleanup
        os.unlink(temp_path)

    def test_analyze_file_no_obfuscation(self):
        # Create a temp file with normal code
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode='w') as f:
            f.write("def hello_world():\n    print('Hello, World!')\n")
            temp_path = Path(f.name)

        findings = self.analyzer.analyze_file(temp_path)
        # Should have no findings or only low severity
        self.assertTrue(all(f.severity == "low" for f in findings) or len(findings) == 0)

        # Cleanup
        os.unlink(temp_path)

if __name__ == '__main__':
    unittest.main()
