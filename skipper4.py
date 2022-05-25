import pyautogui
import os
import time
import asyncio

### config

CONFIDENCE = .80
GRAYSCALE = True
DELAY = 1
TASKS = 5

###


PATH = os.getcwd()
GEMS = [os.path.join(PATH, "gems", x) for x in os.listdir(os.path.join(PATH, "gems"))]

async def locate(gem, sem, gs = GRAYSCALE, conf = CONFIDENCE):
    async with sem:
        f = await asyncio.to_thread(pyautogui.locateOnScreen, gem, grayscale=gs, confidence=conf)
        # f = pyautogui.locateOnScreen(gem, grayscale=gs, confidence=conf)
    return f


async def main():

    sem = asyncio.Semaphore(TASKS)
    
    while True:
        
        template = os.path.join(PATH, "template.jpg")
        res = await locate(template, sem)
        print(res)
        input()
    
        tasks = [locate(x, sem) for x in GEMS]
        res = await asyncio.gather(*tasks)
        
        for i in range(len(res)):
            if res[i]:
                # print(f"Found {os.path.basename(GEMS[i])}")
                print(res)
        
        print('sleeping')
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())