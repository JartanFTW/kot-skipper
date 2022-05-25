import pyautogui
import os
from PIL import Image
import time

PATH = os.getcwd()
TOLERANCE = 1

TLP = (95, 196, 0)
BRP = (255, 129, 67)

TARGET_LIMIT = 1


def find_unique_color(l1, l2):
    for color in l1:
        if color not in l2:
            return color

def remove_all_values(l, v):
    try:
        while True:
            l.remove(v)
    except ValueError:
        return l

def remove_duplicates(l1, l2):
    l11 = l1
    l22 = l2
    for x in l1:
        if x in l2:
            remove_all_values(l11, x)
            remove_all_values(l22, x)
    return l11, l22

def remove_gem_duplicates(gems, sc_colors):
    LEN = len(gems)
    final_gems = gems
        
    i = 0
    for gem1 in gems:
        for gem2 in gems[i+1:]:
            remove_duplicates(gem1[1], gem2[1])
        remove_duplicates(gem1[1], sc_colors)
        i += 1
            

def remove_duplicate_individual(l):
    ll = []
    for x in l:
        if x not in ll:
            ll.append(x)
    l = ll


def load_image_filters():
    dir = os.path.join(PATH, "filter")
    filter = []
    
    for file in os.listdir(dir):
        img = Image.open(os.path.join(dir, file))
        
        colors = img.getcolors(maxcolors = 50000)
        colors.sort(reverse = True, key = lambda x : x[0])
        colors = [x[1] for x in colors]
        
        for color in colors:
            if color not in filter:
                filter.append(color)
    
    return filter

def match(c1, c2, t):
    if not (c1[0] > c2[0] - t and c1[0] < c2[0] + t):
        return False
    if not (c1[1] > c2[1] - t and c1[1] < c2[1] + t):
        return False
    if not (c1[2] > c2[2] - t and c1[2] < c2[2] + t):
        return False
    print(str(c1) + " " + str(c2))
    return True

def load_gem_imgs():
    dir = os.path.join(PATH, "imgs")
    filter = []
    
    # sc = pyautogui.screenshot()
    # sc_colors = sc.getcolors(maxcolors = 3000000)
    # sc_colors.sort(reverse=True, key= lambda x : x[0])
    # sc_colors = [x[1] for x in sc_colors.copy()]
    # filter += sc_colors
    
    print("Loading filter images")
    filter += load_image_filters()
    
    print("Removing duplicate colors")
    remove_duplicate_individual(filter)
    
    
    gems = []
    for file in os.listdir(dir):
        img = Image.open(os.path.join(dir, file))
        
        name = file[:-4]
        
        colors = img.getcolors(maxcolors = 5000)
        colors.sort(key = lambda x : x[0])
        colors = [x[1] for x in colors]
        
        target_colors = []
        for color in colors:
            if color not in filter:
                target_colors.append(color)
                
                if len(target_colors) >= TARGET_LIMIT:
                    break
        
        filter = target_colors + filter
        
        gems.append([name, target_colors])
    
    # for i in range(len(gems)):
        # gem = gems[i]
        
        # try:
            # all_colors = sum([x[1] for x in gems[i+1:]], [])
        # except IndexError:
            # all_colors = []
        # all_colors += filter
        
        # remove_duplicate_individual(all_colors)
        
        # # gems[i][1], all_colors = remove_duplicates(gems[i][1], all_colors)
        # gems[i][1] = find_unique_color(gems[i][1], all_colors)
    
    return gems
    
# def locate_game():
    
    # sc = pyautogui.screenshot()
    # sc_colors = sc.getcolors(3000000)
    # for color in sc_colors:
        # if color[1] == TLP:
            # print(f"TL: {color}")
        # if color[1] == BRP:
            # print(f"BR: {color}")
    
    

print("Loading gem images")
gems = load_gem_imgs()

for gem in gems:
    print(f"{gem[0]} : " + str(gem[1]))

while True:
    
    sc = pyautogui.screenshot()
    sc_colors = sc.getcolors(maxcolors = 3000000)
    sc_colors.sort(reverse=False, key= lambda x : x[0])
    sc_colors = [x[1] for x in sc_colors.copy()]
    # remove_duplicate_individual(sc_colors)
    
    for gem in gems:
        
        for target in gem[1]:
            for sc_pix in sc_colors:
                if match(target, sc_pix, TOLERANCE):
                    print(f"Found {gem[0]} gem!")
        
        # if any(gem[1]) in sc_colors:
            # print(f"Found {gem[0]} gem!")
    
    input("Press enter to re-scan.")