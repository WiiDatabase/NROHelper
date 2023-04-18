#!/usr/bin/env python3

import io
import os
import sys
import tkinter as tk
import webbrowser
from tkinter import filedialog, messagebox

from PIL import Image, ImageTk

import nrohelper

VERSION = "0.1"

jpg_path = "default.jpg"

try:
    jpg_path = os.path.join(sys._MEIPASS, jpg_path, jpg_path)
except:
    pass


class Editor:
    def __init__(self, elems):
        self.filename = None
        self.elements = elems

        self.name = tk.StringVar()
        self.name.set("Untitled Homebrew")
        self.author = tk.StringVar()
        self.author.set("Unknown Author")
        self.version = tk.StringVar()
        self.version.set("0.0.0.0")

        self.image = None
        self.data = None
        self.nrosize = 0

    # NRO File browser
    def browse(self):
        tmpfilename = (
            filedialog.askopenfilename(
                title="Select NRO",
                filetypes=(("NRO Files", "*.nro"), ("All Files", "*.*")),
            )
            or self.filename
        )
        self.load_nro_data(tmpfilename)

    # Load data from NRO specified in tmpfilename
    def load_nro_data(self, tmpfilename):
        if not tmpfilename:
            return False
        try:
            self.data = nrohelper.NROHelper(tmpfilename)
        except NotImplementedError:
            messagebox.showerror(
                "Error: Unsupported NRO",
                "NRO files without Assets (e.g. those built with libtransistor) "
                "are currently unsupported.",
            )
            return False
        except:
            messagebox.showerror(
                "Error: Not a valid NRO",
                "This is not a (valid) Nintendo Switch NRO file.",
            )
            return False

        self.filename = tmpfilename
        self.name.set(self.data.get_name())
        self.author.set(self.data.get_publisher())
        self.version.set(self.data.nacp.get_version())

        self.image = Image.open(io.BytesIO(self.data.icon))
        image = ImageTk.PhotoImage(self.image)
        self.imagebox.configure(image=image)
        self.imagebox.image = image

        if self.filename:
            # Enable text fields
            for elem in self.elements:
                elem.configure(state="normal")

            # Enable "extract" menu item
            menubar.entryconfig("Extract", state="normal")
            if self.data.asset.icon.size > 0:
                extract_menu.entryconfig("Icon", state="normal")
            else:
                extract_menu.entryconfig("Icon", state="disabled")
            if self.data.asset.nacp.size > 0:
                extract_menu.entryconfig("NACP", state="normal")
            else:
                extract_menu.entryconfig("NACP", state="disabled")
            if self.data.asset.romfs.size > 0:
                extract_menu.entryconfig("RomFS", state="normal")
            else:
                extract_menu.entryconfig("RomFS", state="disabled")

    def browse_image(self):
        """Opens filebrowser for browsing images."""
        image_path = filedialog.askopenfilename(
            title="Select image file",
            filetypes=(
                ("PNG Files", "*.png"),
                ("JPG Files", "*.jpg"),
                ("JPEG Files", "*.jpeg"),
                ("GIF Files", "*.gif"),
                ("BMP Files", "*.bmp"),
                ("TGA Files", "*.tga"),
                ("All Files", "*.*"),
            ),
        )
        self.image = Image.open(image_path).convert("RGB")
        self.image = self.image.resize((256, 256), Image.ANTIALIAS)
        buffer = io.BytesIO()
        # if it's not already a jpeg, convert it into one
        if self.image.format != "JPEG":
            self.image.save(buffer, format="JPEG")
            self.image = Image.open(buffer)

        image2 = ImageTk.PhotoImage(self.image)
        self.imagebox.configure(image=image2)

        self.imagebox.image = image2

    def save(self):
        name = self.name.get()
        try:
            self.data.edit_name(name)
        except ValueError:
            messagebox.showerror("Saving failed", "Name must be < 512 characters")
            return False

        author_name = self.author.get()
        try:
            self.data.edit_publisher(author_name)
        except ValueError:
            messagebox.showerror(
                "Saving failed", "Author name must be < 256 characters"
            )
            return False

        version = self.version.get()
        try:
            self.data.edit_version(version)
        except ValueError:
            messagebox.showerror("Saving failed", "Version must be < 16 characters")
            return False

        self.data.save_nacp()
        messagebox.showinfo("Saving completed", "Saving completed:\n" + self.filename)

    def extract_icon(self):
        icon_filename = filedialog.asksaveasfilename(
            title="Select JPG path",
            filetypes=(("JPG Files", "*.jpg"), ("All Files", "*.*")),
            defaultextension=".jpg",
            initialfile=os.path.splitext(os.path.basename(self.filename))[0],
        )

        if icon_filename:
            self.data.extract_icon(icon_filename)
            messagebox.showinfo("Extraction completed", "Icon extraction completed!")

    def extract_nacp(self):
        nacp_filename = filedialog.asksaveasfilename(
            title="Select NACP path",
            filetypes=(("NACP Files", "*.nacp"), ("All Files", "*.*")),
            defaultextension=".nacp",
            initialfile=os.path.splitext(os.path.basename(self.filename))[0],
        )

        if nacp_filename:
            self.data.extract_nacp(nacp_filename)
            messagebox.showinfo("Extraction completed", "NACP extraction completed!")

    def extract_romfs(self):
        romfs_filename = filedialog.asksaveasfilename(
            title="Select RomFS path",
            filetypes=(("RomFS Files", "*.romfs"), ("All Files", "*.*")),
            defaultextension=".romfs",
            initialfile=os.path.splitext(os.path.basename(self.filename))[0],
        )

        if romfs_filename:
            self.data.extract_romfs(romfs_filename)
            messagebox.showinfo("Extraction completed", "RomFS extraction completed!")

    @staticmethod
    def open_source():
        webbrowser.open_new_tab("https://github.com/WiiDatabase/NROHelper")

    @staticmethod
    def version_info():
        messagebox.showinfo(
            "About NROHelper GUI",
            "NROHelper GUI v" + VERSION + " by iCON (WiiDatabase.de)",
        )


# Main and title
root = tk.Tk()
root.title("NROHelper GUI")
ico_path = "icon.ico"
try:
    ico_path = os.path.join(sys._MEIPASS, ico_path, ico_path)
except:
    pass

try:
    root.iconbitmap(root, ico_path)
except:
    pass

# UI elements
elems = []
editor = Editor(elems)

# Text boxes
frame = tk.Frame(root)
frame.grid(row=3, column=2, columnspan=2)
tk.Label(frame, text="Name").grid(row=0, column=0, padx=5)
t1 = tk.Entry(frame, state="disabled", width=40, textvariable=editor.name)
t1.grid(row=0, column=1, padx=5)
elems.append(t1)

tk.Label(frame, text="Author").grid(row=1, column=0, padx=5)
t2 = tk.Entry(frame, state="disabled", width=40, textvariable=editor.author)
t2.grid(row=1, column=1, padx=5)
elems.append(t2)

tk.Label(frame, text="Version").grid(row=2, column=0, padx=5)
t3 = tk.Entry(frame, state="disabled", width=40, textvariable=editor.version)
t3.grid(row=2, column=1, padx=5)
elems.append(t3)

# b1 = tk.Button(frame, text="Replace image...", state="disabled", command=editor.browse_image)
# b1.grid(row=3, column=1)
# elems.append(b1)

# Icon preview
im = Image.open(jpg_path)
tkimage = ImageTk.PhotoImage(im)

canvas = tk.Label(frame, image=tkimage, width=256, height=256)
canvas.grid(row=0, rowspan=8, column=2)
editor.imagebox = canvas

# Menubar
menubar = tk.Menu(root)
root.config(menu=menubar)

# "File"
file = tk.Menu(menubar, tearoff=0)
file.add_command(label="Open", command=editor.browse)
file.add_command(label="Save", command=editor.save)
file.add_command(label="Exit", command=root.quit)
menubar.add_cascade(label="File", menu=file)

# "Extract"
extract_menu = tk.Menu(menubar, tearoff=0)
extract_menu.add_command(label="Icon", command=editor.extract_icon, state="disabled")
extract_menu.add_command(label="NACP", command=editor.extract_nacp, state="disabled")
extract_menu.add_command(label="RomFS", command=editor.extract_romfs, state="disabled")
menubar.add_cascade(label="Extract", menu=extract_menu, state="disabled")

# "About"
about_menu = tk.Menu(menubar, tearoff=0)
about_menu.add_command(label="Source Code", command=editor.open_source)
about_menu.add_command(label="Info", command=editor.version_info)
menubar.add_cascade(label="About", menu=about_menu)

# Main window
root.geometry("575x265")
root.resizable(0, 0)

if len(sys.argv) > 1:
    editor.load_nro_data(sys.argv[1])
# TODO: Open dialog after starting, but makes fields uneditable!?
# else:
#    editor.browse()

root.mainloop()
