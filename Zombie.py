# Title:	Zombie
# Author:	Nicholas Wright
# Info:		A simple Zombie in a maze based off the Lonely (by BRIGHTLINE) music video produced by Jonah Geh.
# Version:	v0.0

import Game
import World
import Images
import Display

class Zombie():
	def __init__(self):
		self.display = Display.Display(self._Update, "Zombie")
		self.images = Images.Images()
		self.world = World.World(self)
		self.game = Game.Game(self)
		
	def MainLoop(self):
		self.display.MainLoop()
		
	def _Update(self, canvas, width, height):
		self.world.Update(canvas, width, height)
		
if __name__ == "__main__":
	z = Zombie()
	z.MainLoop()
	
