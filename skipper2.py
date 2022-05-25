import pyautogui
import os
import time
import asyncio
from keyboard import send

### config

TARGETS = [""]
CONFIDENCE = .90
GRAYSCALE = False
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
        tasks = [locate(x, sem) for x in GEMS]
        res = await asyncio.gather(*tasks)
        
        # with Pool(len(GEMS)) as pool:
            # res = pool.map(locate, [gem for gem in GEMS])
        for i in range(len(res)):
            if res[i]:
                print(f"Found {os.path.basename(GEMS[i])}")
        if not any(res):
            print("Nothing found!")
        
        # found_gems = []
        # for gem in GEMS:
            # found = 
            # if found:
                # found_gems.append(os.path.basename(gem))
        
        # if found_gems:
            # print(f"Found " + " ".join(found_gems))
            
        await asyncio.sleep(2)
        send("space")
        await asyncio.sleep(DELAY)
        print("---")
        

if __name__ == "__main__":
    while True:
        try:
            asyncio.run(main()) 
        except KeyboardInterrupt:
            input("Press enter to continue")
     