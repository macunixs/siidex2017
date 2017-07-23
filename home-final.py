from gpiozero import LED,MotionSensor,MCP3008,CPUTemperature,OutputDevice,Buzzer,RGBLED,Servo
from time import sleep
from ISStreamer.Streamer import Streamer

import threading # for running multiple processes in parallel at once

## sudo modprobe bcm2835-v4l2
## sudo ./mjpg_streamer -i "./input_uvc.so -f 5 -r 320x160 -n -y" -o "./output_http.so -w ./www -p 8080"


relay1 = OutputDevice(12)
relay2 = OutputDevice(13)

motion = MotionSensor(4)
ldr = MCP3008(1) # light sensor
temp = MCP3008(2) # MCP9700 
ntcw = MCP3008(5) # negative temp coeff white 100K
ntcb = MCP3008(6) # negative temp coeff black 50K
cputemp = CPUTemperature()
sbright = OutputDevice(27)
bz = Buzzer(17)
thresh = 100
auto1 = LED(7)
auto2 = LED(25)


# Initial State bucket name (displayed)
BUCKET_NAME = ":homes: macunixsxv home monitor"
# Initial State bucket key (hidden)
BUCKET_KEY = "macunixsxvhome"
# Initial State access key
ACCESS_KEY = 'VZYQQJ3iiVJxWw0aeX7IooXd6IIsHQUm'


# Variables that ensure we don't stream "Motion 
# Detected" or "No Motion" twice in a row This saves 
# on sent events and processing power
alreadyRecordedMotion = False
alreadyRecordedNoMotion = False
# Initialize the Initial State Streamer
streamer = Streamer(bucket_name=BUCKET_NAME, bucket_key=BUCKET_KEY, access_key=ACCESS_KEY)

class autoLightStatus(threading.Thread):
 
    def __init__(self):
        super(autoLightStatus, self).__init__()
        self.terminated = False
        self.start()
 
    def run(self):
        prev_auto1_state = False
        prev_auto2_state = False
        print ('\n Auto LED status thread started! ')
        while not self.terminated:
            current_auto1_state = auto1.is_lit
            current_auto2_state = auto2.is_lit
            if current_auto1_state != prev_auto1_state:
                if current_auto1_state: # if HIGH LED is active
                    streamer.log(":rotating_light: AutoLED 1 state",":white_check_mark: LED 1 ON")
                    streamer.flush()
                    sleep(1)
                    prev_auto1_state = current_auto1_state
                    
                else:
                    streamer.log(":rotating_light: AutoLED 1 state",":negative_squared_cross_mark: LED 1 OFF")
                    streamer.flush()
                    prev_auto1_state = current_auto1_state
                    sleep(1)
            else:
                sleep(1) # just skip if the value is still the same
                
            if current_auto2_state != prev_auto2_state:
                if current_auto2_state: # if HIGH LED is active
                    streamer.log(":rotating_light: AutoLED 2 state",":white_check_mark: LED 2 ON")
                    streamer.flush()
                    sleep(1)
                    prev_auto2_state = current_auto2_state
                    
                else:
                    streamer.log(":rotating_light: AutoLED 2 state",":negative_squared_cross_mark: LED 2 OFF")
                    streamer.flush()
                    prev_auto2_state = current_auto2_state
                    sleep(1)
            else:
                sleep(1) # just skip if the value is still the same
                
            if self.terminated:
	        break
        print 'Auto LED status thread stopped'



class relayStatus(threading.Thread):
 
    def __init__(self):
        super(relayStatus, self).__init__()
        self.terminated = False
        self.start()
 
    def run(self):
        prev_relay1_state = False
        prev_relay2_state = False
        print ('\n Relay status thread started! ')
        while not self.terminated:
            current_relay1_state = relay1.value
            current_relay2_state = relay2.value
            if current_relay1_state != prev_relay1_state:
                if current_relay1_state: # if LOW relay is active
                    streamer.log(":exclamation: Relay 1 state",":negative_squared_cross_mark: Relay1 Off")
                    streamer.flush()
                    sleep(1)
                    prev_relay1_state = current_relay1_state
                    
                else:
                    streamer.log(":exclamation: Relay 1 state",":white_check_mark: Relay1 On")
                    streamer.flush()
                    prev_relay1_state = current_relay1_state
                    sleep(1)
            else:
                sleep(1) # just skip if the value is still the same
                
            if current_relay2_state != prev_relay2_state:
                if current_relay2_state: # if LOW relay is active
                    streamer.log(":arrow_forward: Relay 2 state",":negative_squared_cross_mark: Relay2 Off")
                    streamer.flush()
                    sleep(1)
                    print('relay 2 off')
                    prev_relay2_state = current_relay2_state
                    
                else:
                    streamer.log(":arrow_forward: Relay 2 state",":white_check_mark: Relay2 On")
                    streamer.flush()
                    prev_relay2_state = current_relay2_state
                    sleep(1)
                    print('relay 2 ON')
            else:
                sleep(1) # just skip if the value is still the same
                
            if self.terminated:
	        break
        print 'Relay status thread stopped'


class cpuSensor(threading.Thread):
 
    def __init__(self):
        super(cpuSensor, self).__init__()
        self.terminated = False
        self.start()
 
    def run(self):
        prev_cpu_temp = 0
        print ('\n CPU sensor thread started! ')
        while not self.terminated:
            current_cpu_temp = cputemp.value * 100
            current_cpu_temp = int(current_cpu_temp)
            
            if current_cpu_temp != prev_cpu_temp:                
                streamer.log(":thermometer: Pi CPU Temp",":computer:{}*C".format(current_cpu_temp))
                streamer.flush()
                prev_cpu_temp = current_cpu_temp
            else:
                pass
            sleep(5)
                
            if self.terminated:
	        break
        print 'CPU Sensor stopped'


class pir(threading.Thread):
 
    def __init__(self):
        super(pir, self).__init__()
        self.terminated = False
        self.start()
 
    def run(self):
        global alreadyRecordedMotion
        global alreadyRecordedNoMotion
        print ('\n motion sensor thread started! ')
        while not self.terminated:
            if motion.motion_detected:
##                print "Motion detected"
                # If we haven't streamed yet:
                if not alreadyRecordedMotion:
                    # Stream to Initial State
                    streamer.log(":spy: Anybody Around?",":runner: Intruder Detected")
                    streamer.flush()
                    alreadyRecordedMotion = True
                    alreadyRecordedNoMotion = False
                else:
                    # Pause the script for 1 
                    # second
                    sleep(1)
            else:
##                print "No motion detected"
                # If we haven't streamed yet:
                if not alreadyRecordedNoMotion:
                    # Stream to Initial State
                    streamer.log(":spy: Anybody Around?",":no_pedestrians: Safe")
                    streamer.flush()
                    alreadyRecordedNoMotion = True
                    alreadyRecordedMotion = False
                else:
                    # Pause the script for 1 
                    # second
                    sleep(1)


        
            if self.terminated:
	        break
        print 'motion Sensor stopped'



# Thread for handling MCP3008 data stream
class readMCP3008(threading.Thread):
 
    def __init__(self):
        super(readMCP3008, self).__init__()
        self.terminated = False
        self.start()
 
    def run(self):
        
        prev_read_ldr = 0
        prev_ntcw_temp = 0
        prev_ntcb_temp = 0
        prev_t1 = 0
        
        print '\nMCP3008 thread started!'
        while not self.terminated:

            current_read_ldr = ldr.raw_value
           
            T1 = 15 * temp.raw_value - 2048 
            current_t1 = T1/100 
            
            current_ntcw_temp = ntcw.raw_value / 18
            current_ntcb_temp = ntcb.raw_value / 18
            
            if current_read_ldr != prev_ntcw_temp:
        
                if current_read_ldr < thresh:
                    sbright.on()
##                    streamer.log(":bulb: Luminance",":bridge_at_night:{}".format(current_read_ldr))
                    streamer.log(":bulb: Luminance",":bridge_at_night: Light ON")
                    streamer.flush()
                else:
                    sbright.off()
##                    streamer.log(":bulb: Luminance",":sunny:{}".format(current_read_ldr))
                    streamer.log(":bulb: Luminance",":sunny: Light OFF")
                    streamer.flush()
                prev_read_ldr = current_read_ldr
                
            else:
                pass
                
            if current_ntcw_temp != prev_ntcw_temp:
                
                if current_ntcw_temp > 30:
                    streamer.log(":thermometer: Room Temp (NTCW)",":fire:{}*C".format(current_ntcw_temp))
                    streamer.flush()
                    bz.on()    
                else:
                    streamer.log(":thermometer: Room Temp (NTCW)",":snowflake:{}*C".format(current_ntcw_temp))
                    streamer.flush()
                    bz.off()
                prev_ntcw_temp = current_ntcw_temp
                
            else:
                pass
            
            if current_ntcb_temp != prev_ntcb_temp:
                
                if current_ntcb_temp > 30:
                    streamer.log(":thermometer: Kitchen Temp (NTCB)",":fire:{}*C".format(current_ntcb_temp))
                    streamer.flush()
                    bz.on()    
                else:
                    streamer.log(":thermometer: Kitchen Temp (NTCB)",":snowflake:{}*C".format(current_ntcb_temp))
                    streamer.flush()
                    bz.off()
                prev_ntcb_temp = current_ntcb_temp
                
            else:
                pass
            
                
            if current_t1 != prev_t1:
                
                if current_t1 > 30:
                    streamer.log(":thermometer: Office Temp (T1)",":fire:{}*C".format(current_t1))
                    streamer.flush()
                    bz.on()    
                else:
                    streamer.log(":thermometer: Office Temp (T1)",":snowflake:{}*C".format(current_t1))
                    streamer.flush()
                    bz.off()
                prev_t1 = current_t1
                
            else:
                pass
    
            sleep(2)
            
            if self.terminated:
	        break
        print '10-bit ADC MCP3008 stopped'

     
if __name__ == "__main__":
    try:
        # Startup sequence
        print 'Initialize all threads!!!!!'
        readMCP3008 = readMCP3008()
        sleep(0.1)
        pir = pir()
        sleep(0.1)
        cpuSensor = cpuSensor()
        sleep(0.1)
        relayStatus = relayStatus()
        sleep(0.1)
        autoLightStatus = autoLightStatus()
        sleep(0.1)

       
        print 'Press CTRL+C to quit...Streaming data to InitialState....'
        running = True
        
        while running:
            sleep(2) # <-- must have something here to make Pi happy =)
    except KeyboardInterrupt:
            print '\nShutting down. Forced by user interrupt!'
    readMCP3008.terminated = True
    readMCP3008.join()
    pir.terminated = True
    pir.join()
    cpuSensor.terminated = True
    cpuSensor.join()
    relayStatus.terminated = True
    relayStatus.join()
    autoLightStatus.terminated = True
    autoLightStatus.join()
    
    print
  

   
    
    

