# Example: Real-time connections
import paho.mqtt.client as mqtt

# MQTT connection
client = mqtt.Client()
client.connect("mqtt.example.com", 1883, 60)
client.publish("test/topic", "Hello MQTT")

# WebSocket (in JS context, but for Python)
import websocket

ws = websocket.create_connection("ws://echo.websocket.org/")
ws.send("Hello WebSocket")
result = ws.recv()
ws.close()
