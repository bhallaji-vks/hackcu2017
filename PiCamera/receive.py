import socket
import os

UDP_IP = "10.202.45.166"
UDP_Port = 5005
print ("Processing End Raspberry Pi")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_Port))
while True:
    data, addr = sock.recvfrom(1024)
    print ("Received Trigger from Customer End Raspberry Pi!! \n", data)
    #os.system("raspistill -o name1.jpg")
    
 
