import serial
import time

ser=serial.Serial("/dev/ttyS0",9600)
ser.baudrate=9600

while True:
    ser.write(b"Send Data/n")
    read_ser=ser.readline().decode('utf-8').rstrip()
    SensorData = read_ser.split(',')
    print(SensorData)
    Luminosity=SensorData[1]
    Distance=SensorData[0]
    print(float(Luminosity))
    print(float(Distance))
    