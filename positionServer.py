import serial
import time
import os
import threading
import asyncio
import websockets

pivot = serial.Serial('COM6', 9600,  timeout=0)
tilt = serial.Serial('COM4', 9600,  timeout=0)
clear = lambda: os.system('cls')

pivot_value = 0
tilt_value  = 0
running = True

def readSerial():
    global pivot_value, tilt_value, running
    while running:
        pivot.write(b'?')
        tilt.write(b'?')
        time.sleep(0.01)
        pivot_value = str(pivot.readline())[3:-3]
        tilt_value = str(tilt.readline())[3:-3]

def printSerial():
    global pivot_value, tilt_value, running
    while running:
        clear()
        print("pivot: {}".format(pivot_value))
        print("tilt: {}".format(tilt_value))
        time.sleep(0.1)
        
x = threading.Thread(target=readSerial)
x.start()

#y = threading.Thread(target=printSerial)
#y.start()


async def emitSerialDataToWebSocket(websocket, path):
    global pivot_value, tilt_value, running
    print("Client Connected")
    try:
        while running:
            await websocket.send('{pivot: ' + str(pivot_value) + ", tilt: " + str(tilt_value) + "}")
            await asyncio.sleep(0.1)
    except:
        print("Client Disconnected")

start_server = websockets.serve(emitSerialDataToWebSocket, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
print("Server started")
asyncio.get_event_loop().run_forever()
