#upython
#import usocket as socket
#import uasyncio as asyncio
#import ujson as json
#import machine
#import aHBridge_ESP as dualHbr

import time
import socket
import asyncio
import json
import aHBridge_PCA as dualHbr
from picamera.array import PiRGBArray
from picamera import PiCamera

SERVER = '192.168.0.61'
PORT   = 65432
WIDTH  = 320
HEIGHT = 240
DEPTH  = 3

async def heartbeat(tms):
    #led = machine.Pin(2, machine.Pin.OUT, value=1)
    while True:
        #led(not led())
        #await asyncio.sleep_ms(tms)
        await asyncio.sleep(tms / 1000)

class aRobot:
    def __init__(self, loop):
        self.loop = loop

        self.cam = PiCamera()
        self.cam.resolution = (WIDTH, HEIGHT)
        self.cam.framerate = 24

        self.sreader = []
        self.swriter = []

        self.behaviors = [
            {
                "name":"ESCAPE",
                "prio": 0,
                "ctrl": 0,
                "dcLeft":0,
                "dcRight":0
            },
            {
                "name":"AVOID",
                "prio": 1,
                "ctrl": 0,
                "dcLeft":0,
                "dcRight":0
            },
            {
                "name":"REMOTE_CTRL",
                "prio": 2,
                "ctrl": 0,
                "dcLeft":0,
                "dcRight":0
            },
            {
                "name":"INACTIVE",
                "prio": 3,
                "ctrl": 0,
                "dcLeft":0,
                "dcRight":0
            }
        ]
        self.Vbat = 9.6
        self.dc = [0, 0]
        ##self.dhb = dualHbr.aDualHBridge(14, 0, 4, 5, 1000)
        #self.dhb = dualHbr.aDualHBridge(0, 1, 2, 3, 1000)

    def remote_ctrl(self, left, right):
        #print(left, right)
        self.behaviors[2]["ctrl"] = 1
        self.behaviors[2]["dcLeft"] = left
        self.behaviors[2]["dcRight"]= right

    def arbitrate(self):
        result = sorted([(b["prio"], b["dcLeft"], b["dcRight"]) for b in self.behaviors if b["ctrl"] != 0], key = lambda x: x[0])
        if not result:
            return (0, 0)
            #print('unexpected zeroes')
        else:
            return (result[0][1], result[0][2])
    
    def execute(self, dc):
        if self.dc[0] != dc[0]:
            #self.dhb.duty_m1(self.dc[0] / 5000)
            self.dc[0] = dc[0]

        if self.dc[1] != dc[1]:
            #self.dhb.duty_m2(self.dc[1] / 5000)
            self.dc[1] = dc[1]

    async def register(self):
        try:
            #serv = socket.getaddrinfo(server, port)[0][-1]
            #sock.connect(serv)
            self.sreader, self.swriter = await asyncio.open_connection(SERVER, PORT)
            rsp = '{}\n'.format(json.dumps(['ready', 1]))
            self.swriter.write(rsp.encode())
        except OSError:
            print('Cannot connect to {} on port {}'.format(SERVER, PORT))
            #sock.close()

    async def listen(self):
        while True:
            try:
                res = await self.sreader.readline()
                cmd = json.loads(res)
                s = cmd["Speed"]
                l = r = 50
                if cmd["Angle"] <= 0:
                    #turn left
                    l = 50 + cmd["Angle"] 
                    r = 50
                else:
                    #turn right
                    l = 50
                    r = 50 - cmd["Angle"]                       
                self.remote_ctrl((s * l), (s * r))
            except (ValueError, OSError):
                #swriter.close()
                #await writer.wait_closed()
                return
            await asyncio.sleep(0.02)

    async def detect(self):
        raw = PiRGBArray(self.cam, size=(WIDTH, HEIGHT))
        for frame in self.cam.capture_continuous(raw, format="bgr", use_video_port=True):
            # grab the raw NumPy array representing the image, then initialize the timestamp
            # and occupied/unoccupied text
            img = frame.array
            #print(img.dtype, img.shape)
            self.swriter.write(img.tobytes())
            await self.swriter.drain()
            await asyncio.sleep(0.04)
            # clear the stream in preparation for the next frame
            raw.truncate(0)
    
    async def run(self):
        await self.register()
        self.loop.create_task(self.listen())
        self.loop.create_task(self.detect())
        while True:
            self.Vbat = 6.0#machine.ADC(0).read() * 11 / 1024
            #self.remote_ctrl(512, 512) #pwm range 0:1024
            self.execute(dc = self.arbitrate())
            await asyncio.sleep(0.05)

def start():
    loop = asyncio.get_event_loop()
    robo = aRobot(loop)
    time.sleep(0.1)
    loop.create_task(heartbeat(200)) # Optional fast heartbeat to confirm nonblocking operation

    try:
        loop.run_until_complete(robo.run())
    except KeyboardInterrupt:
        #robo.swriter.close()
        #robo.sreader.close()
        print('Interrupted')  # This mechanism doesn't work on Unix build.