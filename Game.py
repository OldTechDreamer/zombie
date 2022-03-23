# Title:	Game module for Zombie (Transitions between game scenes)
# Author:	Nicholas Wright
# Info:		To be used with Zombie.py
# Version:	v0.0

import Assets
import World

import random

class Game():
	# Scenes
	MAZE = 0
	JESUS = 1
	HAND = 2
	
	RESTART_KEY = 32	# Space Bar

	def __init__(self, zombie):
		self.z = zombie
		
		self.SetScene(Game.MAZE)	# Set the start scene
		self.z.display.AddKeyListener(self._OnKeyEvent)
		
	def SetScene(self, scene):
		self.scene = scene
		
		# Clean up
		self.z.world.ClearPointListeners()
		
		# Setup the next scene
		if self.scene == Game.MAZE:
			# Setup the world
			self.z.world.SetWorld(Assets.MAZE)
			
			# Add the player
			self.player = World.Man(1.5, 12.5, 0.35)
			self.player.BindToControls(self.z.display)
			self.z.world.AddEntity(self.player)
			
			# Generate a random exit point from the list
			treasure_points = Assets.MAZE["TreasurePoints"]
			point = treasure_points[random.randrange(0, len(treasure_points))]
			self.z.world.AddPointListener(point, self._NextScene)
			
		elif self.scene == Game.JESUS:
			# Setup the world
			self.z.world.SetWorld(Assets.JESUS)
			
			# Set the exit point
			self.z.world.AddPointListener(Assets.JESUS["TreasurePoints"][0], self._NextScene)
			
		elif self.scene == Game.HAND:
			self.z.world.SetWorld(Assets.HAND)
			
			# Delete the player
			self.z.world.ClearEntities()

	def _NextScene(self, *args):
		self.SetScene(self.scene + 1)
		
	def _OnKeyEvent(self, event):
		# Restart the game
		if str(event.type) == "KeyPress" and event.keycode == Game.RESTART_KEY:
			self.z.world.ClearEntities()
			self.SetScene(Game.MAZE)