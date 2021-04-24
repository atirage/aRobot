#!/usr/bin/env python3

import threading
import tkinter as tk
import socket
import json
import time
import PIL.Image
import PIL.ImageTk
import numpy as np
import timeit

HOST   = '192.168.0.61'#'localhost'
PORT   = 65432        # Port to listen on (non-privileged ports are > 1023)
WIDTH  = 320
HEIGHT = 240
DEPTH  = 3

cmd =  { "Speed": 0, "Angle": 0}
stop_thr = False

conn = []

#def sel():
#   selection = "Value = " + str(var.get())
#   label.config(text = selection)

def waitConnection(ev, text):
    global conn
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    text.insert(tk.END, "Listening...\n")
    s.listen()
    conn, addr = s.accept()
    text.insert(tk.END, "Connected by " + str(addr))
    # wait for client readiness
    data = conn.recv(1024)
    if not data:
        text.insert(tk.END, "Invalid data!")
        return
    x = json.loads(data)
    if x[0]:
        ev.set()
                    
def sendCommands(ev):
    global conn
    ev.wait()
    while not stop_thr:
        #poll for values
        cmd["Speed"] = scaleS.get()
        cmd["Angle"] = scaleA.get()
        x = '{}\n'.format(json.dumps(cmd))
        conn.sendall(x.encode())
        time.sleep(0.05)

def recvFrames(ev, label):
    global conn
    ev.wait()
    size = 0
    data = b""
    #start_time = timeit.default_timer()
    while not stop_thr:
        chunk = conn.recv(4096)
        l = len(chunk)
        #deserialize after HEIGHT * WIDTH * DEPTH bytes
        if size < (HEIGHT * WIDTH * DEPTH - l):
            data = b"".join([data, chunk])
            size += l
        else:
            #start_time = timeit.default_timer()
            data = b"".join([data, chunk[:HEIGHT * WIDTH * DEPTH - size]])
            cv_img = np.frombuffer(data, dtype=np.uint8).reshape((HEIGHT, WIDTH, DEPTH))
            if l > HEIGHT * WIDTH * DEPTH - size:
                data = chunk[HEIGHT * WIDTH * DEPTH - size:]
            else:
                data = b""   
            size = len(data)
            photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(cv_img))
            label.configure(image=photo)
            label.image = photo
            #print(timeit.default_timer() - start_time)
            #start_time = timeit.default_timer()

top = tk.Tk()
top.title("aRobot GUI")
top.geometry("440x320") 
#var = DoubleVar()
labelR = tk.Label(top, width = 320, height = 240)
canvasL = tk.Canvas(top, width = 120, height = 240)
canvasB = tk.Canvas(top, width = 440, height = 80)
#create widgets
scaleS = tk.Scale(canvasL, from_ = 100, to = -100, label = 'Speed', orient = tk.VERTICAL)#, variable = var )
scaleA = tk.Scale(canvasL, from_ = -50, to = 50, label = 'Steering', orient = tk.HORIZONTAL)
text   = tk.Text(canvasB, height = 4, width = 60)
#place widgets
canvasB.pack(side = tk.BOTTOM)
canvasL.pack(side = tk.LEFT)
labelR.pack(side = tk.RIGHT)
scaleS.pack(side = tk.TOP)
scaleA.pack(side = tk.BOTTOM)
text.pack()

ev = threading.Event()
wait_conn = threading.Thread(target=waitConnection, args=(ev, text,))
send_cmds = threading.Thread(target=sendCommands, args=(ev,))
recv_frms = threading.Thread(target=recvFrames, args=(ev, labelR,))

#button = Button(root, text = "Send", command = sel)
#button.pack(anchor = CENTER)
#label = Label(root)
#label.pack()

wait_conn.start()
send_cmds.start()
recv_frms.start()
top.mainloop()
stop_thr = True
send_cmds.join()  
recv_frms.join() 
