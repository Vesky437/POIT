from threading import Lock
from flask import Flask, render_template, session, request, jsonify, url_for
from flask_socketio import SocketIO, emit, disconnect  
import time
import random
import math
import serial

async_mode = None

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock() 

ser=serial.Serial("/dev/ttyS0",9600)
ser.baudrate=9600

def background_thread(args):
    count = 0
    ardEvent = 1    
    dataList = []          
    while True:
        ser.reset_output_buffer()
        ser.write(str(ardEvent).encode('utf-8'))
        read_ser=ser.readline()
        Str_ser = read_ser.decode('utf-8')
        SensorData = Str_ser.split(',')
        #print(SensorData)
        Luminosity=SensorData[1]
        Distance=SensorData[0]
        #print(float(Luminosity))
        #print(float(Distance))
        
        if args:
          A = dict(args).get('A')
          btnV = dict(args).get('btn_value')
          btnV = 'wtf'
          
        else:
          A = 1
          btnV = 'null'
          
        if btnV == 'start':
            ardEvent = 1
        if btnV == 'Stop':
            ardEvent = 0
        
        
        print(args)  
        socketio.sleep(2)
        count += 1
        prem = math.sin(count)
        prem2 = math.cos(count)
        dataDict = {
          "t": time.time(),
          "x": count,
          "y": float(A)*prem,
        }
        dataList.append(dataDict)
        #if len(dataList)>0:
        #  print(str(dataList))
        #  print(str(dataList).replace("'", "\""))
        
        if ardEvent == 1:
            socketio.emit('my_response',
                      {'Distance': float(Distance), 'Luminosity': float(Luminosity), 'count': count, 'btn': str(btnV)},
                      namespace='/test') 
        if ardEvent == 0:
            socketio.emit('my_response',
                      {'Distance': float(0), 'Luminosity': float(Luminosity), 'count': count},
                      namespace='/test') 
        

@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)
       
@app.route('/graphlive', methods=['GET', 'POST'])
def graphlive():
    return render_template('graphlive.html', async_mode=socketio.async_mode)
      
@socketio.on('my_event', namespace='/test')
def test_message(message):   
#    session['receive_count'] = session.get('receive_count', 0) + 1 
    session['A'] = message['value']    
#    emit('my_response',
#         {'data': message['value'], 'count': session['receive_count']})
 
@socketio.on('disconnect_request', namespace='/test')
def disconnect_request():
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']})
    disconnect()

@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread, args=session._get_current_object())
#    emit('my_response', {'data': 'Connected', 'count': 0})



@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)
    
@socketio.on('btn_event', namespace='/test')
def db_message(message):   
    session['btn_value'] = message['value']  

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=80, debug=True)
