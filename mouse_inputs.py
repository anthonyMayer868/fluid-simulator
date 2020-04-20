from pynput.mouse import Listener
from pynput.keyboard import Listener as K 

with Listener() as listener:
    listener.join
click_pos = [0,0,0,0]

def on_click(x,y,button,pressed):
    global click_pos
    if pressed:
        click_pos[0] = str(x)
        click_pos[1] = str(y)
    if pressed == False:
        click_pos[2] = str(x) 
        click_pos[3] = str(y)
        with open('log.txt','w') as f:
            f.write(click_pos[0]+','+click_pos[1]+','+click_pos[2]+','+click_pos[3])


def on_move(x,y):
    pass 

def on_scroll(x,y,dx,dy):
    with open('scrollLog.txt','r') as f:
        y = int(f.read())
    with open('scrollLog.txt','w') as f:
        f.write(str(y+dy))



with Listener(on_move = on_move,on_click=on_click,on_scroll=on_scroll) as listener:
    listener.join()

