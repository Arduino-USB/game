import tkinter as tk
from tkinter import simpledialog

def popup_input(prompt):
	root = tk.Tk()
	root.withdraw()  # Hide main Tk window

	result = simpledialog.askstring(
				"Input Required", 
				prompt
	)

	root.destroy()
	return result



