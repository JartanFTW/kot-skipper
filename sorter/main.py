import tkinter as tk
import os
from PIL import Image, ImageTk

PATH = os.getcwd()

UNSORTED = [
    os.path.join(PATH, "unsorted", x)
    for x in os.listdir(os.path.join(PATH, "unsorted"))
]
GEMS = [os.path.join(PATH, "gems", x) for x in os.listdir(os.path.join(PATH, "gems"))]


def setup_root():

    root = tk.Tk()
    root.title("Sorter")

    width, height = root.winfo_screenwidth(), root.winfo_screenheight()

    root.geometry(f"400x500+{int(width/2)}+{int(height/2)}")

    root.resizable(False, False)

    return root


def main():
    root = setup_root()
    root_x, root_y = root.size()

    tk.Label(
        root,
        text="Click the correct gem",
        anchor=tk.CENTER,
        borderwidth=1,
        padx=10,
        pady=5,
        font=("Helvetica", 14),
    ).pack()

    ##

    button_locations = []
    y = 480
    for i in range(5):
        y -= 40
        x = 0
        for i in range(8):
            x += 40
            button_locations.append((x, y))

    ##

    buttons = []
    for gem in GEMS:
        print(gem)
        image = ImageTk.PhotoImage(image=Image.open(gem).resize((40, 40)))
        button = tk.Button(
            root,
            image=image,
        )
        print(
            button_locations[len(buttons)][0],
            button_locations[len(buttons)][1],
        )
        button.place(
            x=button_locations[len(buttons)][0],
            y=button_locations[len(buttons)][1],
        )
        button.id = GEMS[len(buttons)]
        buttons.append(button)

    # for location in button_locations:
    #     image = ImageTk.PhotoImage(file=gem, resize=(40, 40))
    #     button = tk.Button(root, image=image, x=location[0], y=location[1])

    # selection_buttons = []
    # for gem in GEMS:
    #     image = ImageTk.PhotoImage(file=gem, resize=)
    #     button = tk.Button(root, anchor=tk.SW, image=image)
    #     button.id = os.path.basename(gem)
    #     button.pack()
    #     selection_buttons.append(button)

    # img = tk.Label(bg, anchor=tk.CENTER, borderwidth=2, padx=10, pady=5)

    root.mainloop()


if __name__ == "__main__":
    main()
