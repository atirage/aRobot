import usocket as socket
import uasyncio as asyncio
import ujson
import machine

server = '192.168.0.101'
port = 65432

async def heartbeat(tms):
    led = machine.Pin(2, machine.Pin.OUT, value=1)
    while True:
        led(not led())
        await asyncio.sleep_ms(tms)

async def listen(robo):
    sock = socket.socket()
    try:
        serv = socket.getaddrinfo(server, port)[0][-1]
        sock.connect(serv)
    except OSError:
        print('Cannot connect to {} on port {}'.format(server, port))
        sock.close()
        return
    swriter = asyncio.StreamWriter(sock, {})
    await swriter.awrite('{}\n'.format(ujson.dumps(['ready', 1])))
    while True:
        sreader = asyncio.StreamReader(sock)
        while True:
            try:
                res = await sreader.readline()
            except OSError:
                sock.close()
                return
            try:
                cmd = ujson.loads(res)
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
                robo.remote_ctrl((s * l * 1023) // 5000,
                                 (s * r * 1023) // 5000)
            except ValueError:
                sock.close()
                return
            await asyncio.sleep_ms(20)

class aRobot:
    def __init__(self):
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
        #left motor
        pin = machine.Pin(14)
        self.in1 = machine.PWM(pin)
        self.in1.freq(1000)
        self.in1.duty(0)
        pin = machine.Pin(0)
        self.in2 = machine.PWM(pin)
        self.in2.freq(1000)
        self.in2.duty(0)
        #right motor
        pin = machine.Pin(4)
        self.in3 = machine.PWM(pin)
        self.in3.freq(1000)
        self.in3.duty(0)
        pin = machine.Pin(5)
        self.in4 = machine.PWM(pin)
        self.in4.freq(1000)
        self.in4.duty(0)

    def remote_ctrl(self, left, right):
        #print(left, right)
        self.behaviors[2]["ctrl"] = 1
        self.behaviors[2]["dcLeft"] = (1023 * left) // 100
        self.behaviors[2]["dcRight"]= (1023 * right ) // 100

    def arbitrate(self):
        result = sorted([(b["prio"], b["dcLeft"], b["dcRight"]) for b in self.behaviors if b["ctrl"] != 0], key = lambda x: x[0])
        if not result:
            return (0, 0)
            #print('unexpected zeroes')
        else:
            return (result[0][1], result[0][2])
    
    def execute(self, dc):
        if self.dc[0] != dc[0]:
            self.dc[0] = dc[0]
            if dc[0] < 0:
                self.in1.duty(0)
                self.in2.duty(-dc[0])
            else:
                self.in1.duty(dc[0])
                self.in2.duty(0)
        if self.dc[1] != dc[1]:
            self.dc[1] = dc[1]
            if dc[1] < 0:
                self.in3.duty(0)
                self.in4.duty(-dc[1])
            else:
                self.in3.duty(dc[1])
                self.in4.duty(0)

    async def run(self):
        while True:
            self.Vbat = machine.ADC(0).read() * 11 / 1024
            #self.remote_ctrl(512, 512) #pwm range 0:1024
            self.execute(dc = self.arbitrate())
            await asyncio.sleep_ms(50)

def start():
    robo = aRobot()
    loop = asyncio.get_event_loop()
    loop.create_task(heartbeat(200)) # Optional fast heartbeat to confirm nonblocking operation
    loop.create_task(listen(robo))
    try:
        loop.run_until_complete(robo.run())
    except KeyboardInterrupt:
        print('Interrupted')  # This mechanism doesn't work on Unix build.