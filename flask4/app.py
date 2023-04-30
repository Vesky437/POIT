from threading import Lock
from flask import Flask, render_template, session, request, jsonify, url_for
from flask_socketio import SocketIO, emit, disconnect  
import time
import MySQLdb
import configparser as ConfigParser
import random
import math
import serial

async_mode = None

app = Flask(__name__)

config = ConfigParser.ConfigParser()
config.read('config.cfg')
myhost = config.get('mysqlDB', 'host')
myuser = config.get('mysqlDB', 'user')
mypasswd = config.get('mysqlDB', 'passwd')
mydb = config.get('mysqlDB', 'db')
print(myhost)


app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock() 

ser=serial.Serial("/dev/ttyS0",9600)
ser.baudrate=9600
#global ardEvent
def background_thread(args):
    count = 0
    Luminosity = 0
    Distance= 0
    global ardEvent
    ardEvent = 0
    global dbEvent   
    dbEvent=0 
    dataList = []     
    db = MySQLdb.connect(host=myhost,user=myuser,passwd=mypasswd,db=mydb)          
    dataCounter = 0 
    while True:
        ser.reset_output_buffer()
        ser.reset_input_buffer()
        ser.write(str(ardEvent).encode('utf-8'))
        if ardEvent == 1:
            read_ser=ser.readline()
            Str_ser = read_ser.decode('utf-8')
            SensorData = Str_ser.split(',')
            #print(SensorData)
            Luminosity=SensorData[1]
            Distance=SensorData[0]
            #print(float(Luminosity))
            #print(float(Distance))
            count += 1
            
        
        if args:
          A = dict(args).get('A')
          btnV = dict(args).get('btn_value')
          #btnV = 'wtf'
        else:
          A = 1
          btnV = 'null'
        
        if dbEvent == 1:
          dataDict = {
            "t": time.time(),
            "Distance": float(Distance),
            "Luminosity": float(Luminosity)}
          dataList.append(dataDict)
          if len(dataList)>0:
            #print(str(dataList))
            fuj = str(dataList).replace("'", "\"")
            #print(fuj)
            cursor = db.cursor()
            cursor.execute("SELECT MAX(id) FROM data")
            maxid = cursor.fetchone()
            cursor.execute("INSERT INTO data (id, hodnoty) VALUES (%s, %s)", (maxid[0] + 1, fuj))
            db.commit()
          dataList = []
        
          
                
        
        #print(args)  
        socketio.sleep(1)

        
        
        
        if ardEvent == 1:
            socketio.emit('my_response',
                      {'Distance': float(Distance), 'Luminosity': float(Luminosity), 'count': count, 'btn': float(ardEvent)},
                      namespace='/test') 
        # else:
            # socketio.emit('my_response',
                      # {'Distance': float(0), 'Luminosity': float(0), 'count': count, 'btn': str(btnV)},
                      # namespace='/test') 
    db.close()        

@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)
       
@app.route('/graphlive', methods=['GET', 'POST'])
def graphlive():
    return render_template('graphlive.html', async_mode=socketio.async_mode)
    
@app.route('/db')
def db():
  db = MySQLdb.connect(host=myhost,user=myuser,passwd=mypasswd,db=mydb)
  cursor = db.cursor()
  cursor.execute('''SELECT  hodnoty FROM  data WHERE id=1''')
  rv = cursor.fetchall()
  return str(rv)   

@app.route('/dbdata/<string:num>', methods=['GET', 'POST'])
def dbdata(num):
  db = MySQLdb.connect(host=myhost,user=myuser,passwd=mypasswd,db=mydb)
  cursor = db.cursor()
  print(num)
  cursor.execute("SELECT hodnoty FROM  data WHERE id=%s", num)
  rv = cursor.fetchone()
  return str(rv[0])

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



@socketio.on('stop_btn', namespace='/test')
def Start_btn_message(message):
    global ardEvent   
    ardEvent=0 
    
@socketio.on('start_btn', namespace='/test')
def Stop_btn_message(message):
    global ardEvent   
    ardEvent=1 
    
@socketio.on('stop_db', namespace='/test')
def Start_btn_message(message):
    global dbEvent   
    dbEvent=0 
    
@socketio.on('start_db', namespace='/test')
def Stop_btn_message(message):
    global dbEvent   
    dbEvent=1 

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=80, debug=True)
