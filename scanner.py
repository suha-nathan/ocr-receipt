import cv2
import pytesseract
import imutils
import numpy as np
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from imutils.perspective import four_point_transform
import re

class ReceiptScanner:
    def __init__(self, root):
        self.root = root
        self.points = []
        self.image = None
        self.ratio = None
        self.setup_ui()

    def setup_ui(self):
        self.root.title("Receipt Scanner")
        self.canvas = tk.Canvas(self.root)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(fill=tk.X)

        load_btn = tk.Button(btn_frame, text="Load Image", command=self.load_image)
        load_btn.pack(side=tk.LEFT)

        process_btn = tk.Button(btn_frame, text="Process", command=self.process_image)
        process_btn.pack(side=tk.LEFT)

        self.canvas.bind("<Button-1>", self.get_mouse_click)

    def load_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.image = cv2.imread(file_path)
            self.image = imutils.resize(self.image, width=500)
            self.ratio = self.image.shape[1] / float(self.image.shape[1])
            self.display_image(self.image)

    def display_image(self, image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        image = ImageTk.PhotoImage(image)

        self.canvas.image = image
        self.canvas.create_image(0, 0, anchor=tk.NW, image=image)

    def get_mouse_click(self, event):
        if len(self.points) < 4:
            self.points.append((event.x, event.y))
            self.canvas.create_oval(event.x - 5, event.y - 5, event.x + 5, event.y + 5, outline="red", width=2)
        if len(self.points) == 4:
            self.process_image()

    def process_image(self):
        if len(self.points) != 4:
            print("Please select 4 points.")
            return

        pts = np.array(self.points, dtype="float32")
        receipt = four_point_transform(self.image, pts)
        self.display_image(receipt)
        self.perform_ocr(receipt)

    def perform_ocr(self, image):
        options = "--psm 4"
        text = pytesseract.image_to_string(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), config=options)

        print("[INFO] raw output:")
        print("==================")
        print(text)
        print("\n")

        pricePattern = r'([0-9]+\.[0-9]+)'

        print("[INFO] price line items:")
        print("========================")

        for row in text.split("\n"):
            if re.search(pricePattern, row) is not None:
                print(row)

if __name__ == "__main__":
    root = tk.Tk()
    app = ReceiptScanner(root)
    root.mainloop()
