import pytest
from detectors.port_exposure import PortExposureDetector

def test_port_exposure_detector_positive():
    detector = PortExposureDetector(config={})
    file_content = "app.listen(3000)"
    signals = list(detector.match("test.js", file_content))
    assert len(signals) == 1
    assert signals[0]["type"] == "port_exposure"
    assert signals[0]["detail"] == "Detected port exposure: 3000"

def test_port_exposure_detector_positive_with_callback():
    detector = PortExposureDetector(config={})
    file_content = "app.listen(8080, () => { console.log('listening') })"
    signals = list(detector.match("test.js", file_content))
    assert len(signals) == 1
    assert signals[0]["type"] == "port_exposure"
    assert signals[0]["detail"] == "Detected port exposure: 8080"

def test_port_exposure_detector_negative():
    detector = PortExposureDetector(config={})
    file_content = "const port = 3000;"
    signals = list(detector.match("test.js", file_content))
    assert len(signals) == 0

def test_port_exposure_detector_severity_override():
    detector = PortExposureDetector(config={"severity": "critical"})
    file_content = "app.listen(3000)"
    signals = list(detector.match("test.js", file_content))
    assert len(signals) == 1
    assert signals[0]["severity"] == "critical"
