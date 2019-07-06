#!/usr/bin/python
#client send the video stream via a webcam
import socket
import cv2
import numpy
import re
import numpy as np
import os
from PIL import Image
import pygame
from pygame.locals import *
import sys
from googletrans import Translator
import urllib.request

## google translator
translator = Translator()

##naver speech tts api
client_id = "sdGe3hd5Zd1LFdS0f6ri"
client_secret = "xn2sKZehbX"
url = "https://openapi.naver.com/v1/voice/tts.bin"
request = urllib.request.Request(url)
request.add_header("X-Naver-Client-Id",client_id)
request.add_header("X-Naver-Client-Secret",client_secret)

NUM_TO_SHOW = 3

def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf

TCP_IP = 'localhost'
TCP_PORT = 5001
BUFFER_SIZE = 1024
RECEIVE_FILE = 'myTransfer.txt'
PATH = os.path.expanduser('./') + RECEIVE_FILE

sock = socket.socket()
sock.connect((TCP_IP, TCP_PORT))

pygame.init()
pygame.display.set_caption("OpenCV camera stream on Pygame")
screen = pygame.display.set_mode([640,480])
font = pygame.font.Font("NanumBarunGothic.ttf", 15)
DISPLAY=pygame.display.set_mode((500,400),0,32)
WHITE=(255,255,255)
blue=(0,0,255)
DISPLAY.fill(WHITE)

capture = cv2.VideoCapture(0)
try:
    while True:
        
        ### First, send raw webcam video stream
        ret, frame = capture.read()
        encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),90]
        result, imgencode = cv2.imencode('.jpg', frame, encode_param)
        data = numpy.array(imgencode)
        stringData = data.tostring()
        stringLength = str(len(stringData))
        sock.sendall(stringLength.encode('utf-8'))
        sock.sendall( stringData );
        while sock.recv(2048).decode('utf-8') != u"ack":
            #print ("waiting for ack")
            pass
        #print ("ack received!")


        ### Second, receive the jason data from the deep learning server 
        #if os.path.exists(PATH):
            #      os.remove(PATH)
        #with open(PATH, 'wb') as file_to_write:
        length = sock.recv(2048).decode('utf-8')
        #print('length: ', length)
        stringData = recvall(sock, int(length))
        #print(stringData)
        #print(type(stringData))
        stringData = stringData.decode('utf-8')
        # Third, draw rectangles and texts    
        # lines = ''.join( file_to_write.readlines() )
        posText = re.findall('[\d.E+-]+', stringData)
        del posText[0]
        del posText[0]
        captionPos = np.array(posText, float)
        m = int(np.size(captionPos,0) / 4)
        n = int(4)
        captionPos = np.reshape( captionPos, (m,n) )
        captionText = re.findall(r'\"(.+?)\"', stringData)
        del captionText[0]
        del captionText[0]
        del captionText[0]
        if len(captionText) > 1:
            del captionText[len(captionText)-1]    


        screen.fill([0,0,0])
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = np.rot90(frame)
        frame = pygame.surfarray.make_surface(frame)
        screen.blit(frame, (0,0))
        pygame.display.update()


        for i in range(0, NUM_TO_SHOW):
            capPos = captionPos[i]
            x1 = int(round(capPos[0]))
            y1 = int(round(capPos[1]))
            x2 = int(round(x1 + capPos[2]))
            y2 = int(round(x2 + capPos[3]))
            pygame.draw.rect(screen,blue,pygame.Rect(x1, y1, x2, y2), 1)
            capStr = translator.translate(captionText[i], dest='ko')
            text = font.render(capStr.text, True, (0, 255, 0))
            screen.blit(text, (x1,y1))
            pygame.display.flip()
#            encText = urllib.parse.quote(transStr)
#            data = "speaker=mijin&speed=0&text=" + encText;
#            response = urllib.request.urlopen(request, data=data.encode('utf-8'))
#            rescode = response.getcode()
        

        
        
        
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                capture.release()
                sock.close()
                cv2.destroyAllWindows() 
                sys.exit(0)
                
except (KeyboardInterrupt,SystemExit):
    pygame.quit()


sock.close()
cv2.destroyAllWindows()     


 

