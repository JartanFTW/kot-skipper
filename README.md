# kot-skipper

A command line interface tool for the mobile game King of Thieves by ZeptoLab. All rights to the game and it's assets to the rightful owners.

This tool allows you to automatically skip through bases for target gold count and/or target gems color/tier.

Currently only Bluestacks has been tested for functionality. Make sure your display resolution in bluestacks settings is set to 1600 x 900 otherwise identification **will** fail.

**You MUST enable android debug bridge in Settings > Advanced**

Example use:
`main.py bluestacks -gd 50000 --gems 4 6 r5 b`

## Arguments

### -h

Displays argument help

### emulator (string)

Which emulator is being used  
Options: bluestacks

### -gd --gold (int)

Pause skipping when this amount of gold is found

### -gm --gems (list)

Pause when any of these gems are found

This parameter accepts multiple formats which can be mixed, including:

1. first letter of color and tier : r1 r2 r3 b1 b2 b3
2. first letter of color : r b y g p  
   This will enable all gems of the entered color
3. tier : 5 6 7 8  
   This will enable all gems of the entered tier

### -r --retries (int)

How many retries to perform on failed identification tasks

### -d --delay (float)

How many seconds to wait between retries and after skipping

### --debug (list)

Enables the program to output images to file during different stages of processing.
Screenshotmode allows the user to use the program to identify gold/gems on-demand. Useful for getting particular debug images.  
Options: window, chest, slot, slot, gems, screenshotmode

# Educational Purpose

This is made for educational purposes. Throughout this project I have learnt:

1. Lots about artificial intelligence, different models, optimizer algorithms, loss algorithms, layers, and more. I recommend these resources:  
   https://www.youtube.com/playlist?list=PLOU2XLYxmsII9mzQ-Xxug4l2o04JBrkLV  
   https://www.youtube.com/watch?v=mdKjMPmcWjY

2. Some things about tkinter. This video got me started (first 18 minutes): https://www.youtube.com/watch?v=xuXYKhdoTsw

3. Command line arguments in Python. https://docs.python.org/3/library/argparse.html

# Inspiration  
  
A thank you to the repository that inspired me: https://github.com/23cku0r/KOT_AUTO_SKIP  
  
# Contact
You can contact me in the [Jartan's Tavern discord server](https://discord.gg/AsU7UPBZMs). We're always accepting new members, so come say hi! https://discord.gg/AsU7UPBZMs  
If you would like to contact me (Jartan) personally, you can do so via any of the following means:  
* Email: jgogox@gmail.com  
* Discord Username: jartan  
* Discord ID: 511608939477991425
