import pyautogui
import os
import asyncio
from keyboard import send
from matplotlib import pyplot as plt
from PIL import Image, ImageDraw, ImageShow
from math import floor

### config

TARGETS = []
PAUSE_ON_FOUND = False

CHEST_IDENTIFICATION_GRAYSCALE = True
CHEST_IDENTIFICATION_CONFIDENCE = .50

GEM_IDENTIFICATION_GRAYSCALE = False # recommend False
GEM_IDENTIFICATION_CONFIDENCE = .85

RESIZE_GEM_IMAGES = True
GEM_IMAGE_SIZE = (30, 30)

SKIP = True
SKIP_DELAY = 0

# DEBUG
SAVE_TOTEM_SUCCESS = False
SAVE_TOTEM_FAILURE = False
SAVE_SLOT_IMAGES = True

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

async def locate_gem(gem, slots, resize = RESIZE_GEM_IMAGES, size=GEM_IMAGE_SIZE, gs = GEM_IDENTIFICATION_GRAYSCALE, conf = GEM_IDENTIFICATION_CONFIDENCE):
    
    gem_img = os.path.join(PATH, "gems", gem)
    
    img = gem_img
    if resize:
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
    

async def identify_gem(gem, resize=RESIZE_GEM_IMAGES, size=GEM_IMAGE_SIZE, minconf = .02):
    compare = [Image.open(os.path.join(PATH, "imgs", x)) for x in os.listdir(os.path.join(PATH, "imgs"))]
    match = None
    confidence = 1
    
    if resize:
        compare2 = []
        for comp in compare:
            if resize:
                image = comp.resize(size)
                image.filename = comp.filename
                compare2.append(image)
        compare = compare2
    
    while not match:
        for comp in compare:
            if await locate(comp, gem, gs=True, conf = confidence):
                match = comp
                break
        
        confidence -= .01
        if confidence < minconf:
            return None
    
    if not match:
        return None
    
    return (os.path.basename(match.filename), confidence)
        
    
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
    if SAVE_SLOT_IMAGES:
        slot_count = 1
        
        
    print("Beginning in 5 seconds")
    await asyncio.sleep(5)
    
        
    
    while True:
        
        await asyncio.sleep(.1)
        screen = pyautogui.screenshot()
        
        # Identify slots
        
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
        
        # Split slots into three sections
        slot_dimensions = []
        x, y = slots.size
        x3, y3 = floor(x/3), floor(y/3)
        slot_dimensions = [(0, 0, x3, y), (x3, 0, x3*2, y), (x3*2, 0, x, y) ]
        
        
        identities = []
        for dimension in slot_dimensions:
            
            slot = slots.crop(dimension)
            res = await identify_gem(slot, minconf = .1)
            if res:
                identities.append(res)
                
                if SAVE_SLOT_IMAGES:
                    slot.save(os.path.join(PATH, "debug", f"{res[0]}_{slot_count}.png"))
                    slot_count += 1
        
        # if SAVE_SLOT_IMAGES:
            # for i in identities:
                # if i:
                    # i[0].save(os.path.join(PATH, "debug", f"slot_{slot_count}.png"))
                    # slot_count += 1
                
        
        print(identities)
        
            
        # gems = await locate_gems(slots)
        
        # if gems:
            # print(f"Found targets: {[os.path.basename(x) for x in gems]}")
            # if PAUSE_ON_FOUND:
                # input("Press Enter to continue, then click on your game window")
        
        await pause_or_continue()
        

if __name__ == "__main__":
    try:
        asyncio.run(main()) 
    except KeyboardInterrupt:
        pass
     