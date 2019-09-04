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
pull_rate_sleep_time = 1 / 55

def readSerial():
    global pivot_value, tilt_value, running, pull_rate_sleep_time
    
    # Set encoder word width to 16 bit
    pivot.write(b'B16\r')
    tilt.write(b'B16\r')
    while running:
        pivot.write(b'?')
        tilt.write(b'?')
        time.sleep(pull_rate_sleep_time)
        pivot_value = pivot.readline().decode('utf-8')
        tilt_value = tilt.readline().decode('utf-8')

def printSerial():
    global pivot_value, tilt_value, running
    
    old_pivot = -1
    old_tilt = -1
    while running:    
        if old_pivot != pivot_value or old_tilt != tilt_value:
            old_pivot = pivot_value
            old_tilt = tilt_value
            clear()
            print("pivot: {}".format(pivot_value))
            print("tilt: {}".format(tilt_value))
        time.sleep(pull_rate_sleep_time)
        
x = threading.Thread(target=readSerial)
x.start()

# Uncomment to enable CLI output
#y = threading.Thread(target=printSerial)
#y.start()


async def emitSerialDataToWebSocket(websocket, path):
    global pivot_value, tilt_value, running, pull_rate_sleep_time
    print("Client Connected")
    try:
        old_pivot = -1
        old_tilt = -1
        while running:
            if old_pivot != pivot_value or old_tilt != tilt_value:
                old_pivot = pivot_value
                old_tilt = tilt_value
                await websocket.send('{{"pivot":{},"tilt":{}}}'.format(old_pivot, old_tilt))
            await asyncio.sleep(pull_rate_sleep_time)
    except:
        print("Client Disconnected")

start_server = websockets.serve(emitSerialDataToWebSocket, "0.0.0.0", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
print("Server started")
asyncio.get_event_loop().run_forever()
