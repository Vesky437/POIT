import serial
import time

ser=serial.Serial("/dev/ttyS0",9600)
ser.baudrate=9600
#ser.reset_input_buffer()

while True:
    ser.write("2".encode('utf-8'))
    read_ser=ser.readline().decode('utf-8').rstrip()
    print(read_ser)
    SensorData = read_ser.split(',')
    print(SensorData)
    Luminosity=SensorData[1]
    Distance=SensorData[0]
    print(float(Luminosity))
    print(float(Distance))
    time.sleep(1)