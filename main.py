import pygame
from client import send_to_server, read_from_server, get_server_data
import time

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1920, 1080))
clock = pygame.time.Clock()
running = True
walkspeed = 15

client_data = {
	"x": 0,
	"y": 0
}

last_server_data = {}

# rate limit sending updates
last_send_time = 0
send_interval = 0.05  # 50ms

# load player image once
player_image = pygame.image.load("player.jpg").convert()

while running:
	screen.fill((255, 255, 255))

	# poll for events
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

	# handle movement
	keys = pygame.key.get_pressed()
	moved = False
	if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
		client_data["x"] += walkspeed
		moved = True
	if keys[pygame.K_LEFT] or keys[pygame.K_a]:
		client_data["x"] -= walkspeed
		moved = True
	if keys[pygame.K_DOWN] or keys[pygame.K_s]:
		client_data["y"] += walkspeed
		moved = True
	if keys[pygame.K_UP] or keys[pygame.K_w]:
		client_data["y"] -= walkspeed
		moved = True

	# send updates at most every send_interval seconds
	now = time.time()
	if moved and now - last_send_time >= send_interval:
		send_to_server({"set_location": {"x": client_data["x"], "y": client_data["y"]}})
		last_send_time = now


	server_reply = read_from_server()

	
	if server_reply == None:
		server_reply = last_server_data
	if "server_data" in server_reply.keys():
		last_server_data = server_reply
		server_data = server_reply["server_data"]
		for user_id, current_user_dict in server_data.items():
			if "location" in current_user_dict:
				location = current_user_dict["location"]
				screen.blit(player_image, (location["x"], location["y"]))

	# flip the display
	pygame.display.flip()
	clock.tick(60)


pygame.quit()

