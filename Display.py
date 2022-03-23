# Title:	Display module for Zombie
# Author:	Nicholas Wright
# Info:		To be used with Zombie.py
# Version:	v0.0

import time
import tkinter

# Creates a GUI window to play a game

class Display():
	MIN_WIDTH = 800		# Minimum window width
	MIN_HEIGHT = 700	# Minimum window height
	REFRESH_RATE = 40	# Refresh rate in Hz
	
	MINIMUM_WAIT_TIME = 0.01	# The minimum time which the process waits for between renders (100 FPS)
	STAT_X = 6					# X position of the statistics display
	STAT_Y = 6					# Y position of the statistics display
	STAT_SIZE = 14				# Font size of the statistics display
	
	STATS_KEY = 123				# Key binding for showing stats

	def __init__(self, draw_function, title):
		# Required values
		self.draw_function = draw_function		# A function of the form: def Draw(canvas, width, height)
		self.title = title						# The name of the window
		
		# Values which may be modified
		self.max_fps = Display.REFRESH_RATE		# Maximum FPS allowed
		self.show_stats = False					# If statistics should be shown on the screen (e.g. fps)
		self.on_ready = None					# A function to run when the display is ready
		
		self.key_listeners = []					# A list of methods to call when a key is pressed
		
		# Running variables
		self.alive = False						# If the window is active or not
		self.last_stats = 0						# The last time.time() the stats were calculated
		self.frame_count = 0					# Counts updates to calculate the FPS
		self.render_time_sum = 0				# The sum of the time it takes to render a frame
		self.fps = 0							# The measured FPS
		self.render_duty = 0					# A ratio of the time it takes to render a frame to the total time passed
		
		self.screen = None						# Tkinter screen object
		self.flip = False						# Which buffer is visible
		self.buffers = [None, None]				# Canvas Objects
		
		self.width = Display.MIN_WIDTH
		self.height = Display.MIN_HEIGHT
		
		# Misc
		self.font = ("Monospace", Display.STAT_SIZE)
		
	def AddKeyListener(self, listener):
		self.key_listeners.append(listener)
		
	def RemoveKeyListener(self, listener):
		new_listeners = []
		
		for l in self.key_listeners:
			if l != listener:
				new_listeners.append(l)
				
		self.key_listeners = new_listeners
		
	def MainLoop(self, on_ready = None):							# Open the window and call the draw_function on every update
		self.on_ready = on_ready
		# Open the display
		self._Setup()
		
		# Set the first callback
		self.screen.after(int(1000.0 / self.max_fps), self._Update)
		
		# Main loop
		self.alive = True
		self.screen.mainloop()
		self.alive = False
		
	def _Setup(self):
		# Create the screen
		self.screen = tkinter.Tk()
		self.screen.title(self.title)
		self.screen.minsize(Display.MIN_WIDTH, Display.MIN_HEIGHT)
		self.screen.bind("<Configure>", self._OnResize)				# Call _OnResize when the window is resized
		self.screen.bind("<KeyPress>", self._OnKeyEvent)
		self.screen.bind("<KeyRelease>", self._OnKeyEvent)
		
		# Create the canvass, one for each buffer
		for i in range(2):
			self.buffers[i] = tkinter.Canvas(
			self.screen, 
			width = self.width,
			height = self.height,
			bd = 0							# Set border width
		)
		
		self.buffers[self.flip].place(x = 0, y = 0)	# Place the first buffer
		
	def _OnKeyEvent(self, event):
		for listener in self.key_listeners:
			listener(event)
			
		# Custom
		if str(event.type) == "KeyPress" and event.keycode == Display.STATS_KEY:
			self.show_stats = not self.show_stats
		
	def _Update(self):
		# Run the on_ready if set
		if self.on_ready != None:
			self.on_ready()
			self.on_ready = None
	
		# Find the time passed since the last update and calculate the FPS
		render_start = time.time()
		time_passed = render_start - self.last_stats
		
		self.frame_count += 1
		
		if time_passed >= 1.0:	# 1 second passed, set the FPS
			self.last_stats = render_start
			
			# Calculate stats
			self.fps = self.frame_count
			self.render_duty = (self.render_time_sum / self.frame_count) / time_passed
			
			self.frame_count = 0
			self.render_time_sum = 0
		
		# Flip the buffers
		self.flip = not self.flip
		
		# Update everything
		self.buffers[self.flip].delete("all")			# Clear the canvas
		self.draw_function(self.buffers[self.flip], self.width, self.height)
		
		self.buffers[self.flip].place(x = 0, y = 0)
		self.buffers[not self.flip].place_forget()
		
		# Display the FPS and duty cycle if needed
		if self.show_stats:
			stats = str(self.fps) + " FPS, Rendering @ " + str(round(self.render_duty * 100, 2)) + "%"
			self.buffers[self.flip].create_text(
				Display.STAT_X, 
				Display.STAT_Y, 
				font = self.font, 
				text = stats,
				anchor = tkinter.NW)
		
		# Calculate the render time and time to sleep until the next frame
		time_passed = time.time() - render_start
		self.render_time_sum += time_passed
		
		wait_time = (1.0 / self.max_fps) - time_passed
		
		if wait_time < Display.MINIMUM_WAIT_TIME:		# Restrict the render cycle from taking up everything
			wait_time = Display.MINIMUM_WAIT_TIME

		self.screen.after(int(1000.0 * wait_time), self._Update)
		
	def _OnResize(self, event):
		# Return if not running yet
		if not self.alive:
			return
	
		# Get the new size
		self.width = self.screen.winfo_width()
		self.height = self.screen.winfo_height()
		
		# Configure the canvas
		for i in range(2):	
			self.buffers[i].configure(
				width = self.width,
				height = self.height,
			)