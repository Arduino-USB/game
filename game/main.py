# main.py
import pygame
import time
from settings import FPS
pygame.init()

clock = pygame.time.Clock()
running = True
import scenes
current_scene = "setup_scene"
scene_output = {}

while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

	output = getattr(scenes, current_scene)()

	if output is not None:
		current_scene = output[0]
		
		if len(output) < 2:
			break
	
		scene_dict = output[1]
		scene_keys = list(scene_dict.keys())
		for i in range(len(scene_dict)):
			scene_output[scene_keys[i]] = scene_dict[scene_keys[i]]
		
		

	pygame.display.flip()
	clock.tick(FPS)

pygame.quit()

