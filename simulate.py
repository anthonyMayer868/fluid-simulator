import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from fluid_nographics import *
import subprocess
from screeninfo import get_monitors
import sys

'''
NOTE: THE MATPLOTLIB WINDOW MUST BE IN FULL SCREEN FOR THIS PROGRAM TO WORK CORRECTLY.
      
      REQUIRES: pynput (pip install pynput). screeninfo (pip install screeninfo).

      I've run the program succesfully in python3 it should work for python2
      as well. I tested the script on ubuntu and windows 10. 
      linues 71 through 76 will porbabily cause an error on mac.

      This program runs an interactive simulation of fluid flow by calling two subprocesses to monitor
      keyboard and mouse inputs.

      To create new particles click within the matplotlib window and drag the mouse in the direction you want 
      the particles to move. The velocity of the particles will be proportional to the distance the mouse was dragged.
      The particle will be centered about the point where the click began. 

      Scroll up with the mouse scroller to increase viscosity. Scoll down to decrease. 

      Press the 'u' key to increase the time step and the 'd' key to decrease.
      
      Capital 'X' will increase force in the x direction, 'x' will decrease force in the x direction.
              'Y' will increase force in the y direction, 'y' will decrease force in the y direction.


      The terminal will continously print out the values for the viscosity, time step, and Force of the system.   


      Initial parameters:
            
            time step = .25
            viscosity = 0
            N = 52
            Force = (0,0)

'''
#Need monitor Dimensions for proper conversion of cordinates.
#I have no idea if the screeninfo module works on mac or windows.
#may need to hard code monitor height and width.
m = get_monitors()[0]
width = m.width - 1
height = m.height - 1


#intialize files that will log mouse and keyboard actions
#mouse_inputs.py will log relavent mosue actions.
# key_input.py will log relavent keyboard inputs 
with open('forceLog.txt','w') as f:
    #Tracks how the user wants to change the forces.
    # 0 -> no change in force
    # 1 -> fx += .02
    #-1 -> fx -= .02
    # 2 -> fy += .02
    #-2 -> fy -= .02
    f.write('0')

with open('log.txt','w') as f:
    #Tracks how the user wants to add particles.
    f.write('0')

with open('scrollLog.txt','w') as f:
    #Tracks how the user wants to increase or decrease viscosity.
    f.write('0')

#start subprocesses.
if sys.version_info[0]< 3 or sys.platform=='win32': #check python version and operating system
    mouse_listen = subprocess.Popen(['python', 'mouse_inputs.py'])
    key_listen = subprocess.Popen(['python', 'key_input.py'])
else:
    mouse_listen = subprocess.Popen(['python3', 'mouse_inputs.py'])
    key_listen = subprocess.Popen(['python3', 'key_input.py'])

#Initialize fluid simulator.
fs = FluidSimulator(visc=0)
fs.add_particle(0,0,10,10,.1)
fs.time_step()
fig, ax = plt.subplots()
#initialize image for animation
img = plt.imshow(np.random.rand(52,52))


def init():
    img = plt.imshow((np.random.rand(52,52)))
    return [img]

def update(frame):
    #read in data from log files to see what the user wants to happen in the simulation.
    #after rewrite the log file to '0' so the same input isnt run more than once.
    #try statemant is just in case the other scripts are operating on the same file at 
    #the same time in this case just '' are read in. 
    with open('forceLog.txt','r') as f:
        try:
            df = int(f.read())
        except:
            df = 0
    with open('forceLog.txt','w') as f:
        f.write('0')
    with open('keyLog.txt','r') as f:
        try:
            dt = int(f.read())
        except:
            dt = 0
    with open('keyLog.txt','w') as f:
        f.write('0')
    with open('scrollLog.txt','r') as f:
        try:
            dv = int(f.read())
        except:
            dv = 0
    with open('scrollLog.txt','w') as f:
        f.write('0')
    with open('log.txt','r') as f:
        try:
            click = f.read()
        except:
            click = '0'
    with open('log.txt','w') as f:
        f.write('0')

    #update parameters based on log files.
    if len(click) > 1:
        pos = click.split(',')
        x0 = int(pos[0])
        y0 = int(pos[1])
        x1 = int(pos[2])
        y1 = int(pos[3])
        if (x0>int(.7*(width+1)) or x0<(.3261*(width+1))) or (y0>int(.8463*(height+1)) or y0<int(.1815*(height+1))):
            #clicks out side the plot window will be ignored
            #these values are for 1980x1020 displays.
            pass
        else:
           #change cordinates
            cx = (width)/2  #x position of center of screen
            cy = (height)/2 #y posiiton of center 
            x = (x0-cx)/(.7*(width+1)-.3261*(width+1)) #scale 
            y = (y0-cy)/(.8463*(height+1)-.1815*(height+1))#scale 
            fs.add_particle(x,y,1e-2*(x1-x0),1e-2*(y1-y0),.08)
            
    fs.visc += 10*dv
    if fs.dt + .01*dt <0:
        #keeping the time steps positive
        pass 
    else:
        fs.dt += .01*dt
    if df == 1:
        fs.A.x = fs.A.x + .02
        fs.ax += .02
    if df == -1:
        fs.A.x = fs.A.x - .02
        fs.ax -= .02
    if df == -2:
        fs.A.y = fs.A.y - .02
        fs.ay -= .02
    if df == 2:
        fs.A.y = fs.A.y + .02
        fs.ay += .02
    
    #show current values of paramters in the terminal
    print('viscosity ',fs.visc,'time step: ',fs.dt,'Force: ',(fs.ax,fs.ay))
    #take a time step
    img.set_data(fs.rho)
    fs.time_step()
    return [img]

ani = FuncAnimation(fig, update, frames=80,
                    init_func=init, blit=True)
plt.show()
mouse_listen.kill()
key_listen.kill()
