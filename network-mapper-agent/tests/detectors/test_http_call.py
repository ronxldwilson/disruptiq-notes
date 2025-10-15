import pytest
from detectors.http_call import HttpCallDetector

def test_http_call_detector_positive_axios():
    detector = HttpCallDetector(config={})
    file_content = "axios.get('https://api.example.com')"
    signals = list(detector.match("test.js", file_content))
    assert len(signals) == 1
    assert signals[0]["type"] == "http_call"
    assert signals[0]["detail"] == "Detected HTTP call: axios.get"

def test_http_call_detector_positive_fetch():
    detector = HttpCallDetector(config={})
    file_content = "fetch('https://api.example.com')"
    signals = list(detector.match("test.js", file_content))
    assert len(signals) == 1
    assert signals[0]["type"] == "http_call"
    assert signals[0]["detail"] == "Detected HTTP call: fetch"

def test_http_call_detector_positive_requests():
    detector = HttpCallDetector(config={})
    file_content = "requests.post('https://api.example.com')"
    signals = list(detector.match("test.py", file_content))
    assert len(signals) == 1
    assert signals[0]["type"] == "http_call"
    assert signals[0]["detail"] == "Detected HTTP call: requests.post"

def test_http_call_detector_negative():
    detector = HttpCallDetector(config={})
    file_content = "console.log('hello')"
    signals = list(detector.match("test.js", file_content))
    assert len(signals) == 0
