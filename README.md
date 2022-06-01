# kot-skipper

A command line interface tool for the mobile game King of Thieves by ZeptoLab. All rights to the game and it's assets to the rightful owners.

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
Options: window, chest, slot, slot, gems, name, screenshotmode

# Educational Purpose

This is made for educational purposes. Throughout this project I have learnt:

1. Lots about artificial intelligence, different models, optimizer algorithms, loss algorithms, layers, and more. I recommend these resources:  
   https://www.youtube.com/playlist?list=PLOU2XLYxmsII9mzQ-Xxug4l2o04JBrkLV  
   https://www.youtube.com/watch?v=mdKjMPmcWjY

2. Some things about tkinter. This video got me started (first 18 minutes): https://www.youtube.com/watch?v=xuXYKhdoTsw

3. Command line arguments in Python. https://docs.python.org/3/library/argparse.html
