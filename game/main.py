# main.py
import pygame

pygame.init()
pygame.display.set_caption("mypygameapp")

from settings import FPS
import scene_manager

clock = pygame.time.Clock()
running = True


client_data = {
	"current_scene" : "setup_scene",
	"screen" : pygame.display.set_mode((1000, 1000), pygame.RESIZABLE),
	"FPS" : 60,
	"RESIZE_DELAY" : 1000,
	"last_resize_time" : 0,
	"font" : pygame.font.Font(None, 32),
	"LAST_KNOWN_WH" : (999,999),
	"scale" : 1,
	"win" : pygame.display.set_mode((1000, 1000), pygame.RESIZABLE),
	"SEND_INTERVAL" : 0.05,
	"SCENE_RAN" : False,
	"PLAYER_IMAGE_PATH" : "player.jpg",
	"player_pos" : {"x" : 0, "y" : 0},
	"BLOCK_X" : 0,
	"BLOCK_Y" : 0,
	"CURRENT_BLOCK" : None,
	"MAP_CONF" : None,
	"CURRENT_MAP" : "goodmap",
	"WALKSPEED" : 2,
	"last_send_time" : 0
}

def force_square_window(client_data=None):
	
	w, h = client_data["win"].get_size()
	new_size = min(w, h)
	if w != new_size or h != new_size:
		client_data["win"] = pygame.display.set_mode((new_size, new_size), pygame.RESIZABLE)
	
	return client_data
# =================================================================
while running:
	current_time = pygame.time.get_ticks()

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

		elif event.type == pygame.VIDEORESIZE:
			client_data["last_resize_time"] = current_time

	if client_data["last_resize_time"] != 0 and (current_time - client_data["last_resize_time"] >= client_data["RESIZE_DELAY"]):
		client_data = force_square_window(client_data=client_data)
		client_data["last_resize_time"] = 0  


	output = getattr(scene_manager, client_data["current_scene"])(client_data=client_data)
	if output is isinstance(output, dict):
		client_data.update(output)
	
	

	pygame.display.flip()
	clock.tick(client_data["FPS"])

pygame.quit()
