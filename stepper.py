from machine import Pin
import time
import uasyncio as asyncio

# (c) IDWizard 2017
# MIT License.



LOW = 0
HIGH = 1
FULL_ROTATION = int(4075.7728395061727 / 8) # http://www.jangeox.be/2013/10/stepper-motor-28byj-48_25.html

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

class Command():
    """Tell a stepper to move X many steps in direction"""
    def __init__(self, stepper, steps, direction=1):
        self.stepper = stepper
        self.steps = steps
        self.direction = direction

class Driver():
    """Drive a set of motors, each with their own commands"""

    @staticmethod
    async def run(commands):
        """Takes a list of commands and interleaves their step calls"""
        
        # Work out total steps to take
        max_steps = sum([c.steps for c in commands])

        count = 0
        while count != max_steps:
            for command in commands:
                # we want to interleave the commands
                if command.steps > 0:
                    await command.stepper.step(1, command.direction)
                    command.steps -= 1
                    count += 1
                    print('Step')
        
class Stepper():
    def __init__(self, mode, pinno1, pinno2, pinno3, pinno4, delay=2):
        self.mode = mode
        self.pin1 = Pin(pinno1,Pin.OUT)
        self.pin2 = Pin(pinno2,Pin.OUT)
        self.pin3 = Pin(pinno3,Pin.OUT)
        self.pin4 = Pin(pinno4,Pin.OUT)
 
        self.delay = delay  # Recommend 10+ for FULL_STEP, 1 is OK for HALF_STEP
        
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
        self.reset()
        
    def reset(self):
        # Reset to 0, no holding, these are geared, you can't move them
        self.pin1.value(0) 
        self.pin2.value(0) 
        self.pin3.value(0) 
        self.pin4.value(0) 

if __name__ == '__main__':
    
    async def hello():
        while(True):
            tim = time.time()
            print("Mike %d " % tim)
            await asyncio.sleep(1)

    loop = asyncio.get_event_loop()
    s1 = Stepper(HALF_STEP, 12, 14, 27, 26, delay=5)    
    #s2 = Stepper(HALF_STEP, microbit.pin6, microbit.pin5, microbit.pin4, microbit.pin3, delay=5)   
    #s1.step(FULL_ROTATION)
    #s2.step(FULL_ROTATION)
    loop = asyncio.get_event_loop()
    
    runner = Driver()
    loop.create_task(runner.run([Command(s1, FULL_ROTATION, 1)]))
    loop.create_task(hello())
    loop.run_forever()
    loop.close()
#     asyncio.run(runner.run([Command(s1, FULL_ROTATION, 1)]))
#     asyncio.run(hello())