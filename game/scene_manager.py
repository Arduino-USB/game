import pygame
import tkinter as tk
from tkinter import simpledialog
import time
import sys
import os



sys.path.append(os.path.dirname(os.getcwd()))
from client import set_host, send_to_server, read_reply, connect, set_uuid

import uuid
from datetime import datetime, timedelta
 
from scenes.setup.helper_functions import popup_input


from scenes.wait.helper_functions import file_picker, message_box

from scenes.main.helper_functions import load_assets
from scenes.main.map import get_region, grid, get_cell, load_current_map, load_map_init
from scenes.main.movement import handle_input, draw_objects
from scenes.main.network import update_server_location, get_server_data
from scenes.main.init import init as init_main







def setup_scene(client_data=None):
	client_data["ip"] = popup_input("Enter Your IP")

	# Force user to enter an IP
	while not client_data["ip"]:
		print("Error: IP not specified")
		client_data["ip"] = popup_input("Error: Please enter an IP")
	set_host(client_data["ip"])
	
	

	uuid_accepted = False
	client_data["uuid"] = str(uuid.uuid4())
	
	connected = False

	while not connected:
		
		time.sleep(0.01)
		set_host(client_data["ip"])
		connected = connect(client_data["ip"])
		if connected == True:
			break
		print("host not connected")
		client_data["ip"] = popup_input("Error: IP not connected")
		
		
	print("Setting up UUID......")
	send_to_server({"set_uuid" : client_data["uuid"]})
		
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
				if current_dih["uuid"] == client_data["uuid"] and current_dih["message"] == "SUCCESS":
					uuid_accepted = True
					set_uuid(client_data["uuid"])
					break

		elif datetime.now() - last_time >= timedelta(seconds=0.5):
			print("server did not respond, sending another UUID") 
			client_data["uuid"] = str(uuid.uuid4())
			send_to_server({"set_uuid" : u_id})
	
	client_data["username"] = popup_input("Enter Your Username")
	send_to_server({"set_username" : client_data["username"]})
			
	username_accepted = False

	while not username_accepted:
		time.sleep(0.01)
		
		reply = read_reply()

		if reply == None:
			continue
		
		if reply["message"] == "SUCCESS":
			break
		else:
			client_data["username"] = popup_input("Error: Username taken")
			send_to_server({"set_username" : client_data["username"]})
	
	
	client_data.update({"current_scene" : "wait_scene", "SCENE_RAN" : False})
	return client_data

def wait_scene(client_data=None):
	pick_player_image = message_box("Pick custom player image? [Y/n]")	
	
	if pick_player_image == True:
		client_data["PLAYER_IMAGE_PATH"] = file_picker()
	else:
		client_data["PLAYER_IMAGE_PATH"] = "player.png"
	
	print("Waiting for server to start the game")
	
	
	
	while True:
		time.sleep(0.01)
		reply = read_reply()
	
		if reply == None:
			continue	

		if "message" in reply.keys() and reply["message"] == "GAME_START":
			break
	
	print("Game started! Getting roles")	

	
	return client_data
	
def main_scene(client_data=None):
	
	if client_data["SCENE_RAN"] == False:
		client_data = init_main(client_data=client_data)
		client_data["SCENE_RAN"] = True			
	
	display = pygame.display.Info()
	client_data, moved = handle_input(client_data=client_data)
	if moved:
		client_data["last_send_time"] = update_server_location(client_data=client_data)

	
	client_data, load_assets_output = load_assets(display.current_w, display.current_w, client_data=client_data)
	#if load_assets_output != None:
	#	client_data = load_assets_output
			

	client_data = draw_objects(get_server_data(), client_data=client_data)
	
	return client_data
