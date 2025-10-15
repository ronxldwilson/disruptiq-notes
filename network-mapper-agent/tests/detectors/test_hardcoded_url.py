import pytest
from detectors.hardcoded_url import HardcodedUrlDetector

def test_hardcoded_url_detector_positive():
    detector = HardcodedUrlDetector(config={})
    file_content = "const url = \"https://example.com/api\";"
    signals = list(detector.match("test.js", file_content))
    assert len(signals) == 1
    assert signals[0]["type"] == "hardcoded_url"
    assert signals[0]["detail"] == "Detected hardcoded external URL: https://example.com/api"

def test_hardcoded_url_detector_negative():
    detector = HardcodedUrlDetector(config={})
    file_content = "const url = \"/api\";"
    signals = list(detector.match("test.js", file_content))
    assert len(signals) == 0

def test_hardcoded_url_detector_severity_override():
    detector = HardcodedUrlDetector(config={"severity": "critical"})
    file_content = "const url = \"https://example.com/api\";"
    signals = list(detector.match("test.js", file_content))
    assert len(signals) == 1
    assert signals[0]["severity"] == "critical"

