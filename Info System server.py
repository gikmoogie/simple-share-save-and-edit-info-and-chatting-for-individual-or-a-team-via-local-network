# _______auther: moogiegik
# pip install --upgrade flask flask-socketio python-socketio
# make sure that flask and flask-socketio”s versions are matched ，or program may not work well，and trough errors。
# try update both
from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, emit, send
# _______auther: moogiegik
import logging
import time

from info import infoDataManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.secret_key = 'trade'  # 密钥用于会话加密
socketio = SocketIO(app)
# connections = 0
app.config['connections'] = 0

# 配置日志
# logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.ERROR)
app.logger.addHandler(logging.StreamHandler())
# _______auther: moogiegik

# socketio________________________________________________________
@socketio.on('connect')
def test_connect():
    app.config['connections'] += 1
    app.logger.info('Client connected ‑> %s', app.config['connections'])
    emit('server_response', {'data': 'Connected'})
    emit('id', {'data': app.config['connections']})

@socketio.on('disconnect')
def test_disconnect():
    app.config['connections'] -= 1
    app.logger.info('Client disconnected ‑> %s', app.config['connections'])
# _______auther: moogiegik

@socketio.on('message')
def handle_message(msg):
    print('Message received: ' + msg)
    app.logger.info('handle_message: %s', msg)
    send(msg, broadcast=True)
    # emit('message_Json', msg, broadcast=True, include_self=True)
    # emit('message', msg, broadcast=True, include_self=True)

@socketio.on('message_Json')
def handle_message_Json(data):
    app.logger.info('handle_message_Json: %s', data['type'])
    # 广播给所有人
    # send(data, broadcast=True, json=True)
    # send("msg", broadcast=True)
    # json=True 等价于 emit('message', data, broadcast=True)
    # emit('message_Json', data, broadcast=True)
    emit('message_Json', data, broadcast=True, include_self=True)
# _______auther: moogiegik
# chat________________________________________________________
@app.route("/")
def home():
    return render_template("home.html")

# chat________________________________________________________
@app.route("/chat")
def chat():
    return render_template("chat.html")

# info________________________________________________________
@app.route("/info")
def info():
    return render_template("info.html")
@app.route('/info/infoSimpleReqest', methods=['POST'])
def infoSimpleReqest():
    json = request.get_json()
    try:
        # return jsonify(json)
        # app.logger.debug("This is a debug messageadd1111") # not work
        # app.logger.info("This is an info message2222")
        # app.logger.warning("This is a warning message")
        # app.logger.info("info request on flask:json:",json,"json,s data:",json.get("data"))

        return jsonify(infoDataManager.Start(json))
    
    except ValueError:
        return jsonify({'error': 'Invalid input. Please provide a valid number.'}), 400
# _______auther: moogiegik
# explore IP________________________________________________________
@app.route('/info/getIP', methods=['POST'])
def getIP():
    try:
        return infoDataManager.Get_Local_IP()
    except ValueError:
        return jsonify({'error': 'get ip failed'}), 400

if __name__ == '__main__':
    # app.run(debug=True)
    socketio.run(app, host='0.0.0.0',port=5005,debug=True,allow_unsafe_werkzeug=True)