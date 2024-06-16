from flask import Flask, request, jsonify
import socket
import time
import threading

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def hello():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)    
    return f"Hello from {hostname} with IP address {ip_address}!"

@app.route('/reverse', methods=['POST'])
def reverse_text():
    time.sleep(2)
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    data = request.json
    if 'text' in data:
        reversed_text = ' '.join(word[::-1] for word in data['text'].split())
        return jsonify({
            'reversed_text': reversed_text,
            'hostname': hostname,
            'ip_address': ip_address
        })
    else:
        return jsonify({'error': 'No text provided'}), 400

@app.route('/cpu-intensive', methods=['GET'])
def cpu_intensive():
    def cpu_task():
        end_time = time.time() + 8
        while time.time() < end_time:
            pass  # Busy-wait to simulate CPU load

    thread = threading.Thread(target=cpu_task)
    thread.start()
    thread.join()  # Wait for the thread to complete

    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return jsonify({
        'message': 'CPU intensive task completed',
        'hostname': hostname,
        'ip_address': ip_address
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)