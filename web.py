from gpiozero import MCP3008,LED,RGBLED,DistanceSensor,Servo,Buzzer,MotionSensor,CPUTemperature
from time import sleep 
import threading

from flask import Flask,render_template
from flask_socketio import SocketIO

PORT_NUM = 5000

app = Flask(__name__)
socketio = SocketIO(app)

@app.route("/")
def index():
    return render_template('home.html')

@socketio.on('set_servo_pos')
def set_servo(state):
    print("servo pos: {}".format(state))
    
@socketio.on('setred')
def set_red(state):
    if state == 1:
        rgb.color = (0,1,1)
    if state == 0:
        rgb.on()

    print("Red LED: {}".format(rgb.value))

@socketio.on('setgreen')
def set_green(state):
    if state == 1:
        rgb.color = (1,0,1)
    if state == 0:
        rgb.on()

    print("Green LED: {}".format(rgb.value))

@socketio.on('setblue')
def set_blue(state):
    if state == 1:
        rgb.color = (1,1,0)
    if state == 0:
        rgb.on()

    print("Blue LED: {}".format(rgb.value))

cputemp = CPUTemperature()
pir = MotionSensor(4)
bz = Buzzer(17)
servo = Servo(12)
rgb = RGBLED(16,20,21)
hcsr = DistanceSensor(echo=6,trigger=5)
pot = MCP3008(0) # Pot is connected to CH0 
ldr = MCP3008(1) # LDR is connected to CH1
temp35 = MCP3008(2) #LM35
temp2 = MCP3008(3)
temp3 = MCP3008(4)
ntc1 = MCP3008(5)
ntc2 = MCP3008(6)
led = LED(26) 
thresh = 300 # set threshold level

# Thread for handling HC-SR04 data stream
class cpuSensor(threading.Thread):
 
    def __init__(self):
        super(cpuSensor, self).__init__()
        self.terminated = False
        self.start()
 
    def run(self):
                
        print ('\n CPU sensor thread started! ')
        while not self.terminated:
            cpusuhu = cputemp.value * 100
            print('cpu temp:{}'.format(cpusuhu))
            sleep(1)
            socketio.emit('cputemp', int(cpusuhu))
        
            if self.terminated:
	        break
        print 'CPU Sensor stopped'



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
      
        print '\nMCP3008 thread started! Reading input channels....'
        while not self.terminated:
            # grab all available input from 
            # MCP3008
            read_pot = pot.raw_value
            read_ldr = ldr.raw_value

            t35 = 0.322*temp35.raw_value 
            T1 = 15 * temp2.raw_value - 2048 
            T2 = 15 * temp3.raw_value - 2048
            T1 = T1/100
            T2 = T2/100
            ntc1_temp = ntc1.raw_value / 18
            ntc2_temp = ntc2.raw_value / 18
            socketio.emit('pot', int(read_pot))
            socketio.emit('ldr', int(read_ldr))
            socketio.emit('t35', int(t35))
	    socketio.emit('t1',int(T1))
	    socketio.emit('t2',int(T2))
	    socketio.emit('ntc1',ntc1_temp)
	    socketio.emit('ntc2',ntc2_temp)

            if read_ldr < thresh:
                led.on()
                bz.on()
            else:
                led.off()
                bz.off()
            sleep(0.5)
	
            if self.terminated:
	        break
        print '10-bit ADC MCP3008 stopped'

# Thread for handling HC-SR04 data stream
class distance(threading.Thread):
 
    def __init__(self):
        super(distance, self).__init__()
        self.terminated = False
        self.start()
 
    def run(self):
        global dist
        
        print ('\n HCSR04 thread started! ')
        while not self.terminated:
            # grab input from 
            # HCSR04
            dist = hcsr.distance * 100
            sleep(1)
            socketio.emit('dist', int(dist))
            
	
            if self.terminated:
	        break
        print 'HC-SR04 Distance Sensor stopped'

# Thread for handling PIR data stream
class motion(threading.Thread):
 
    def __init__(self):
        super(motion, self).__init__()
        self.terminated = False
        self.start()
 
    def run(self):
    
        
        print ('\n PIR thread started! ')
        while not self.terminated:
##            if pir.motio_detected:
##                print('motion detected!')
##                socketio.emit('motion', pir.motion_detected)
##            else:
##                print('no movement')
##                socketio.emit('motion', pir.motion_detected)        
            socketio.emit('motion', pir.motion_detected)
            if pir.motion_detected:
                bz.on()
            else:
                bz.off()
            sleep(1)
            
	
            if self.terminated:
	        break
        print 'Motion Sensor stopped'
        
if __name__ == "__main__":
    try:
        # Startup sequence
        print 'Initialize all threads!!!!!'

        readMCP3008 = readMCP3008()
        sleep(1)
        distance = distance()
        sleep(1)
        motion = motion()
        sleep(1)
        cpuSensor = cpuSensor()
        sleep(1)
       
        rgb.on() # make sure the RGB is turned off
        print 'Press CTRL+C to quit'
        
        print("\nStarting web application at port:{}".format(PORT_NUM))
        socketio.run(app,host='0.0.0.0', port=PORT_NUM, debug=True)
        running = True
        
        while running:
            print("\nPot:{:.2f} LDR:{:.2f}nits t1:{}C t2:{}C LM35:{}C ntc1:{}C ntc2:{}C distance:{}".format(read_pot,read_ldr,T1,T2,t35,ntc1_temp,ntc2_temp,dist))
            sleep(1)
            if read_ldr < thresh:
                led.on()
                rgb.color = (1,0,1)
            else:
                led.off()
                rgb.on()
    except KeyboardInterrupt:
            print '\nShutting down...'
    readMCP3008.terminated = True
    readMCP3008.join()
    distance.terminated = True
    distance.join()
    motion.terminated = True
    motion.join()
    cpuSensor.terminated = True
    cpuSensor.join()
    
    print
  

