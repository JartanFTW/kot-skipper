import tkinter as tk
import os
from PIL import Image, ImageTk

PATH = os.getcwd()

UNSORTED = [
    os.path.join(PATH, "unsorted", x)
    for x in os.listdir(os.path.join(PATH, "unsorted"))
]
GEMS = [os.path.join(PATH, "gems", x) for x in os.listdir(os.path.join(PATH, "gems"))]
COLORS = ["r", "y", "g", "b", "p"]
COLORS_FULL = {"r": "red", "y": "yellow", "g": "green", "b": "blue", "p": "purple"}
TIERS = [1, 2, 3, 4, 5, 6, 7, 8]


class Window(tk.Tk):
    def __init__(self):
        super(Window, self).__init__()

        self.title = "Sorter"
        self.minsize(400, 500)

        self.create_layout()

    def create_layout(self):

        tk.Label(
            self,
            text="Click the Correct Gem",
        ).pack()

        self.sort_img = tk.Label(self)
        self.display_next_img()
        self.sort_img.pack()

        buttons = tk.Label(self)

        for tier in TIERS:  # 1 thru 8
            for color in COLORS:

                image = ImageTk.PhotoImage(
                    image=Image.open(
                        os.path.join(PATH, "gems", f"{color}{tier}.jpg")
                    ).resize((40, 40))
                )

                button = tk.Button(
                    buttons,
                    text=f"{color}{tier}",
                    image=image,
                    command=lambda tier=tier, color=color: self.button_pressed(
                        tier, color
                    ),
                )

                button.image = image

                button.grid(
                    column=tier - 1, row=COLORS.index(color)
                )  # x-1 to compensate for 1-8 instead of 0-7

        tk.Button(buttons, text=f"None", command=self.bad_img).grid(
            columnspan=8, row=6, sticky="we"
        )

        buttons.pack()

    def button_pressed(self, tier: int, color: str):
        print(f"Buttonpress {tier} {color}")
        self.sort_image(tier, color)
        self.display_next_img()

    def bad_img(self):
        file_name = os.listdir(os.path.join(PATH, "unsorted"))[0]
        img = os.path.join(PATH, "unsorted", file_name)
        os.remove(img)
        self.display_next_img()

    def display_next_img(self):
        try:
            img = os.path.join(
                PATH, "unsorted", os.listdir(os.path.join(PATH, "unsorted"))[0]
            )
        except IndexError:
            self.sort_img.configure(image=None)
            self.sort_img.image = None
            self.sort_img.configure(text="No more unsorted images")
            return

        img = Image.open(img).resize((100, 100))
        img = ImageTk.PhotoImage(image=img)
        self.sort_img.configure(image=img)
        self.sort_img.image = img

    def sort_image(self, tier: int, color: int):
        # copy first file in unsorted folder
        # paste file in tier/color provided
        # delete first file in unsorted folder

        file_name = os.listdir(os.path.join(PATH, "unsorted"))[0]
        img = os.path.join(PATH, "unsorted", file_name)
        move_to = os.path.join(
            PATH, "sorted", f"{tier}", f"{COLORS_FULL[color]}", file_name
        )
        print(f"Moving {file_name} to {COLORS_FULL[color]}-{tier}")
        os.rename(img, move_to)
        # os.popen(f"copy {img} {move_to}")


def main():
    window = Window()
    window.mainloop()


# def setup_root():

#     root = tk.Tk()
#     root.title("Sorter")

#     width, height = root.winfo_screenwidth(), root.winfo_screenheight()

#     root.geometry(f"400x500+{int(width/2)}+{int(height/2)}")

#     root.resizable(False, False)

#     return root


# def declare_image(color=str, tier=int):
#     print(f"Declared as {color}{tier}")


# def main():
#     root = setup_root()

#     root_x, root_y = root.size()

#     tk.Label(
#         root,
#         text="Click the correct gem",
#         anchor=tk.CENTER,
#         borderwidth=1,
#         padx=10,
#         pady=5,
#         font=("Helvetica", 14),
#     )

#     ##

#     button_canvas = tk.Canvas(root,
#     colors = ["b", "g", "p", "r", "y"]
#     for tier in range(1, 9):  # 1-8
#         for color in range(5):
#             image = ImageTk.PhotoImage(
#                 image=Image.open(
#                     os.path.join(PATH, "gems", f"{colors[color]}{tier}.jpg")
#                 ).resize((40, 40))
#             )

#             print(f"{colors[color]}{tier}.jpg")
#             tk.Button(
#                 button_canvas,
#                 image=image,
#                 text=f"{colors[color]}{tier}.jpg",
#                 command=lambda: declare_image(colors[color], tier),
#             ).grid(row=color, column=tier, padx=2, pady=5)
#    root.mainloop()

# button_locations = []
# y = 480
# for i in range(5):
#     y -= 40
#     x = 0
#     for i in range(8):
#         x += 40
#         button_locations.append((x, y))

# ##

# buttons = []
# for gem in GEMS:
#     image = ImageTk.PhotoImage(image=Image.open(gem).resize((40, 40)))
#     button = tk.Button(
#         root,
#         image=image,
#     )

#     button.place(
#         x=button_locations[len(buttons)][0],
#         y=button_locations[len(buttons)][1],
#     )
#     button.id = GEMS[len(buttons)]
#     buttons.append(button)

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


if __name__ == "__main__":
    main()
