import pyautogui
import os
import asyncio
from keyboard import send
from matplotlib import pyplot as plt
from PIL import Image, ImageDraw, ImageShow

### config

TARGETS = []
PAUSE_ON_FOUND = False

CHEST_IDENTIFICATION_GRAYSCALE = True
CHEST_IDENTIFICATION_CONFIDENCE = .50

GEM_IDENTIFICATION_GRAYSCALE = False # recommend False
GEM_IDENTIFICATION_CONFIDENCE = .85

RESIZE_GEM_IMAGES = False
GEM_IMAGE_RESIZE = (30, 30)

SKIP = True
SKIP_DELAY = 1

# DEBUG
SAVE_TOTEM_SUCCESS = True
SAVE_TOTEM_FAILURE = False

###

PATH = os.getcwd()

if not TARGETS:
    TARGETS = os.listdir(os.path.join(PATH, "gems"))
# GEMS = [os.path.join(PATH, "imgs EXAMPLE", x) for x in os.listdir(os.path.join(PATH, "imgs EXAMPLE"))]

###

async def locate(img, bg, gs = True, conf = .90):
    res = await asyncio.to_thread(pyautogui.locate, img, bg, grayscale=gs, confidence=conf)
    return res


async def locate_gem_slots(screen, gs = CHEST_IDENTIFICATION_GRAYSCALE, conf = CHEST_IDENTIFICATION_CONFIDENCE):
    
    # attempt to get slot locations using chest
    chest = os.path.join(PATH, "assets", "chest.png")
    totem = await locate(chest, screen, gs = gs, conf = conf)
    
    if totem:
        slots = [totem[0], totem[1], totem[2], totem[3]]
        
        # moving top left corner up by 75% of chest height
        slots[1] -= round(totem[3] * 0.75)
        # moving top left corner left by 10% of chest width
        slots[0] -= round(totem[2] * 0.1)
        
        # setting height to 60% of chest height
        slots[3] = round(totem[3] * 0.60)
        # setting width to 125% of chest width
        slots[2] = round(totem[2] * 1.25)
        
        return slots
    
    return False

async def locate_gem(gem, slots, size=GEM_IMAGE_RESIZE, gs = GEM_IDENTIFICATION_GRAYSCALE, conf = GEM_IDENTIFICATION_CONFIDENCE):
    
    gem_img = os.path.join(PATH, "gems", gem)
    
    img = gem_img
    if RESIZE_GEM_IMAGES:
        img = Image.open(gem_img).resize(size)
    
    found = await locate(img, slots, gs = gs, conf=conf)
    
    if found:
        return True
    return False

async def locate_gems(slots, gems = TARGETS):
    found = []
    for gem in gems:
    
        try:
            search = await locate_gem(gem, slots)
        except ValueError as e:
            print(f"Warning: {gem} image too large for slots image {slots}")
            continue
                
        if search:
            found.append(gem)
    
    return found
    
async def pause_or_continue():
    if SKIP:
        send("space")
        await asyncio.sleep(SKIP_DELAY)
    else:
        input("Press Enter to re-scan")
        print("---")
        print("Beginning in 5 seconds")
        await asyncio.sleep(5)

    

async def main():
    
    if SAVE_TOTEM_FAILURE:
        slots_search_failure = 1
    if SAVE_TOTEM_SUCCESS:
        slots_search_success = 1
        
        
    print("Beginning in 5 seconds")
    await asyncio.sleep(5)
    
        
    
    while True:
        screen = pyautogui.screenshot()
        
        slots = await locate_gem_slots(screen)
        
        if not slots:
            print("Failed to locate slots")
            
            if SAVE_TOTEM_FAILURE:
                screen.save(os.path.join(PATH, "debug", f"slots_failed_{slots_search_failure}.png"))
                slots_search_failure += 1
            
            await pause_or_continue()
            continue
        
        slots = screen.crop((slots[0], slots[1],slots[0]+slots[2], slots[1]+slots[3]))
        
        if SAVE_TOTEM_SUCCESS:
            slots.save(os.path.join(PATH, "debug", f"slots_success_{slots_search_success}.png"))
            slots_search_success += 1
        
        gems = await locate_gems(slots)
        
        
        if gems:
            print(f"Found targets: {[os.path.basename(x) for x in gems]}")
            if PAUSE_ON_FOUND:
                input("Press Enter to continue, then click on your game window")
        
        await pause_or_continue()
    
    
# async def main():
    # global totem_search_failure, totem_search_success

    # # sem = asyncio.Semaphore(TASKS)
    
    # chest = os.path.join(PATH, "assets", "chest.png" )
    
    
    # screen = pyautogui.screenshot()
    # totem = await locate(chest, screen)
    
    # if not totem:
        # print("Skipping - Failed to locate totem")
        # if SAVE_TOTEM_FAILURE:
            # screen.save(os.path.join(PATH, "debug", f"failed_{totem_search_failure}.png"))
            # totem_search_failure += 1
    
    # else:
        # if SAVE_TOTEM_SUCCESS:
            # display = ImageDraw.Draw(screen)
            # display.rectangle([(totem[0], totem[1]),(totem[0]+totem[2], totem[1]+totem[3])], outline="red", width=5)
            # screen.save(os.path.join(PATH, "debug", f"success_{totem_search_success}.png"), "PNG")
            # totem_search_success += 1
    
    # send("space")
    # await asyncio.sleep(DELAY)
    
        

if __name__ == "__main__":
    try:
        asyncio.run(main()) 
    except KeyboardInterrupt:
        pass
     