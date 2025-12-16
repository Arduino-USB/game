import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import os

def file_picker(title="Select a player image", filetypes=(("PNG files", "*.png"), ("JPG files", "*.jpg"), ("JPEG file", "*.jpeg"))):
	"""
	Opens a cross-platform file picker dialog and returns the absolute path
	to the selected file, or None if the user cancels.
	"""
	root = tk.Tk()
	root.withdraw()  # Hide the Tkinter root window

	path = filedialog.askopenfilename(
		title=title,
		filetypes=filetypes
	)
	
	root.destroy()
	if not path:
		return None

	return os.path.abspath(path)



def message_box(prompt):
	root = tk.Tk()
	root.withdraw()  # Hide main Tk window

	result = messagebox.askyesno(
		"Confirmation",
		prompt
	)

	root.destroy()
	return result

