import pytest
from detectors.local_ip import LocalIpDetector

def test_local_ip_detector_positive():
    detector = LocalIpDetector(config={})
    file_content = "const ip = '192.168.1.100';"
    signals = list(detector.match("test.js", file_content))
    assert len(signals) == 1
    assert signals[0]["type"] == "local_ip"
    assert "192.168.1.100" in signals[0]["detail"]

def test_local_ip_detector_class_a():
    detector = LocalIpDetector(config={})
    file_content = "const ip = '10.0.0.1';"
    signals = list(detector.match("test.js", file_content))
    assert len(signals) == 1
    assert signals[0]["type"] == "local_ip"
    assert "10.0.0.1" in signals[0]["detail"]

def test_local_ip_detector_class_b():
    detector = LocalIpDetector(config={})
    file_content = "const ip = '172.16.0.1';"
    signals = list(detector.match("test.js", file_content))
    assert len(signals) == 1
    assert signals[0]["type"] == "local_ip"
    assert "172.16.0.1" in signals[0]["detail"]

def test_local_ip_detector_class_b_edge():
    detector = LocalIpDetector(config={})
    file_content = "const ip = '172.31.255.255';"
    signals = list(detector.match("test.js", file_content))
    assert len(signals) == 1
    assert signals[0]["type"] == "local_ip"
    assert "172.31.255.255" in signals[0]["detail"]

def test_local_ip_detector_negative():
    detector = LocalIpDetector(config={})
    file_content = "const ip = '8.8.8.8';"  # Public IP
    signals = list(detector.match("test.js", file_content))
    assert len(signals) == 0

def test_local_ip_detector_severity_override():
    detector = LocalIpDetector(config={"severity": "high"})
    file_content = "const ip = '192.168.1.100';"
    signals = list(detector.match("test.js", file_content))
    assert len(signals) == 1
    assert signals[0]["severity"] == "high"