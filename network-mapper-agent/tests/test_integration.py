import os
import tempfile
import json
from main import main
import sys
from io import StringIO
import subprocess

def test_basic_scan():
    """Test basic scanning functionality with example files"""
    # Create a temporary directory with test files
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a test JavaScript file with hardcoded URL
        test_js_file = os.path.join(temp_dir, "test.js")
        with open(test_js_file, 'w') as f:
            f.write("const response = fetch('https://api.example.com/data');\n")
        
        # Create a test Python file with hardcoded IP
        test_py_file = os.path.join(temp_dir, "test.py")
        with open(test_py_file, 'w') as f:
            f.write("import socket\ns = socket.socket()\ns.connect(('192.168.1.100', 8080))\n")
        
        # Create a test server file with port exposure
        test_server_file = os.path.join(temp_dir, "server.js")
        with open(test_server_file, 'w') as f:
            f.write("const express = require('express');\nconst app = express();\napp.listen(3000);\n")
        
        # Test the scanner by importing and using the core functionality
        from main import load_detectors, get_file_language, validate_signal
        import yaml
        
        # Load detectors
        ruleset = None  # Use default
        detectors = load_detectors(ruleset)
        
        # Verify we have the expected detectors
        detector_ids = [d.id for d in detectors]
        assert "hardcoded_url_v1" in detector_ids
        assert "local_ip_v1" in detector_ids
        assert "port_exposure_v1" in detector_ids
        
        # Test language detection
        assert get_file_language("test.js") == "javascript"
        assert get_file_language("test.py") == "python"
        
        print("Integration test passed: basic functionality works")


def test_signal_validation():
    """Test that signals follow the required schema"""
    from main import validate_signal
    
    # Valid signal
    valid_signal = {
        "id": "test-123",
        "type": "hardcoded_url",
        "detector_id": "hardcoded_url_v1",
        "file": "test.js",
        "line": 1,
        "column": 1,
        "severity": "medium",
        "confidence": 0.9,
        "detail": "test detail",
        "context": {"snippet": "test"}
    }
    assert validate_signal(valid_signal) == True
    
    # Invalid signal (missing required field)
    invalid_signal = {
        "id": "test-123",
        "type": "hardcoded_url",
        "detector_id": "hardcoded_url_v1",
        "file": "test.js",
        "line": 1,
        "column": 1,
        "severity": "medium",
        "confidence": 0.9,
        # missing "detail" field
        "context": {"snippet": "test"}
    }
    assert validate_signal(invalid_signal) == False
    
    # Invalid signal (wrong confidence type)
    invalid_signal2 = {
        "id": "test-123",
        "type": "hardcoded_url",
        "detector_id": "hardcoded_url_v1",
        "file": "test.js",
        "line": 1,
        "column": 1,
        "severity": "medium",
        "confidence": "not_a_number",  # wrong type
        "detail": "test detail",
        "context": {"snippet": "test"}
    }
    assert validate_signal(invalid_signal2) == False
    
    print("Integration test passed: signal validation works")


if __name__ == "__main__":
    test_basic_scan()
    test_signal_validation()
    print("All integration tests passed!")