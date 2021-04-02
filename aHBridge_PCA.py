import Adafruit_PCA9685

class aDualHBridge:
    def __init__(self, m1_1, m1_2, m2_1, m2_2, f):
        self.pwm = Adafruit_PCA9685.PCA9685()
        self.pwm.set_pwm_freq(f)
        self.in1 = m1_1
        self.in2 = m1_2
        self.in3 = m2_1
        self.in4 = m2_2
        self.freq = f

    def duty_m1(self, dc):
        if dc < -0.95:
            cv_on1  = 0
            cv_off1 = 4096
            cv_on2  = 4096
            cv_off2 = 0
        elif -0.95 <= dc < -0.05:
            cv_on1  = 0
            cv_off1 = 4096
            cv_on2  = int(2048 * (1 + dc))
            cv_off2 = int(2048 * (1 - dc))
        elif -0.05  <= dc < 0.05:
            cv_on1  = 0
            cv_off1 = 4096
            cv_on2  = 0
            cv_off2 = 4096
        elif  0.05  <= dc < 0.95:
            cv_on1  = int(2048 * (1 - dc))
            cv_off1 = int(2048 * (1 + dc))
            cv_on2  = 0
            cv_off2 = 4096
        else:            
            cv_on1  = 4096
            cv_off1 = 0
            cv_on2  = 0
            cv_off2 = 4096

        self.pwm.set_pwm(self.in1, cv_on1, cv_off1)
        self.pwm.set_pwm(self.in2, cv_on2, cv_off2)
    
    def duty_m2(self, dc):
        if dc < -0.95:
            cv_on3  = 0
            cv_off3 = 4096
            cv_on4  = 4096
            cv_off4 = 0
        elif -0.95 <= dc < -0.05:
            cv_on3  = 0
            cv_off3 = 4096
            cv_on4  = int(2048 * (1 + dc))
            cv_off4 = int(2048 * (1 - dc))
        elif -0.05  <= dc < 0.05:
            cv_on3  = 0
            cv_off3 = 4096
            cv_on4  = 0
            cv_off4 = 4096
        elif  0.05  <= dc < 0.95:
            cv_on3  = int(2048 * (1 - dc))
            cv_off3 = int(2048 * (1 + dc))
            cv_on4  = 0
            cv_off4 = 4096
        else:            
            cv_on3  = 4096
            cv_off3 = 0
            cv_on4  = 0
            cv_off4 = 4096

        self.pwm.set_pwm(self.in3, cv_on3, cv_off3)
        self.pwm.set_pwm(self.in4, cv_on4, cv_off4)
    
    def freq_all(self, f):
        self.freq = f
        self.pwm.set_pwm_freq(f)