import pygame
from scenes.main.helper_functions import load_assets, norm_path
from scenes.main.map import teleport_out, get_cell, get_region, grid, load_current_map	
from pprint import pprint


def try_move(target_x, target_y, client_data=None):
	if get_cell(grid(target_x), grid(target_y), client_data=client_data) is None:
		return client_data, False

	if get_region(target_x, target_y, client_data=client_data) == "no_walk_zone":
		# teleport out if stuck
		coords = teleport_out(client_data)
		if coords:
			client_data["player_pos"]["x"], client_data["player_pos"]["y"] = coords
		return client_data, False

	client_data["player_pos"]["x"] = target_x
	client_data["player_pos"]["y"] = target_y
	return client_data, True

def handle_input(client_data=None):
    keys = pygame.key.get_pressed()
    moved = False

    # Right / Left
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        client_data, moved = try_move(client_data["player_pos"]["x"] + client_data["WALKSPEED"], client_data["player_pos"]["y"], client_data=client_data)
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        client_data, moved = try_move(client_data["player_pos"]["x"] - client_data["WALKSPEED"], client_data["player_pos"]["y"], client_data=client_data)

    # Down / Up
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        client_data, moved = try_move(client_data["player_pos"]["x"] , client_data["player_pos"]["y"] + client_data["WALKSPEED"], client_data=client_data)
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        client_data, moved = try_move(client_data["player_pos"]["x"] , client_data["player_pos"]["y"] - client_data["WALKSPEED"], client_data=client_data)

    return client_data, moved



def simplify_coords(x, y):
	subtract_by_x = int(x / 1000) * 1000
	subtract_by_y = int(y / 1000) * 1000
	
	
	return x - subtract_by_x, y - subtract_by_y

def filter_server_data(server_data):
	pass
	

def draw_objects(server_data, client_data=None):
	
		
	pprint(f"server_data; {server_data}")	
		
	client_data, return_val = load_current_map(client_data["player_pos"]["x"], client_data["player_pos"]["y"], client_data=client_data)
	
	

	if not server_data:
		return client_data
	
	

	
	user_data = server_data["users"]
	user_keys = list(user_data.keys())
	
	player_pos = client_data["player_pos"]
	for i in range(len(user_data)):
		current_user_dict = user_data[user_keys[i]]

		if "location" in current_user_dict:
			location = current_user_dict["location"]

			#Check if other players  on the same part of the map and if they are not,

			current_player_grid = (grid(location["x"]), grid(location["y"]))
			client_player_grid = (grid(player_pos["x"]), grid(player_pos["y"]))

			if current_player_grid != client_player_grid:
				continue

			#turn server  real coords to relitave ones
			graph_x, graph_y = simplify_coords(location["x"], location["y"])

			

			#get the player image from ram
			uuid = current_user_dict["uuid"]
			player_image = client_data["player_images"][uuid]
			
			#username tag thing
			username_surface = client_data["font"].render(current_user_dict["username"], True, (0, 0, 0))

			#scale that thaang
			new_w = int(username_surface.get_width() * client_data["scale"])
			new_h = int(username_surface.get_height() * client_data["scale"])			
			
			username_surface = pygame.transform.scale(username_surface, (new_w, new_h))




			#center username and stuff
			player_rect = player_image.get_rect(
				topleft=(graph_x * client_data["scale"], graph_y * client_data["scale"])
			)
	
			# Text rectangle
			text_rect = username_surface.get_rect()
			text_rect.midbottom = player_rect.midtop
			text_rect.y -= 15 

			client_data["screen"].blit(username_surface, text_rect)
			client_data["screen"].blit(player_image, player_rect)


	return client_data
