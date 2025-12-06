import pygame
import tkinter as tk
from tkinter import simpledialog
import time
import sys
import os

from settings import SCREEN_WIDTH, SCREEN_HEIGHT, BG_COLOR, SEND_INTERVAL
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

from player import handle_input, draw_players
from network import update_server_location, get_server_data

sys.path.append(os.path.dirname(os.getcwd()))
from client import set_host, send_to_server, read_reply, connect, set_uuid

import uuid
from datetime import datetime, timedelta


client_data = {"x": 0, "y": 0}
last_send_time = 0




def show_message(message, duration=500):
	"""
	Show a small popup message without window decorations for a set duration.
	"""
	root = tk.Tk()
	root.withdraw()  # hide main window

	popup = tk.Toplevel(root)
	popup.overrideredirect(True)  # remove title bar
	popup.geometry("200x50+500+300")  # width x height + x_offset + y_offset

	label = tk.Label(popup, text=message, font=("Arial", 12), bg="lightyellow", fg="black")
	label.pack(expand=True, fill="both")

	# Auto-close after duration
	popup.after(duration, popup.destroy)
	root.after(duration + 100, root.destroy)  # destroy hidden root after popup closes

	root.mainloop()



def popup_input(prompt):
	root = tk.Tk()
	root.withdraw()  # Hide main Tk window

	result = simpledialog.askstring("Input Required", prompt)

	root.destroy()
	return result

def setup_scene():
	global current_scene  # <- Important
	ip = popup_input("Enter Your IP")

	# Force user to enter an IP
	while not ip:
		print("Error: IP not specified")
		ip = popup_input("Error: Please enter an IP")
	set_host(ip)
	
	print("Setting up UUID......")
	show_message("Setting up UUID.....")
	
	uuid_accepted = False
	u_id = str(uuid.uuid4())
	
	connect(ip)
		
	send_to_server({"set_uuid" : u_id})
		
	while not uuid_accepted:
		time.sleep(0.01)
		reply = read_reply()
		
		print(f"Reply when SEND: {reply}")
		
		last_time = datetime.now()
		if reply is not None:
			reply_keys = list(reply.keys())
			for i in range(len(reply_keys)):
				current_dih = reply
				print(f"Currently checking dict: {current_dih}")
				if current_dih["uuid"] == u_id and current_dih["message"] == "SUCCESS":
					uuid_accepted = True
					set_uuid(u_id)
					break

		elif datetime.now() - last_time >= timedelta(seconds=0.5):
			print("server did not respond, sending another UUID") 
			u_id = str(uuid.uuid4())
			send_to_server({"set_uuid" : u_id})
	
	username = popup_input("Enter Your Username")
	send_to_server({"set_username" : username})
			
	username_accepted = False

	while not username_accepted:
		time.sleep(0.01)
		
		reply = read_reply()

		if reply == None:
			continue
		
		if reply["message"] == "SUCCESS":
			break
		else:
			username = popup_input("Error: Username taken")
			send_to_server({"set_username" : username})
	
	
	
	return "main_scene"
	
	
def main_scene():

	global last_send_time
	moved = handle_input(client_data)
	if moved:
		last_send_time = update_server_location(client_data, last_send_time, SEND_INTERVAL)

	screen.fill(BG_COLOR)
	 
	draw_players(screen, get_server_data())
	
	#return "end_scene"
