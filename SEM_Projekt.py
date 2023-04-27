import serial
import time

ser=serial.Serial("/dev/ttyS0",9600)
ser.baudrate=9600

while True:
    read_ser=ser.readline()
    print(read_ser)
#     for i in range(0, 10):
#         if str(read_ser)(i)==' ':
#             for j in range(0, i):
#                 DistanceCM=read_ser(j)
    values= read_ser.split(" ")
    print(values)
    