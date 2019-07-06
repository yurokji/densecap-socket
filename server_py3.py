#!/usr/bin/python
import socket
import cv2
import numpy
import re
import numpy as np

NUM_TO_SHOW = 3

BUFFER_SIZE = 1024

input_dir = 'webcam/inputs/'
output_dir = 'webcam/outputs/'

def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf

TCP_IP = '0.0.0.0'
TCP_PORT = 5001

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.bind((TCP_IP, TCP_PORT))
socket.listen(True)
conn, addr = socket.accept()
while True:
	
	### First, receive raw webcam video stream
	length = conn.recv(2048).decode('utf-8')
	#print('length: ', length)
	stringData = recvall(conn, int(length))
	data = numpy.fromstring(stringData, dtype='uint8')
	decimg=cv2.imdecode(data,1)
	cv2.imwrite('cam_image.jpg', decimg)	
	cv2.waitKey(1)
	conn.send("ack".encode('utf-8'))

	### second, send the json data after deep learning the images 
	with open(output_dir+'cam_image.json', 'rb') as file_to_send:
		stringData = file_to_send.read()
		stringLength = str(len(stringData))
		conn.sendall(stringLength.encode('utf-8'))
		conn.sendall( stringData )
	#print ("Sending finished")

	#cv2.imshow('SERVER',decimg)
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break	
		
socket.close()
cv2.destroyAllWindows() 



