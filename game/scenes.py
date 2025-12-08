import pygame
import tkinter as tk
from tkinter import simpledialog
import time
import sys
import os

from settings import SCREEN_WIDTH, SCREEN_HEIGHT, BG_COLOR, SEND_INTERVAL, PLAYER_IMAGE_PATH
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)

from player import handle_input, draw_players, load_map_init
from network import update_server_location, get_server_data

sys.path.append(os.path.dirname(os.getcwd()))
from client import set_host, send_to_server, read_reply, connect, set_uuid

import uuid
from datetime import datetime, timedelta


client_data = {"x": 0, "y": 0}
last_send_time = 0


player_image_unscaled = pygame.image.load(PLAYER_IMAGE_PATH).convert()
player_image_unscaled.set_colorkey((255, 255, 255))

LAST_KNOWN_WH = 1000, 1000
scale = 1
font = pygame.font.Font(None, round(32 / scale))
player_image = player_image_unscaled
MAIN_RAN = False



def load_assets(w, h):
	global player_image_unscaled
	global LAST_KNOWN_WH
	display = pygame.display.Info()
	CURRENT_W = display.current_w
	CURRENT_H = display.current_h
	
	if LAST_KNOWN_WH == (w, h):
		return None

	if w != CURRENT_W and h != CURRENT_H:
		return None
	
	
	print("load_assets is not returning None this time")
	scale = CURRENT_W / 1000 
	
	LAST_KNOWN_WH = w, h

	player_image = pygame.transform.scale(player_image_unscaled, (CURRENT_W / 10, CURRENT_H / 10))
	font = pygame.font.Font(None, int(32 / scale))

	return player_image, font, scale 



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

	global last_send_time, player_image, font, scale, MAIN_RAN
	display = pygame.display.Info()
	moved = handle_input(client_data)
	if moved:
		last_send_time = update_server_location(client_data, last_send_time, SEND_INTERVAL)

	
	load_assets_output = load_assets(display.current_w, display.current_w)
	if load_assets_output != None:
		player_image, font, scale = load_assets_output
	
	if not MAIN_RAN:
		load_map_init()
		MAIN_RAN = False

	draw_players(screen, get_server_data(), player_image, font, scale, client_data)
	
	#return "end_scene"
