from pynput.keyboard import Listener as K
def on_press(key):
    try:
        if key.char == 'u':
            with open('keyLog.txt','w') as f:
                f.write('1')
        if key.char == 'd':
            with open('keyLog.txt','w') as f:
                f.write('-1')
        if key.char == 'X':
            with open('forceLog.txt','w') as f:
                f.write('1')
        if key.char == 'x':
            with open('forceLog.txt','w') as f:
                f.write('-1')
        if key.char == 'Y':
            with open('forceLog.txt','w') as f:
                f.write('2')
        if key.char == 'y':
            with open('forceLog.txt','w') as f:
                f.write('-2')
        
    except:
        pass
with K(on_press = on_press) as l:
    l.join()
