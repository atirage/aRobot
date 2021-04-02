import machine

class aDualHBridge:
    def __init__(self, m1_1, m1_2, m2_1, m2_2, f):
        #left motor
        pin = machine.Pin(m1_1)
        self.in1 = machine.PWM(pin)
        self.in1.freq(f)
        self.in1.duty(0)
        pin = machine.Pin(m1_2)
        self.in2 = machine.PWM(pin)
        self.in2.freq(f)
        self.in2.duty(0)
        #right motor
        pin = machine.Pin(m2_1)
        self.in3 = machine.PWM(pin)
        self.in3.freq(f)
        self.in3.duty(0)
        pin = machine.Pin(m2_2)
        self.in4 = machine.PWM(pin)
        self.in4.freq(f)
        self.in4.duty(0)

    def duty_m1(self, dc):
        if dc < 0:
            self.in1.duty(0)
            self.in2.duty(int(-dc * 1023))
        else:
            self.in1.duty(int(dc * 1023))
            self.in2.duty(0)

    def duty_m2(self, dc):
        if dc < 0:
            self.in3.duty(0)
            self.in4.duty(int(-dc * 1023))
        else:
            self.in3.duty(int(dc * 1023))
            self.in4.duty(0)

    def freq_all(self, f):
        self.in1.freq(f)
        self.in2.freq(f)
        self.in3.freq(f)
        self.in4.freq(f)