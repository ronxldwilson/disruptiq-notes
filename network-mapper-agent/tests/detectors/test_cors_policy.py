import pytest
from detectors.cors_policy import CorsPolicyDetector

def test_cors_policy_detector_positive():
    detector = CorsPolicyDetector(config={})
    file_content = "app.use(cors({origin: '*'}));"
    signals = list(detector.match("test.js", file_content))
    assert len(signals) == 1
    assert signals[0]["type"] == "cors_policy"
    assert "permissive CORS policy" in signals[0]["detail"]

def test_cors_policy_detector_case_insensitive():
    detector = CorsPolicyDetector(config={})
    file_content = "app.use(Cors({Origin: '*'}));"
    signals = list(detector.match("test.js", file_content))
    assert len(signals) == 1
    assert signals[0]["type"] == "cors_policy"

def test_cors_policy_detector_with_quotes():
    detector = CorsPolicyDetector(config={})
    file_content = 'app.use(cors({"origin": "*"}));'
    signals = list(detector.match("test.js", file_content))
    assert len(signals) == 1
    assert signals[0]["type"] == "cors_policy"

def test_cors_policy_detector_negative():
    detector = CorsPolicyDetector(config={})
    file_content = "app.use(cors({origin: 'https://example.com'}));"
    signals = list(detector.match("test.js", file_content))
    assert len(signals) == 0

def test_cors_policy_detector_severity_override():
    detector = CorsPolicyDetector(config={"severity": "critical"})
    file_content = "app.use(cors({origin: '*'}));"
    signals = list(detector.match("test.js", file_content))
    assert len(signals) == 1
    assert signals[0]["severity"] == "critical"