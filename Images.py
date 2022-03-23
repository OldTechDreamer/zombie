# Title:	Image module for Zombie (stores and loads all the images)
# Author:	Nicholas Wright
# Info:		To be used with Zombie.py
# Version:	v0.0

import tkinter

import Assets

class Images():
	def __init__(self):
		self.images = {}	# Images indexed by their number
		
	def GetImage(self, index):
		# Load the image if not loaded
		if not index in self.images:
			self._LoadImage(index)
			
		return self.images[index]
			
	def _LoadImage(self, index):
		image = tkinter.PhotoImage(data = Assets.RAW_IMAGE_DATA[index])
		self.images[index] = image