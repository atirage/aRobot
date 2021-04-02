#!/usr/bin/env python3

import threading
import tkinter as tk
import socket
import json
import time

HOST = '192.168.0.101'
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

cmd =  { "Speed": 0, "Angle": 0}
stop_thr = False

#def sel():
#   selection = "Value = " + str(var.get())
#   label.config(text = selection)

def handleConnection():
    ready = False
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        print('Listening...')
        s.listen()
        conn, addr = s.accept()
        print('Connected by ', addr)
        with conn:
            while True:
                if stop_thr:
                    break
                if not ready:
                    # wait for client readiness
                    data = conn.recv(1024)
                    if not data:
                        break
                    x = json.loads(data)
                    ready = x[0]
                else:
                    #poll for values
                    cmd["Speed"] = scaleS.get()
                    cmd["Angle"] = scaleA.get()
                    x = '{}\n'.format(json.dumps(cmd))
                    conn.sendall(x.encode())
                    time.sleep(0.05)

thr = threading.Thread(target=handleConnection, args=())
top = tk.Tk()
top.geometry("200x180") 
#var = DoubleVar()
scaleS = tk.Scale(top, from_ = 100, to = -100, label = 'Speed', orient = tk.VERTICAL)#, variable = var )
scaleA = tk.Scale(top, from_ = -50, to = 50, label = 'Steering', orient = tk.HORIZONTAL)
scaleS.pack(side = tk.TOP)
scaleA.pack(side = tk.BOTTOM)
#button = Button(root, text = "Send", command = sel)
#button.pack(anchor = CENTER)
#label = Label(root)
#label.pack()

thr.start()
top.mainloop()
stop_thr = True
thr.join()          
