import pytest
from detectors.certificate_check import CertificateCheckDetector

def test_certificate_check_python():
    detector = CertificateCheckDetector(config={})
    file_content = "response = requests.get(url, verify=False)"
    signals = list(detector.match("test.py", file_content))
    assert len(signals) == 1
    assert signals[0]["type"] == "certificate_check"
    assert "verify=False" in signals[0]["detail"]

def test_certificate_check_javascript():
    detector = CertificateCheckDetector(config={})
    file_content = "xhr.rejectUnauthorized = false;"
    signals = list(detector.match("test.js", file_content))
    assert len(signals) == 1
    assert signals[0]["type"] == "certificate_check"
    assert "rejectUnauthorized" in signals[0]["detail"]

def test_certificate_check_javascript_object():
    detector = CertificateCheckDetector(config={})
    file_content = "options = {rejectUnauthorized: false};"
    signals = list(detector.match("test.js", file_content))
    assert len(signals) == 1
    assert signals[0]["type"] == "certificate_check"

def test_certificate_check_negative():
    detector = CertificateCheckDetector(config={})
    file_content = "response = requests.get(url, verify=True)"
    signals = list(detector.match("test.py", file_content))
    assert len(signals) == 0

def test_certificate_check_severity_override():
    detector = CertificateCheckDetector(config={"severity": "critical"})
    file_content = "response = requests.get(url, verify=False)"
    signals = list(detector.match("test.py", file_content))
    assert len(signals) == 1
    assert signals[0]["severity"] == "critical"