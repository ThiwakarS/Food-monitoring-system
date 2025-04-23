from flask import Flask, render_template, jsonify, request, redirect, url_for, Response
from flask_socketio import SocketIO, emit
from functools import wraps
import logging

app = Flask(__name__, static_folder='static')
socketio = SocketIO(app)
logging.basicConfig(level=logging.DEBUG)
# Global variables to store the latest sensor data
sensor_data = {
    "device_id": "2871960d23457820",
    "ds18b20": 0,
    "dht11": 0,
    "humidity": 0,
    "air_quality": 0,
    "latitude": 0,
    "longitude": 0
}

def check_auth(username, password):
    """Check if a username/password combination is valid."""
    return username == 'Admin' and password == 'Dragon@123'

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route('/')
@requires_auth
def index():
    return render_template('index_2.html')


@app.route('/', methods=['POST'])
def update():
    global sensor_data

    data = request.json
    if data and data.get("device_id") == "2871960d234578207634329863206876":
        sensor_data.update(data)
        socketio.emit('sensor_update', sensor_data)
        print(data)
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "failed"}), 400

@socketio.on('connect')
def handle_connect():
    auth = request.authorization
    if auth and check_auth(auth.username, auth.password):
        emit('sensor_update', sensor_data)
        print("data changed")
    else:
        return False  # Reject the connection if not authenticated

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8080, debug=True, allow_unsafe_werkzeug=True)