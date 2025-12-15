import pygame
import base64
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
from client import read_reply  # Edited by Grok - for main_scene

# Edited by Grok - full original setup_scene restored
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
            send_to_server({"set_uuid" : client_data["uuid"]})
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

# Edited by Grok - full original wait_scene restored
def wait_scene(client_data=None):
    pick_player_image = message_box("Pick custom player image? [Y/n]")
    if pick_player_image == True:
        client_data["PLAYER_IMAGE_PATH"] = file_picker()
    else:
        client_data["PLAYER_IMAGE_PATH"] = os.path.join(os.getcwd() ,"player.png")
    with open(client_data["PLAYER_IMAGE_PATH"], "rb") as f:
        print("sending player sprite to server")
        send_to_server({"set_player_image" : base64.b64encode(f.read()).decode()})
    print("waiting fro server to send init data")
    while True:
        time.sleep(0.01)
        reply = read_reply()
        if reply == None:
            continue
        if reply["func"] == "__send_init_data":
            client_data["init_player_data"] = reply["player_data"]
            client_data["CURRENT_MAP"] = reply["map"]
            client_data["obj"] = reply["obj"]
            break
    print("Server sent player_data")
    client_data.update({"current_scene" : "main_scene", "SCENE_RAN" : False})
    return client_data

# Edited by Grok - updated main_scene with server message handling (kill, win/lose)
def main_scene(client_data=None):
    if client_data["SCENE_RAN"] == False:
        client_data = init_main(client_data=client_data)
        client_data["SCENE_RAN"] = True
    
    # Check for important server messages (death, game end, etc.)
    reply = read_reply()
    while reply is not None:
        if reply.get("func") == "player_killed":
            if reply.get("target_uuid") == client_data["uuid"]:
                client_data["alive"] = False
        elif reply.get("func") == "game_end":
            client_data["won"] = reply.get("won", False)
            client_data["current_scene"] = "end_scene"
            client_data["SCENE_RAN"] = False  # reset for end_scene
            return client_data
        elif reply.get("func") == "exits_opened":
            pass  # visual change happens automatically via objects
        reply = read_reply()
    
    display = pygame.display.Info()
    client_data, moved = handle_input(client_data=client_data)
    if moved:
        client_data["last_send_time"] = update_server_location(client_data=client_data)
    client_data, load_assets_output = load_assets(display.current_w, display.current_w, client_data=client_data)
    client_data = draw_objects(get_server_data(), client_data=client_data)
    return client_data

# Edited by Grok - new end scene
def end_scene(client_data=None):
    screen = client_data["screen"]
    screen.fill((0, 0, 0))
    
    font_big = pygame.font.Font(None, 120)
    font_small = pygame.font.Font(None, 60)
    
    won = client_data.get("won", False)
    
    if won:
        text = "YOU ESCAPED!"
        subtext = "Survivors Win"
        color = (0, 255, 0)
    else:
        text = "YOU DIED"
        subtext = "Hunter Wins" if client_data.get("role") == "hunter" else "Survivors Lose"
        color = (255, 0, 0)
    
    surf = font_big.render(text, True, color)
    rect = surf.get_rect(center=(screen.get_width()//2, screen.get_height()//2 - 60))
    screen.blit(surf, rect)
    
    sub_surf = font_small.render(subtext, True, (255, 255, 255))
    sub_rect = sub_surf.get_rect(center=(screen.get_width()//2, screen.get_height()//2 + 20))
    screen.blit(sub_surf, sub_rect)
    
    instr = font_small.render("Press ESC to quit", True, (200, 200, 200))
    instr_rect = instr.get_rect(center=(screen.get_width()//2, screen.get_height()//2 + 100))
    screen.blit(instr, instr_rect)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            client_data["running"] = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                client_data["running"] = False
    
    return client_data
