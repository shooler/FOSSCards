"""
File for keybinds
"""
import sys
import tk_functions as tkfuncs
import webbrowser

if sys.version.startswith('2'):
	pyver = 2
	import Tkinter as tk
	import tkFileDialog	
	import tkMessageBox as messagebox
else:
	import tkinter as tk
	from tkinter import filedialog
	tkFileDialog = filedialog
	from tkinter import messagebox
	
class Funcs:
	def __init__(self, tkfuncs):
		self.tkfuncs = tkfuncs
		
	def switchFocus(self, box):
		"""
		binds Tab to switch between the question 
		and answer boxes in the Notecard Creation window
		"""	
		box.focus()
		return("break")


	def addCard(self, q, a, qb, ab, lb):
		"""
		binds Control+Enter in question and answer box to
		add the current card to the stack
		"""
		self.tkfuncs.add_new_card(q, a, qb, ab, lb)
		return("break")

	def hyperLink(self):
		"""
		Used for opening up the hyperlink in the setup text
		"""
		webbrowser.open_new("https://www.dropbox.com/developers/apps")