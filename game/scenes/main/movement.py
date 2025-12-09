import pygame
from scenes.main.helper_functions import load_assets, norm_path
from scenes.main.map import teleport_out, get_cell, get_region, grid, load_current_map	



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
	
	print(client_data, type(client_data))
		
	client_data, return_val = load_current_map(client_data["player_pos"]["x"], client_data["player_pos"]["y"], client_data=client_data)
	

	
	
	for user_id, current_user_dict in server_data.items():
		if "location" in current_user_dict:
					
			#print(f" SCALE: {scale}, FONT_SIZE : ({font.get_height()}, {font.get_linesize()}), PLAYER_SIZE: {player_image.get_size()}")
			
			location = current_user_dict["location"]
			username_surface = client_data["font"].render(current_user_dict["username"], True, (0, 0, 0))
			new_w = int(username_surface.get_width() * client_data["scale"])
			new_h = int(username_surface.get_height() * client_data["scale"])

			username_surface = pygame.transform.scale(username_surface, (new_w, new_h))
			graph_x, graph_y = simplify_coords(location["x"], location["y"])
			
			player_rect = client_data["player_image"].get_rect(topleft=(graph_x * client_data["scale"], graph_y * client_data["scale"]))
            # TEXT RECT
			text_rect = username_surface.get_rect()

			# Center the bottom of the text at the top center of the player
			text_rect.midbottom = player_rect.midtop

			# Move it up a little so it doesn't touch the head
			text_rect.y -= 25			
			client_data["screen"].blit(username_surface, text_rect)
			
			client_data["screen"].blit(client_data["player_image"], player_rect)
			
	return client_data
