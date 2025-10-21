from detectors.base import Detector, Signal
import re

# Regex patterns for real-time connections
REALTIME_PATTERNS = [
    re.compile(r'(?:paho\.mqtt\.client|mqtt\.Client)\s*\(\s*', re.IGNORECASE),
    re.compile(r'(?:RTCPeerConnection|webrtc\.|WebRTC)\s', re.IGNORECASE),
    re.compile(r'(?:EventSource|Server-Sent Events|sse)\s', re.IGNORECASE),
    re.compile(r'(?:socket\.io|socketio)\s', re.IGNORECASE),
    re.compile(r'(?:import.*paho|require.*mqtt|require.*webrtc)', re.IGNORECASE),
    re.compile(r'(?:ws://|wss://)[^\s\'"]+', re.IGNORECASE),  # WebSocket URLs
]

class RealtimeConnectionDetector(Detector):
    id = "realtime_connection_v1"
    name = "Real-time Connection Detector"
    description = "Detects MQTT, WebRTC, SSE, and WebSocket connections"
    supported_languages = ["python", "javascript", "java", "go"]

    def __init__(self, config):
        super().__init__(config)

    def match(self, file_path, file_content, ast=None):
        for pattern in REALTIME_PATTERNS:
            for m in pattern.finditer(file_content):
                start = m.start()
                line = file_content.count("\n", 0, start) + 1
                col = start - file_content.rfind("\n", 0, start)

                # Extract context
                line_start = file_content.rfind("\n", 0, start)
                if line_start == -1:
                    line_start = 0
                else:
                    line_start += 1

                line_end = file_content.find("\n", start)
                if line_end == -1:
                    line_end = len(file_content)

                snippet_line = file_content[line_start:line_end]

                prev_line_start = file_content.rfind("\n", 0, line_start-1)
                if prev_line_start == -1:
                    prev_line_start = 0
                else:
                    prev_line_start += 1
                prev_line = file_content[prev_line_start:line_start-1] if line_start > 1 else ""

                next_line_end = file_content.find("\n", line_end+1)
                if next_line_end == -1:
                    next_line = ""
                else:
                    next_line = file_content[line_end+1:next_line_end]

                match_text = m.group(0).strip()

                yield {
                    "id": f"realtime-{file_path}-{line}-{hash(match_text)}",
                    "type": "realtime_connection",
                    "detector_id": self.id,
                    "file": file_path,
                    "line": line,
                    "column": col,
                    "severity": self.config.get("severity", "low"),
                    "confidence": 0.8,
                    "detail": f"Detected real-time connection: {match_text}",
                    "context": {
                        "snippet": snippet_line.strip(),
                        "pre": prev_line.strip(),
                        "post": next_line.strip()
                    },
                    "tags": ["network", "realtime", "websocket", "mqtt"],
                    "remediation": "Review real-time connection usage. Ensure proper authentication and connection limits.",
                    "evidence": {
                        "match": m.group(0),
                        "regex": str(pattern.pattern)
                    }
                }
