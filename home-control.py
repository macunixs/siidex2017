from gpiozero import MCP3008,LED,DistanceSensor
from time import sleep 
import threading

hcsr = DistanceSensor(echo=6,trigger=5)
pot = MCP3008(0) # Pot is connected to CH0 
ldr = MCP3008(1) # LDR is connected to CH1
temp35 = MCP3008(2) #LM35
temp2 = MCP3008(3)
temp3 = MCP3008(4)
ntc1 = MCP3008(5)
ntc2 = MCP3008(6)
led = LED(26) 
thresh = 0.5 # set threshold level

# Thread for handling MCP3008 data stream
class readMCP3008(threading.Thread):
 
    def __init__(self):
        super(readMCP3008, self).__init__()
        self.terminated = False
        self.start()
 
    def run(self):
        global read_pot
        global read_ldr
        global t35
        global T1
        global T2
        global ntc1_temp
        global ntc2_temp
        print '\nMCP3008 started! Reading input channels....'
        while not self.terminated:
            # grab all available input from 
            # MCP3008
            read_pot = pot.raw_value
            read_ldr = ldr.value

            t35 = 0.322*temp35.raw_value 
            T1 = 15 * temp2.raw_value - 2048 
            T2 = 15 * temp3.raw_value - 2048
            T1 = T1/100
            T2 = T2/100
            ntc1_temp = ntc1.raw_value / 18
            ntc2_temp = ntc2.raw_value / 18
            

            sleep(0.5)
	
            if self.terminated:
	        break
        print 'MCP3008 stopped'

# Thread for handling HC-SR04 data stream
class distance(threading.Thread):
 
    def __init__(self):
        super(distance, self).__init__()
        self.terminated = False
        self.start()
 
    def run(self):
        global dist
        
        print '\n HCSR04 started! ....'
        while not self.terminated:
            # grab input from 
            # HCSR04
            dist = hcsr.distance * 100
            sleep(0.5)
	
            if self.terminated:
	        break
        print 'HC-SR04 Distance Sensor stopped'
# Startup sequence
print 'Initialize MCP3008' 
readMCP3008 = readMCP3008()
distance = distance()

if __name__ == "__main__":
    try:
        print 'Press CTRL+C to quit'
        running = True
        read_pot = 0
        read_ldr = 0
        t35 = 0
        T1 = 0
        T2 = 0
        dist = 0.00
        ntc1_temp = 0
        ntc2_temp = 0
        while running:
            print("\nPot:{:.2f} LDR:{:.2f}nits t1:{}C t2:{}C LM35:{}C ntc1:{}C ntc2:{}C distance:{}".format(read_pot,read_ldr,T1,T2,t35,ntc1_temp,ntc2_temp,dist))
            sleep(0.1)
            if read_ldr < thresh:
                led.on()
            else:
                led.off()
    except KeyboardInterrupt:
            print '\nShutting down...'
    readMCP3008.terminated = True
    readMCP3008.join()
    distance.terminated = True
    distance.join()
    print
  
