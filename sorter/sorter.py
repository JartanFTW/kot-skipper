import tkinter as tk
import os
from PIL import Image, ImageTk

PATH = os.getcwd()

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
        img = self.sort_img_path
        os.remove(img)
        self.display_next_img()

    def display_next_img(self):
        try:
            # gets first image in unsorted folder
            img = os.path.join(
                PATH, "unsorted", os.listdir(os.path.join(PATH, "unsorted"))[0]
            )
        except IndexError:
            self.sort_img.configure(image=None)
            self.sort_img.image = None
            self.sort_img.configure(text="No more unsorted images")
            return

        self.sort_img_path = img

        img = Image.open(img).resize((100, 100))
        img = ImageTk.PhotoImage(image=img)
        self.sort_img.configure(image=img)
        self.sort_img.image = img

    def sort_image(self, tier: int, color: int):
        # moves image to sorted folder based on input

        file_path = self.sort_img_path
        img = os.path.join(PATH, "unsorted", file_path)
        move_to = os.path.join(
            PATH,
            "sorted",
            f"{tier}",
            f"{COLORS_FULL[color]}",
            os.path.basename(file_path),
        )
        print(f"Moving {os.path.basename(file_path)} to {COLORS_FULL[color]}-{tier}")
        os.rename(img, move_to)


def main():
    window = Window()
    window.mainloop()


if __name__ == "__main__":
    main()
