# servo handler
from flask import Flask,render_template,request
from flask_socketio import SocketIO
from gpiozero import Servo,RGBLED, OutputDevice,LED
from time import sleep

PORT_NUM = 5000
tilt = Servo(23)
pan = Servo(24)
##rgb = RGBLED(16,20,21)
count = 0
relay1 = OutputDevice(12)
relay2 = OutputDevice(13)
red = LED(16)
green = LED(20)
blue = LED(21)
prev_state = False
relay1.on() # active low 
relay2.on() # active low
auto1 = LED(7)
auto2 = LED(25)
control = False

app = Flask(__name__)
socketio = SocketIO(app)

@app.route("/")
def index():
    return render_template('home.html')

    
@socketio.on('LEDcontrol')
def set_superbright(state):
    print(state)
    if state == "auto":
        for i in range(3):   
            auto1.on()
            auto2.on()
            sleep(1)
            auto1.off()
            auto2.off()
            sleep(1)
            
    if state == "manual":
       
        auto1.toggle()
        auto2.toggle()
        
    
@socketio.on('setred')
def set_red(state):

    red.toggle()
    green.on()
    blue.on()
       

@socketio.on('setgreen')
def set_green(state):

    red.on()
    green.toggle()
    blue.on()
        
@socketio.on('setblue')
def set_blue(state):

    red.on()
    green.on()
    blue.toggle()


@app.route("/relay/<string:state>", methods=['POST'])
def relay(state):
    # Check if the led state is 0 (off) or 1 (on) and set the LED accordingly.
    if state == 'relay1toggle':
        relay1.toggle()
        print 'relay1 toggled'
    
    if state == 'relay2toggle':
        relay2.toggle()
        print 'relay2 toggled'
    return ('', 204)
      
    

@app.route("/servo/<string:state>", methods=['POST'])
def servo(state):
    # Check if the led state is 0 (off) or 1 (on) and set the LED accordingly.
    global count
    if state == 'center':
        if count == 0:
            tilt.mid()
            pan.mid()
            print 'center pressed'
          
        else:
            pass
        
    elif state == 'up':
        tilt.min()
        pan.mid()
        print 'up pressed'
        
    elif state == 'down':
        tilt.max()
        pan.mid()
        print 'down pressed'
        
    elif state == 'left':
        tilt.mid()
        pan.min()
        print 'left pressed'
        
    elif state == 'right':
        tilt.mid()
        pan.max()
        print 'right pressed'
        
    else:
        return ('Unknown Servo state', 400)
    
    sleep(5)
    #tilt.detach()
    #pan.detach()
    #count = 0
    return ('', 204)
       
    
if __name__ == "__main__":
    try:
        # Startup sequence
##        rgb.color = (1,1,1)
        red.on()
        green.on()
        blue.on()
        tilt.detach()
        pan.detach()
        socketio.run(app,host='0.0.0.0', port=PORT_NUM, debug=True)
        running = True
        
        while running:
##            rgb.color = (1,1,1)
            red.on()
            green.on()
            blue.on()
            sleep(2) # <-- must have something here to make Pi happy =)
    except KeyboardInterrupt:
##        rgb.color = (1,1,1)
        print '\nShutting down. Forced by user interrupt!'
 
    
    print
