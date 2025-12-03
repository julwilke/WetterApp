import socketio

print("Client-skript gestartet")

#Socket.IO-Client mit etwas Logging
sio = socketio.Client()

@sio.event
def connect():
    print("✅ Verbunden mit Socket.IO-Server")
    #Stadt direkt senden
    sio.emit("cityInput", {"city": "Hamburg"})

@sio.event
def connect_error(data):
    print("❌ Verbindung fehlgeschlagen:", data)

@sio.event
def disconnect():
    print("🔌 Vom Server getrennt")

@sio.on("update")
def on_update(data):
    print("📡 Update vom Server:", data)

if __name__ == "__main__":
    sio.connect("http://127.0.0.1:5000")
    sio.wait()