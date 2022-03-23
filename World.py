# Title:	World module for Zombie (draws the maze and men)
# Author:	Nicholas Wright
# Info:		To be used with Zombie.py
# Version:	v0.0

# The World, all sizes are relative to smallest dimension (width or height)

import time
import math

class World():
	WALL_WIDTH = 0.35			# Width of the wall relative to one size unit
	WALL_EXTENSION_WIDTH = 0.2	# With of the wall extension
	
	WALL_SET_BACK = -0.1		# How much the wall is set back from the end of it (relative to one size unit)
	WALL_EXTENSION = 0.15		# How much the wall sticks out at the ends (relative to one size unit)
	
	WALL_COLOUR = "#000000"
	BACKGROUND_COLOUR = "#555555"
	
	POINT_DISTANCE = 0.5		# The distance from the point a player needs to be to trigger it

	def __init__(self, zombie):
		self.z = zombie
		
		self.SetSize(1, 1)
	
		self.background_colour = World.BACKGROUND_COLOUR	# Background colour of the world
	
		self.walls = []			# Walls in the world, a list of (x1, y1, x2, y2) for lines
		self.objects = []		# Objects
		self.entities = []		# Entities (players)
		self.images = []		# Images
		
		self.point_listeners = []	# Listeners listening for points on the world where a play pay move to. A list of: ((point_x, point_y), function) where the function is of the form: def Point(man), where is the player who triggered the point
		
	def AddPointListener(self, point, callback):
		self.point_listeners.append((point, callback))
		
	def ClearPointListeners(self):
		self.point_listeners = []
		
	def SetSize(self, width, height):
		self.width = width
		self.height = height
		
		# Define the relative size
		self.size = height
		
		if width < height:
			self.size = height
		
	def Update(self, canvas, width, height):
		# Centre the world on the display
		world_ratio = self.width / float(self.height)
		display_ratio = width / float(height)
		
		if display_ratio >= world_ratio:		# Relative to height
			msize = height
			mx = (width - (world_ratio * msize)) / 2.0
			my = 0
			
		else:									# Relative to width
			msize = width
			mx = 0
			my = (height - (msize / world_ratio)) / 2.0
			
		scale = msize / self.size
		
		# Update everything
		canvas.create_rectangle(0, 0, width, height, fill = self.background_colour)
		
		self._DrawWalls(canvas, scale, mx, my)
		
		for o in self.objects:
			o.Update(canvas, scale, mx, my)
			
		for entity in self.entities:
			entity.Update(canvas, scale, mx, my, self)
			
		for image in self.images:
			self._DrawImage(canvas, scale, mx, my, image)
			
	def _DrawImage(self, canvas, scale, mx, my, image):
		image_object = self.z.images.GetImage(image[3])
		
		canvas.create_image(
			mx + (image[0] * scale),
			my + (image[1] * scale),
			image = image_object
		)
	
	def _DrawWalls(self, canvas, scale, mx, my):
		# Draw the walls
		set_back = World.WALL_SET_BACK * scale
		extension = World.WALL_EXTENSION * scale
		
		wall_width = World.WALL_WIDTH * scale
		wall_extension_width = World.WALL_EXTENSION_WIDTH * scale
		
		for wall in self.walls:
			x1 = mx + (wall[0] * scale)
			y1 = my + (wall[1] * scale)
			x2 = mx + (wall[2] * scale)
			y2 = my + (wall[3] * scale)
			
			# Define wall end extensions
			x1b = x1
			y1b = y1
			
			x2b = x2
			y2b = y2
			
			if x1 < x2:
				x1 += set_back
				x2 -= set_back
				
				x1b -= extension
				x2b += extension
				
			if x1 > x2:
				x1 -= set_back
				x2 += set_back
				
				x1b += extension
				x2b -= extension
			
			if y1 < y2:
				y1 += set_back
				y2 -= set_back
				
				y1b -= extension
				y2b += extension
				
			if y1 > y2:
				y1 -= set_back
				y2 += set_back
				
				y1b += extension
				y2b -= extension
			
			canvas.create_line(
				x1, y1, x2, y2,
				
				width = wall_width,
				fill = World.WALL_COLOUR
			)
			
			canvas.create_line(
				x1, y1, x1b, y1b,
				
				width = wall_extension_width,
				fill = World.WALL_COLOUR
			)
			
			canvas.create_line(
				x2, y2, x2b, y2b,
				
				width = wall_extension_width,
				fill = World.WALL_COLOUR
			)
			
	def SetWorld(self, world_data):
		self.SetSize(world_data["Width"], world_data["Height"])
		
		if "Background" in world_data:
			self.background_colour = world_data["Background"]
			
		else:
			self.background_colour = World.BACKGROUND_COLOUR
		
		if "Walls" in world_data:
			self.walls = world_data["Walls"]
			
		else:
			self.walls = []
			
		if "Objects" in world_data:
			self.objects = world_data["Objects"]
			
		else:
			self.objects = []
			
		if "Images" in world_data:
			self.images = world_data["Images"]
			
		else:
			self.images = []
			
	def AddEntity(self, entitie):
		self.entities.append(entitie)
		
	def ClearEntities(self):
		for entity in self.entities:
			entity.Kill()
	
		self.entities = []
		
######## WORLD OBJECTS ########

# All world objects must have an Update(canvas, scale, x_offset, y_offset) method

class ObjectText():
	def __init__(self, x, y, text, font, size, colour, anchor):
		self.x = x				# X location of the text (centre)
		self.y = y				# Y location of the text (centre)
		self.text = text		# The text to render
		self.font = font		# The font family e.g. "Times"
		self.size = size		# Font size
		self.colour = colour	# The text colour
		self.anchor = anchor	# The anchor of the text e.g. tkinter.NW or tkinter.CENTER
	
	def Update(self, canvas, scale, x_offset, y_offset):
		canvas.create_text(
			x_offset + (self.x * scale),
			y_offset + (self.y * scale),
			text = self.text,
			font = (self.font, int(self.size * scale)),
			fill = self.colour,
			anchor = self.anchor
		)

class Man():
	ANIMATION_TIME = 0.2
	WALK_SPEED = 4.0
	
	MOVE_UP = [38, 87]
	MOVE_DOWN = [40, 84]
	MOVE_LEFT = [37, 65]
	MOVE_RIGHT = [39, 68]
	
	COLIDE_RADIUS = 1.1

	def __init__(self, x, y, size):
		self.x = x			# X location of the man
		self.y = y			# Y location of the man
		
		self.size = size	# Relative size of the man (the width) The height is twice the width
		
		self.dir = False		# The direction the man is facing (True = Right)
		self.animation = False	# The current animation stage
		self.last_animation = 0	# The last time.time() the animation was flipped
		
		# Velocity and direction the man is travailing in
		self.velocity = 0.0		# Size units per second
		self.direction = 0.0	# Radians, up = right, going clockwise
		
		self.last_update = 0	# The last time the man was updated
		
		# Store the states of the controls (0, 1 or -1)
		self.xc = 0
		self.yc = 0
		
		# Store the key status
		self.up = False
		self.down = False
		self.left = False
		self.right = False
		
	def BindToControls(self, display):
		self.display = display
		display.AddKeyListener(self._KeyEvent)
		
	def Kill(self):
		self.display.RemoveKeyListener(self._KeyEvent)
		
	def _KeyEvent(self, event):
		if str(event.type) == "KeyPress":
			if event.keycode in Man.MOVE_LEFT:
				self.left = True
				self.xc = -1
				
			elif event.keycode in Man.MOVE_RIGHT:
				self.right = True
				self.xc = 1
				
			if event.keycode in Man.MOVE_UP:
				self.up = True
				self.yc = -1
				
			elif event.keycode in Man.MOVE_DOWN:
				self.down = True
				self.yc = 1
				
		elif str(event.type) == "KeyRelease":
			if event.keycode in Man.MOVE_LEFT:
				self.left = False
				self.xc = 0
				
				if self.right:
					self.xc = 1
				
			elif event.keycode in Man.MOVE_RIGHT:
				self.right = False
				self.xc = 0
				
				if self.left:
					self.xc = -1
				
			if event.keycode in Man.MOVE_UP:
				self.up = False
				self.yc = 0
				
				if self.down:
					self.yc = 1
				
			elif event.keycode in Man.MOVE_DOWN:
				self.down = False
				self.yc = 0
				
				if self.up:
					self.yc = -1
			
		if self.xc != 0 or self.yc != 0:
			self.velocity = Man.WALK_SPEED
			
		else:
			self.velocity = 0
			
		if self.xc > 0:
			self.dir = True
			
		elif self.xc < 0:
			self.dir = False
			
		self.direction = math.atan2(self.yc, self.xc)
		
	def Update(self, canvas, scale, x_offset, y_offset, world):
		# Change the animation stage if needed
		time_now = time.time()
		ani_time_passed = time_now - self.last_animation
		
		if ani_time_passed >= Man.ANIMATION_TIME:
			self.last_animation = time_now
			self.animation = not self.animation
		
		# Update movement
		if self.last_update == 0:
			self.last_update = time_now
			
		up_time_passed = time_now - self.last_update
		self.last_update = time_now
		
		self.x += math.cos(self.direction) * (self.velocity * up_time_passed)
		self.y += math.sin(self.direction) * (self.velocity * up_time_passed)
		
		# Collide with walls
		for wall in world.walls:
			# Find the distance and angle the man is relative to the first wall point (wall[0] and wall[1])
			wall_length = math.sqrt(math.pow(wall[3] - wall[1], 2) + math.pow(wall[2] - wall[0], 2))
			wall_theta = math.atan2(wall[3] - wall[1], wall[2] - wall[0])
			man_theta = math.atan2(self.y - wall[1], self.x - wall[0])
			relative_theta = man_theta - wall_theta
			man_distance = math.sqrt(math.pow(self.y - wall[1], 2) + math.pow(self.x - wall[0], 2))
			
			# Check if the man is facing the wall (find the adjacent length)
			distance_along = math.cos(relative_theta) * man_distance
			
			if distance_along < 0:	# The man is past point 1 (wall[0] and wall[1])
				# Check if the man is too close
				if abs(man_distance) < Man.COLIDE_RADIUS * self.size:	# Too close to the wall
					# Move the man out
					self.x = wall[0] + (math.cos(man_theta) * Man.COLIDE_RADIUS * self.size)
					self.y = wall[1] + (math.sin(man_theta) * Man.COLIDE_RADIUS * self.size)
					
			elif distance_along > wall_length:	# Do the same as above but with the second wall node
				man_distance2 = math.sqrt(math.pow(self.y - wall[3], 2) + math.pow(self.x - wall[2], 2))
				man_theta2 = math.atan2(self.y - wall[3], self.x - wall[2])
				
				if abs(man_distance2) < Man.COLIDE_RADIUS * self.size:	# Too close to the wall
					# Move the man out
					self.x = wall[2] + (math.cos(man_theta2) * Man.COLIDE_RADIUS * self.size)
					self.y = wall[3] + (math.sin(man_theta2) * Man.COLIDE_RADIUS * self.size)
					
			else:	
				# Check collisions with the whole wall
				distance_from_wall = math.sin(relative_theta) * man_distance
				
				if abs(distance_from_wall) < Man.COLIDE_RADIUS * self.size:	# Too close to the wall
					# Move the man
					d = 1.0
					
					if distance_from_wall < 0:
						d = -1.0
					
					new_theta = math.atan2(Man.COLIDE_RADIUS * self.size * d, distance_along)
					new_distance = math.sqrt(math.pow(Man.COLIDE_RADIUS * self.size, 2) + math.pow(distance_along, 2))
					
					self.x = wall[0] + (math.cos(new_theta + wall_theta) * new_distance)
					self.y = wall[1] + (math.sin(new_theta + wall_theta) * new_distance)
					
		# Check for matching points
		for point, callback in world.point_listeners:
			distance = math.sqrt(math.pow(point[0] - self.x, 2) + math.pow(point[1] - self.y, 2))
			
			if distance <= World.POINT_DISTANCE:	# Man is in the point!
				callback(self)
	
		# Render the main body (no animation)
		canvas.create_line(		# Head
			x_offset + (self.x * scale),
			y_offset + ((self.y - (self.size)) * scale),
			x_offset + (self.x * scale),
			y_offset + ((self.y - (self.size * 0.7)) * scale),
			width = (self.size * 0.2) * scale
		)
		
		canvas.create_line(		# Body
			x_offset + (self.x * scale),
			y_offset + ((self.y - (self.size * 0.6)) * scale),
			x_offset + (self.x * scale),
			y_offset + ((self.y + (self.size * 0.6)) * scale),
			width = (self.size * 0.2) * scale
		)
		
		# Render the arms and legs
		dir = [-1.0, 1.0][self.dir]
		
		if self.animation:
			canvas.create_line(		# Back leg
				x_offset + ((self.x - (self.size * 0.2 * dir)) * scale),
				y_offset + ((self.y + (self.size * 0.55)) * scale),
				x_offset + ((self.x - (self.size * 0.3 * dir)) * scale),
				y_offset + ((self.y + self.size) * scale),
				width = (self.size * 0.2) * scale
			)
			
			canvas.create_line(		# Front leg
				x_offset + ((self.x + (self.size * 0.1 * dir)) * scale),
				y_offset + ((self.y + (self.size * 0.5)) * scale),
				x_offset + ((self.x + (self.size * 0.3 * dir)) * scale),
				y_offset + ((self.y + self.size) * scale),
				width = (self.size * 0.2) * scale
			)
			
			canvas.create_line(		# Upper arm 1
				x_offset + (self.x * scale),
				y_offset + ((self.y - (self.size * 0.52)) * scale),
				x_offset + ((self.x + (self.size * 0.45 * dir)) * scale),
				y_offset + ((self.y - (self.size * 0.55)) * scale),
				width = (self.size * 0.18) * scale
			)
			
			canvas.create_line(		# Upper arm 2
				x_offset + ((self.x + (self.size * 0.3 * dir)) * scale),
				y_offset + ((self.y - (self.size * 0.45)) * scale),
				x_offset + ((self.x + (self.size * 0.6 * dir)) * scale),
				y_offset + ((self.y - (self.size * 0.45)) * scale),
				width = (self.size * 0.16) * scale
			)
			
			canvas.create_line(		# Lower arm 1
				x_offset + (self.x * scale),
				y_offset + ((self.y - (self.size * 0.25)) * scale),
				x_offset + ((self.x + (self.size * 0.35 * dir)) * scale),
				y_offset + ((self.y - (self.size * 0.25)) * scale),
				width = (self.size * 0.16) * scale
			)
			
			canvas.create_line(		# Lower arm 2
				x_offset + ((self.x + (self.size * 0.3 * dir)) * scale),
				y_offset + ((self.y - (self.size * 0.15)) * scale),
				x_offset + ((self.x + (self.size * 0.55 * dir)) * scale),
				y_offset + ((self.y - (self.size * 0.15)) * scale),
				width = (self.size * 0.16) * scale
			)
			
		else:
			canvas.create_line(		# Back leg
				x_offset + ((self.x - (self.size * 0.2 * dir)) * scale),
				y_offset + ((self.y + (self.size * 0.5)) * scale),
				x_offset + ((self.x - (self.size * 0.2 * dir)) * scale),
				y_offset + ((self.y + self.size) * scale),
				width = (self.size * 0.2) * scale
			)
			
			canvas.create_line(		# Front leg
				x_offset + ((self.x + (self.size * 0.2 * dir)) * scale),
				y_offset + ((self.y + (self.size * 0.4)) * scale),
				x_offset + ((self.x + (self.size * 0.2 * dir)) * scale),
				y_offset + ((self.y + self.size) * scale),
				width = (self.size * 0.2) * scale
			)
			
			canvas.create_line(		# Upper arm 1
				x_offset + (self.x * scale),
				y_offset + ((self.y - (self.size * 0.5)) * scale),
				x_offset + ((self.x + (self.size * 0.45 * dir)) * scale),
				y_offset + ((self.y - (self.size * 0.5)) * scale),
				width = (self.size * 0.2) * scale
			)
			
			canvas.create_line(		# Upper arm 2
				x_offset + ((self.x + (self.size * 0.3 * dir)) * scale),
				y_offset + ((self.y - (self.size * 0.4)) * scale),
				x_offset + ((self.x + (self.size * 0.6 * dir)) * scale),
				y_offset + ((self.y - (self.size * 0.4)) * scale),
				width = (self.size * 0.16) * scale
			)
			
			canvas.create_line(		# Lower arm 1
				x_offset + (self.x * scale),
				y_offset + ((self.y - (self.size * 0.2)) * scale),
				x_offset + ((self.x + (self.size * 0.35 * dir)) * scale),
				y_offset + ((self.y - (self.size * 0.2)) * scale),
				width = (self.size * 0.16) * scale
			)
			
			canvas.create_line(		# Lower arm 2
				x_offset + ((self.x + (self.size * 0.3 * dir)) * scale),
				y_offset + ((self.y - (self.size * 0.1)) * scale),
				x_offset + ((self.x + (self.size * 0.55 * dir)) * scale),
				y_offset + ((self.y - (self.size * 0.1)) * scale),
				width = (self.size * 0.16) * scale
			)
			
		# Draw a circle to show the COLIDE_RADIUS
		#canvas.create_oval(
		#	x_offset + ((self.x - (self.size * Man.COLIDE_RADIUS))  * scale),
		#	y_offset + ((self.y - (self.size * Man.COLIDE_RADIUS))  * scale),
		#	x_offset + ((self.x + (self.size * Man.COLIDE_RADIUS)) * scale),
		#	y_offset + ((self.y + (self.size * Man.COLIDE_RADIUS)) * scale)
		#)
		