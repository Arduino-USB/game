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
	
	

	uuid_accepted = False
	u_id = str(uuid.uuid4())
	
	connected = False

	while not connected:
		
		time.sleep(0.01)
		set_host(ip)
		connected = connect(ip)
		if connected == True:
			break
		print("host not connected")
		ip = popup_input("Error: IP not connected")
		
		
	print("Setting up UUID......")
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
