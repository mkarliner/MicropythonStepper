from machine import Pin
import time
import uasyncio as asyncio
import network
import binascii
import asyn

# (c) IDWizard 2017
# MIT License.

async def connect():
    station = network.WLAN(network.STA_IF)
    station.active(True)
    station.connect("mihome", "electr1c")
    while(station.isconnected() != True):
        await asyncio.sleep(1)
    print(station.ifconfig())
    mac = station.config('mac')
    last = binascii.hexlify(mac)[-4:].decode("ascii")
    print("ping me on PYBD{}.local".format(last))
    



LOW = 0
HIGH = 1
FULL_ROTATION = int(4075.7728395061727 / 8) # http://www.jangeox.be/2013/10/stepper-motor-28byj-48_25.html
DEFAULT_SPEED = 300

HALF_STEP = [
    [LOW, LOW, LOW, HIGH],
    [LOW, LOW, HIGH, HIGH],
    [LOW, LOW, HIGH, LOW],
    [LOW, HIGH, HIGH, LOW],
    [LOW, HIGH, LOW, LOW],
    [HIGH, HIGH, LOW, LOW],
    [HIGH, LOW, LOW, LOW],
    [HIGH, LOW, LOW, HIGH],
]

FULL_STEP = [
 [HIGH, LOW, HIGH, LOW],
 [LOW, HIGH, HIGH, LOW],
 [LOW, HIGH, LOW, HIGH],
 [HIGH, LOW, LOW, HIGH]
]

# class Command():
#     """Tell a stepper to move X many steps in direction"""
#     def __init__(self, stepper, steps, direction=1):
#         self.stepper = stepper
#         self.steps = steps
#         self.direction = direction

# class Driver():
#     """Drive a set of motors, each with their own commands"""
# 
#     @staticmethod
#     async def run(commands):
#         """Takes a list of commands and interleaves their step calls"""
#         
#         # Work out total steps to take
#         max_steps = sum([c.steps for c in commands])
# 
#         count = 0
#         while count != max_steps:
#             for command in commands:
#                 # we want to interleave the commands
#                 if command.steps > 0:
#                     await command.stepper.step(1, command.direction)
#                     command.steps -= 1
#                     count += 1
#                     print('Step')
        
class Stepper():
    def __init__(self, mode, pinno1, pinno2, pinno3, pinno4, speed=DEFAULT_SPEED):
        self.mode = mode
        self.pin1 = Pin(pinno1,Pin.OUT)
        self.pin2 = Pin(pinno2,Pin.OUT)
        self.pin3 = Pin(pinno3,Pin.OUT)
        self.pin4 = Pin(pinno4,Pin.OUT)
        self.position = 0
 
        self.delay = int(1000/speed)  # Recommend 10+ for FULL_STEP, 1 is OK for HALF_STEP
                                 # speed is 1-1000 == 1000 - 1 millisecond delay
        
        # Initialize all to 0
        self.reset()
        
    async def step(self, count, direction=1):
        """Rotate count steps. direction = -1 means backwards"""
        for x in range(count):
            for bit in self.mode[::direction]:
                self.pin1.value(bit[0]) 
                self.pin2.value(bit[1]) 
                self.pin3.value(bit[2]) 
                self.pin4.value(bit[3]) 
                await asyncio.sleep_ms(self.delay)
                self.position += direction
        self.reset()
        
    async def move(self, direction=1, speed=DEFAULT_SPEED):
        print('moving %d' % direction)
        self.moving = True
        while(self.moving):
            await self.step(1, direction)
            
    def stop(self):
        print('Stopping')
        self.moving = False
            
        
    def setSpeed(self,speed):
        self.delay = 1000/speed
        
    def reset(self):
        # Reset to 0, no holding, these are geared, you can't move them
        self.pin1.value(0) 
        self.pin2.value(0) 
        self.pin3.value(0) 
        self.pin4.value(0)
        
    def position(self):
        return self.position
        
class Limits():
    def __init__(self, minLimitPinNo, maxLimitPinNo):
        pass
#         self.minLimitPin = Pin(minLimitPinNo,Pin.IN)
#         self.maxLimitPin = Pin(maxLimitPinNo,Pin.IN)


if __name__ == '__main__':
    
    readOK = asyn.Event()
    
    async def hello():
        while(True):
            tim = time.time()
            print("Mike %d " % tim)
            await asyncio.sleep(1)
            
    async def bounce():
        while(True):
            print('bounce forward')
            asyncio.create_task(s1.move(1, 300))
            print('wait')
            await asyncio.sleep(10)
            print('bounce stop')
            s1.stop()
            await asyncio.sleep(1)
            print('bounce backwards')
            asyncio.create_task(s1.move(-1, 300))
            await asyncio.sleep(10)
            print('bounce stop')
            s1.stop()
            await asyncio.sleep(1)
            
    readr = None
    writr = None
    stepper = None
    
    async def servercb(reader, writer):
        global stepper
        global readr
        global writr
        global loop
        readr = reader
        writr = writer
        loop.create_task(sendMessage(writer))
        loop.create_task(rxMessage(reader))
        print(writer)
        loop.create_task(sendPosition(s1, writer, reader))
        print('Connection made')
        writer.write('Hello telnet'.encode())
        await writer.drain()

    async def sendMessage(writer):
        count = 0
        while True:
#             writer.write(('Hello telnet %d' % count).encode())
#             await writer.drain()
            await asyncio.sleep(10)
            count += 1
            
    
    async def rxMessage(reader):
        global readOK
        while True:
            buf = await reader.readline()
            if(len(buf) == 0):
                return
            msg = buf.rstrip().decode('utf-8')
            print(msg)
            if(msg == 'OK'):
                readOK.set()
            elif(msg == 'moveLeft'):
                s1.stop()
                asyncio.create_task(s1.move(1))
            elif(msg == 'moveRight'):
                s1.stop()
                asyncio.create_task(s1.move(-1))
            elif(msg == 'stop'):
                s1.stop()
            else:
                print('Bad cmd: %s' % msg)
            
                
                    
            
    async def sendPosition(stepper, writer, reader):
        global readOK
        oldPosition = 0
        while True:
            newPosition = stepper.position
            if(newPosition != oldPosition):  
                writer.write('position:%d:' % stepper.position)
                print('position: %d\n' % stepper.position)
                await asyncio.sleep_ms(100)
                await writer.drain()
                await readOK
                readOK.clear()
                print("LEN: %d" % len(writer.out_buf))
                oldPosition = newPosition
            else:
                await asyncio.sleep_ms(100)
            
            

    loop = asyncio.get_event_loop()
    s1 = Stepper(HALF_STEP, 12, 14, 27, 26, speed=300)
    s1.limits = Limits(25, 26)
    #s2 = Stepper(HALF_STEP, microbit.pin6, microbit.pin5, microbit.pin4, microbit.pin3, delay=5)   
    #s1.step(FULL_ROTATION)
    #s2.step(FULL_ROTATION)
    loop = asyncio.get_event_loop()
    asyncio.run(connect())
    
    server = asyncio.start_server(servercb, '0.0.0.0', 2323, backlog=10)
    
    #runner = Driver()
    #loop.create_task(runner.run([Command(s1, FULL_ROTATION, 1)]))
    #loop.create_task(s1.move(1, 300))

            
    loop.create_task(server)
#     loop.create_task(hello())
#     loop.create_task(bounce())
    loop.run_forever()
    loop.close()
#     asyncio.run(runner.run([Command(s1, FULL_ROTATION, 1)]))
#     asyncio.run(hello())