import time
import os
import threading
import asyncio
import websockets
from tkinter import *
from functools import partial

clear = lambda: os.system('cls')

pivot_value = 0
tilt_value  = 0
running = True
pull_rate_sleep_time = 1 / 55


encoderOffsetX = 37000
encoderOffsetY = 44000

encoderMaxX = encoderOffsetX + 20000
encoderMaxY = encoderOffsetY + 10000

overflowValue = 65535

def setPivotvalue(val):
    global pivot_value
    pivot_value = val
    
def setTiltvalue(val):
    global tilt_value
    tilt_value = val


class GUI(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.start()

    def callback(self):
        self.root.quit()

    def run(self):
        self.root = Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.callback)

        label = Label(self.root, text="PositionServerTester")
        label.pack()
        x = Scale(self.root, from_=encoderOffsetX, to=encoderMaxX, command=setPivotvalue)
        x.pack()
        y = Scale(self.root, from_=encoderOffsetY, to=encoderMaxY, orient='horizontal', command=setTiltvalue)
        y.pack()

        self.root.mainloop()


async def runGui(root, interval=0.01):
    while True:
        root.update()
        await asyncio.sleep(interval)

async def emitSerialDataToWebSocket(websocket, path):
    global pivot_value, tilt_value, running, pull_rate_sleep_time, overflowValue
    print("Client Connected")
    try:
        old_pivot = -1
        old_tilt = -1
        while running:
            if old_pivot != pivot_value or old_tilt != tilt_value:
                old_pivot = pivot_value
                old_tilt = tilt_value
                await websocket.send('{{"pivot":{},"tilt":{}}}'.format((old_pivot % overflowValue), (old_tilt % overflowValue)))
            await asyncio.sleep(pull_rate_sleep_time)
    except:
        print("Client Disconnected")

start_server = websockets.serve(emitSerialDataToWebSocket, "0.0.0.0", 8765)

app = GUI()
print('Now we can continue running code while mainloop runs!')

asyncio.get_event_loop().run_until_complete(start_server)
print("Server started")

asyncio.get_event_loop().run_forever()