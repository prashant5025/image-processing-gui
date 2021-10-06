import ctypes
import os
from tkinter import *
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import matplotlib.image as mpimg
import numpy as np
import cv2

ctypes.windll.shcore.SetProcessDpiAwareness(True)

root = Tk()
ttk.Style().configure("TButton", justify=CENTER)

# Global variables
gui_width = 1385
gui_height = 595
ip_file = ""
op_file = ""
original_img = None
modified_img = None

root.title("Image processing")
root.geometry(f"{gui_width}x{gui_height}")
# root.resizable(False, False)
root.minsize(gui_width, gui_height)


def draw_before_canvas():
    global original_img, ip_file
    # original_img = Image.open(filename).resize((512, 512), Image.BILINEAR)  # if resize
    # img = ImageTk.PhotoImage(original_img)
    original_img = Image.open(ip_file)
    img = ImageTk.PhotoImage(original_img)
    before_canvas.create_image(
        256,
        256,
        image=img,
        anchor="center",
    )
    before_canvas.img = img


def draw_after_canvas(mimg):
    global modified_img
    modified_img = Image.fromarray(mimg)
    img = ImageTk.PhotoImage(modified_img)
    after_canvas.create_image(
        256,
        256,
        image=img,
        anchor="center",
    )
    after_canvas.img = img


def load_file():
    global ip_file
    ip_file = filedialog.askopenfilename(
        title="Open an image file",
        initialdir=".",
        filetypes=[("All Image Files", "*.*")],
    )
    draw_before_canvas()
    print(f"Image loaded from: {ip_file}")


def save_file():
    global ip_file, original_img, modified_img
    file_ext = os.path.splitext(ip_file)[1][1:]
    op_file = filedialog.asksaveasfilename(
        filetypes=[
            (
                f"{file_ext.upper()}",
                f"*.{file_ext}",
            )
        ],
        defaultextension=[
            (
                f"{file_ext.upper()}",
                f"*.{file_ext}",
            )
        ],
    )
    modified_img = modified_img.convert("RGB")
    modified_img.save(op_file)
    print(f"Image saved at: {op_file}")


# frames
left_frame = ttk.LabelFrame(root, text="Original Image", labelanchor=N)
left_frame.pack(fill=BOTH, side=LEFT, padx=10, pady=10, expand=1)

middle_frame = ttk.LabelFrame(root, text="Algorithms", labelanchor=N)
middle_frame.pack(fill=BOTH, side=LEFT, padx=5, pady=10)

right_frame = ttk.LabelFrame(root, text="Modified Image", labelanchor=N)
right_frame.pack(fill=BOTH, side=LEFT, padx=10, pady=10, expand=1)

# left frame contents
before_canvas = Canvas(left_frame, bg="white", width=512, height=512)
before_canvas.pack(expand=1)

browse_btn = ttk.Button(left_frame, text="Browse", command=load_file)
browse_btn.pack(expand=1, anchor=SW, pady=(5, 0))

# middle frame contents
algo_canvas = Canvas(middle_frame, width=260, highlightthickness=0)
scrollable_algo_frame = Frame(algo_canvas)
scrollbar = Scrollbar(
    middle_frame, orient="vertical", command=algo_canvas.yview, width=15
)
scrollbar.pack(side="right", fill="y")
algo_canvas.pack(fill=BOTH, expand=1)
algo_canvas.configure(yscrollcommand=scrollbar.set)
algo_canvas.create_window((0, 0), window=scrollable_algo_frame, anchor="nw")
scrollable_algo_frame.bind(
    "<Configure>", lambda _: algo_canvas.configure(scrollregion=algo_canvas.bbox("all"))
)

grayscale_setting = IntVar()
grayscale_setting.set(0)

grayscale_checkbtn = ttk.Checkbutton(
    middle_frame, text="Grayscale output?", variable=grayscale_setting
)
grayscale_checkbtn.pack(pady=6)

# right frame contents
after_canvas = Canvas(right_frame, bg="white", width=512, height=512)
after_canvas.pack(expand=1)

save_btn = ttk.Button(right_frame, text="Save", command=save_file)
save_btn.pack(expand=1, anchor=SE, pady=(5, 0))


# algorithm fns
def RGB2Gray():
    img = mpimg.imread(ip_file)
    R, G, B = img[:, :, 0], img[:, :, 1], img[:, :, 2]
    return 0.299 * R + 0.58 * G + 0.114 * B


def callRGB2Gray():
    grayscale = RGB2Gray()
    draw_after_canvas(grayscale)


def negative():
    img = RGB2Gray() if (grayscale_setting.get()) else Image.open(ip_file)
    img = np.array(img)
    img = 255 - img
    draw_after_canvas(img)


def gray_slice_withbg():
    lower_limit = 100
    upper_limit = 180
    img = RGB2Gray()
    m, n = img.shape
    img_thresh = np.zeros((m, n), dtype=int)

    for i in range(m):
        for j in range(n):
            img_thresh[i, j] = (
                0 if lower_limit < img[i, j] <= upper_limit else img[i, j]
            )
    draw_after_canvas(img_thresh)


def gray_slice_withoutbg():
    lower_limit = 100
    upper_limit = 180
    img = RGB2Gray()
    m, n = img.shape
    img_thresh = np.zeros((m, n), dtype=int)

    for i in range(m):
        for j in range(n):
            img_thresh[i, j] = 0 if lower_limit < img[i, j] <= upper_limit else 255
    draw_after_canvas(img_thresh)


def bit_slice():
    bitplanes = []

    img = cv2.imread(ip_file, 0)
    img = np.array(img)

    for k in range(9):
        plane = np.full((img.shape[0], img.shape[1]), 2 ** k, np.uint8)
        res = cv2.bitwise_and(plane, img)
        x = res * 255
        x = cv2.resize(x, (171, 171))
        bitplanes.append(x)

    row1 = cv2.hconcat([bitplanes[0], bitplanes[1], bitplanes[2]])
    row2 = cv2.hconcat([bitplanes[3], bitplanes[4], bitplanes[5]])
    row3 = cv2.hconcat([bitplanes[6], bitplanes[7], bitplanes[8]])
    final_img = cv2.vconcat([row1, row2, row3])
    draw_after_canvas(final_img)


# algorithm btns
algo_b1 = ttk.Button(
    scrollable_algo_frame, text="RGB to Grayscale", width=30, command=callRGB2Gray
).pack(expand=1, padx=5, pady=2, ipady=2)

algo_b2 = ttk.Button(
    scrollable_algo_frame, text="Negative", width=30, command=negative
).pack(pady=2, ipady=2)

algo_b3 = ttk.Button(
    scrollable_algo_frame,
    text="Gray level slicing\n(with background)",
    width=30,
    command=gray_slice_withbg,
).pack(pady=2, ipady=2)

algo_b4 = ttk.Button(
    scrollable_algo_frame,
    text="Gray level slicing\n(without background)",
    width=30,
    command=gray_slice_withoutbg,
).pack(pady=2, ipady=2)


algo_b5 = ttk.Button(
    scrollable_algo_frame,
    text="Bit plane slicing",
    width=30,
    command=bit_slice,
).pack(pady=2, ipady=2)

root.mainloop()