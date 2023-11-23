# app.py
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import threading
import time
import pygetwindow as gw
import base64

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")  # Allow connections from any origin

# Use a threading.Event for graceful thread shutdown
stop_computer_recording = threading.Event()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    emit('message', {'data': 'Connected'})

@socketio.on('disconnect')
def handle_disconnect():
    stop_computer_recording.set()  # Signal the recording thread to stop
    emit('message', {'data': 'Disconnected'})

@socketio.on('start_computer_recording')
def start_computer_recording():
    if not stop_computer_recording.is_set():
        emit('message', {'data': 'Computer recording is already in progress'})
    else:
        stop_computer_recording.clear()  # Clear the event to allow recording
        threading.Thread(target=record_computer_screen).start()
        emit('message', {'data': 'Computer recording started'})

@socketio.on('stop_computer_recording')
def stop_computer_recording():
    if stop_computer_recording.is_set():
        emit('message', {'data': 'No computer recording in progress'})
    else:
        stop_computer_recording.set()  # Signal the recording thread to stop
        emit('message', {'data': 'Computer recording stopped'})

def record_computer_screen():
    while not stop_computer_recording.is_set():
        try:
            window = gw.getWindowsWithTitle('Your App Title')[0]
            screenshot = window.screenshot()
            img_str = base64.b64encode(screenshot.tobytes()).decode('utf-8')
            socketio.emit('screenshot', {'image': img_str})
            time.sleep(1)
        except Exception as e:
            print(f"Error in recording thread: {e}")

if __name__ == '__main__':
    socketio.run(app, port=5001)
