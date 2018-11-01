import os
import sys
import db_functions
import fs_functions
import dropbox
import random
import platform
import tk_functions as tkfuncs
import keybinds
import textwrap
import json

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
	
class spawnWindows:
	intro_string = """
	It looks like you haven't linked your DropBox account to the app yet.
	In order to set up the program, you will need to link it via
	a developer access token from Dropbox. I can't make a login box 
	as far as I'm aware without Dropbox Business API, and this is a free app.
	To get your specific key:
	"""
	setup_string = """\
	2: Click on "Create App"
	3: Select Dropbox API (Not Dropbox Business API)
	4: Choose Full Dropbox as the access type (User data isn't sent anywhere external)
	5: Name it whatever you want(nonsense works, it wont be actively used)
	6: Agree to the DropBox terms and conditions, and click "Create App"
	7: On the next page, under OAuth2, click "Generate Access Token"
	8: Paste said access token into the token box below and click done
		(Do not share this token with anyone)
	9: Enter your root folder for the program to use in the course box
		e.g. /FOSSCards/ - The root will hold all course folders e.g. 
		 /FOSSCards/Math/, /FOSSCards/English/, etc...
	"""
	def __init__(self, frame):
		self.intro_string = textwrap.dedent(self.intro_string)
		self.setup_string = textwrap.dedent(self.setup_string)
		self.frame = frame
		frame.withdraw()
		if platform.system() != 'Windows':
			self.datFilePath = (os.getcwd()+'/lib/dat')
		else:
			self.datFilePath = (os.getcwd()+'\\lib\\dat')
			
		if os.path.exists(self.datFilePath):
			with open(self.datFilePath, 'r') as f:
				self.data = json.load(f)
				self.accessToken = self.data["token"]
				self.db_root = self.data["root"]
			if self.accessToken != '':
				self.initialize()
				return
		self.first_time_setup()

	def first_time_setup(self):
		"""
		Used for setting up the users dropbox folder, spawns a window
		and prints the instructions to create the access token and main folder
		"""
		self.setup_frame = tk.Toplevel(self.frame)
		self.setup_frame.wm_title("Set Up Dropbox")
		self.setup_frame.resizable(False, False)
		upperLabel = tk.Label(self.setup_frame, text=self.intro_string)
		iLabel = tk.Label(self.setup_frame, text="1: Follow this link",
						 justify=tk.LEFT, fg="blue", cursor="hand2")
		lowerLabel = tk.Label(self.setup_frame, 
							  text=self.setup_string, justify=tk.LEFT)
		ok_button = tk.Button(self.setup_frame, text="OK", 
				  command = lambda: self.setup_done(course_entry.get(),
												   token_entry.get()))
		
		self.setup_token_frame = tk.Frame(self.setup_frame)
		token_label = tk.Label(self.setup_token_frame, text="Token: ")
		token_entry = tk.Entry(self.setup_token_frame)
		token_label.pack(side=tk.LEFT)
		token_entry.pack()
		
		self.setup_course_frame = tk.Frame(self.setup_frame)
		course_label = tk.Label(self.setup_course_frame, text="Path: ")
		course_entry = tk.Entry(self.setup_course_frame)
		course_label.pack(side=tk.LEFT)
		course_entry.pack()
			
		upperLabel.pack()
		iLabel.pack()
		lowerLabel.pack()
		self.setup_token_frame.pack()
		self.setup_course_frame.pack()
		ok_button.pack()
		bkbs = keybinds.Funcs('pass')
		iLabel.bind("<Button-1>", lambda e: bkbs.hyperLink())
		
	def setup_done(self, course_folder, accessToken):
		"""
		Finalizes first time setup, normally functions like this would occur
		in the tk_functions class/file, but we have not initialized it since
		we have no dropbox string. 
		This should probably be changed later as I'm sure
		people wont like having to link db to use it, but for
		current purposes its fine.
		"""
		if accessToken == "" or course_folder == "":
			return
		self.db_root = course_folder
		self.accessToken = accessToken
		self.setup_frame.withdraw()
		with open(self.datFilePath, 'w') as f:
			data = {"token":self.accessToken, "root":self.db_root}
			json.dump(data, f)
		self.initialize()
		
			
	def initialize(self):
		"""
		In all my programming jenyus I had to split the __init__ function
		to accomodate for checking the accessToken (as breaking out into a new
		window will not stop the initalize function from running). So this is
		the init function that should technically be __init__()
		"""
		self.frame.deiconify()#bring the main window back up after first init
		transferData = tkfuncs.TransferData(self.accessToken)
		self.flashText = tk.StringVar()
		self.progressText = tk.StringVar()
		self.q_text = tk.StringVar()
		self.progressText.set("0 Left")
		self.q_text.set("From: N/A")
		self.frame.configure(bg = 'white')
		self.dbx = dropbox.Dropbox(self.accessToken)
		self.root_fs_folder = os.getcwd()
		
		
		#initiate the fs_functions class here
		self.fs_functions = fs_functions.Funcs(self.root_fs_folder)
		#initiate the db_functions class here
		self.db_functions = db_functions.Funcs(self.dbx, self.fs_functions,
					self.db_root, self.root_fs_folder)
		#initiate the tkFuncs class, because sharing is caring
		self.funcs = tkfuncs.tkFuncs(self.db_functions, self.fs_functions,
					self.flashText, self.progressText, self.q_text,
					self.frame, transferData)
		#initiate the keybinds class
		self.kbs = keybinds.Funcs(self.funcs)
		
		#Get the preferences from the saved preferences file
		self.dl_o, self.sync_o =  self.fs_functions.retrieve_prefs()
		self.funcs.save_prefs("pass", self.sync_o, self.dl_o)
		
		
		#creating a menu system for items that dont need to always be shown
		menu = tk.Menu(self.frame)
		self.frame.config(menu=menu)
		filemenu = tk.Menu(menu, tearoff=0)
		menu.add_cascade(label="File", menu=filemenu)
		filemenu.add_command(label="Select Course", 
							 command = lambda: self.select_course_window())
		filemenu.add_command(label="Create/Edit Notecards", 
							 command = lambda: self.edit_notecards_window())
		filemenu.add_command(label="Sync Course Files", command = 
			 lambda: self.db_functions.sync(transferData,
						self.funcs.course_folder))
		filemenu.add_separator()
		filemenu.add_command(label="Exit", command= self.frame.quit)
		
		settings_menu = tk.Menu(menu, tearoff=0)
		menu.add_cascade(label="Settings", menu=settings_menu)
		settings_menu.add_command(label="Preferences",
								  command = lambda: self.preferences_window())
		
		
		#Setting up the Label that the flashcard data goes into
		flashFrame = tk.Frame(self.frame)
		self.flashCard = tk.Label(flashFrame, textvariable=self.flashText,
			font=("Helvetica", 32),	bg='white',
			justify=tk.LEFT, wraplength=1000)
		self.funcs.init_fcard( self.flashCard)
		
		
		#Setting up buttons that go along the top of the frame
		top_button_frame = tk.Frame(self.frame)
		restart_button = tk.Button(top_button_frame, padx=75, text="Restart",
			    command = lambda: self.funcs.restart())
		shuffle_button = tk.Button(top_button_frame, padx=75, text="Shuffle", 
			    command = lambda: self.funcs.shuffle_set
								   ())
		
		#Flip button along the bottom
		flip_button = tk.Button(self.frame, text="Flip", padx=700, 
				 command = lambda: self.funcs.flip_card())
		
		#Setting up right and wrong answer buttons
		right_button = tk.Button(self.frame, text="Right", pady=220, padx=15,
				 command = lambda: self.funcs.call_right())
		wrong_button = tk.Button(self.frame, text="Wrong", pady=220, 
				 command = lambda: self.funcs.call_wrong())
		
		#Setting up the info bar on the bottom
		info_bar_frame = tk.Frame(self.frame)
		progress_label = tk.Label(info_bar_frame,
					textvariable = self.progressText, font=("Helvetica", 8),
					justify = tk.RIGHT, padx=300)
		q_from_label = tk.Label(info_bar_frame,
					textvariable = self.q_text, font=("Helvetica", 8),
					justify = tk.LEFT, padx=300)
		q_from_label.pack(side=tk.LEFT)
		progress_label.pack(side=tk.RIGHT)
	
		#pack everything in a super specific order
		info_bar_frame.pack(side=tk.BOTTOM)
		right_button.pack(side=tk.RIGHT)
		wrong_button.pack(side=tk.LEFT)	
		restart_button.pack(side=tk.LEFT)
		shuffle_button.pack(side=tk.LEFT)
		top_button_frame.pack(side=tk.TOP)
		flip_button.pack(side=tk.BOTTOM)
		flashFrame.pack(side=tk.TOP, expand=True)
		self.flashCard.pack(expand=True)
		
		
		self.center(self.frame)
		
		#Calls the select course window, because no course is selected by default
		self.select_course_window()
	
	def center(self, win):
		win.update()
		w_req, h_req = win.winfo_width(), win.winfo_height()
		w_form = win.winfo_rootx() - win.winfo_x()
		w = w_req + w_form*2
		h = h_req + (win.winfo_rooty() - win.winfo_y()) + w_form
		x = (win.winfo_screenwidth() // 2) - (w // 2)
		y = (win.winfo_screenheight() // 2) - (h // 2)
		win.geometry('{0}x{1}+{2}+{3}'.format(w_req, h_req, x, y))
		win.lift()
		
	def select_course_window(self):
		"""
		Spawns a window that contains a list of all the folders available
		in the db account (from root, at this point in time) and allows the
		user to select a course(folder) from the list so that they can go
		over the flash cards from that folder
		"""
		self.c_sel_frame = tk.Toplevel(self.frame)
		self.c_sel_frame.wm_title("Select A Course")
		self.c_sel_frame.resizable(False, False)
		l = tk.Label(self.c_sel_frame, text="Select A Course")
		
		#setting up the listbox, with a default value to suppress empty selection errors
		self.course_listbox = tk.Listbox(self.c_sel_frame, selectmode = tk.SINGLE)
		course_list = self.db_functions.get_all_folders()
		for item in course_list:
			self.course_listbox.insert(tk.END, item)
		self.course_listbox.select_set(0)
		self.course_listbox.event_generate("<<ListboxSelect>>")
		
		self.scrollbar = tk.Scrollbar(self.course_listbox, orient=tk.VERTICAL)
		self.scrollbar.config(command=self.course_listbox.yview)
		
		self.course_listbox.config(yscrollcommand=self.scrollbar.set)
		
		ok_button = tk.Button(self.c_sel_frame, text="OK", 
				  command = lambda: self.funcs.select_new_course(
								self.course_listbox.get(
									self.course_listbox.curselection()), 
										 self.c_sel_frame))
		add_button = tk.Button(self.c_sel_frame, text="Add Course", 
				  command = lambda: self.add_new_course_window())
		
		l.pack()
		self.course_listbox.pack()
		ok_button.pack(side=tk.RIGHT)
		add_button.pack(side=tk.LEFT)
		self.center(self.c_sel_frame)
		
		
	def add_new_course_window(self):
		"""
		Spawn a window with a label to enter the name of the course to add,
		also provides a cancel option
		"""
		self.c_add_frame = tk.Toplevel(self.c_sel_frame)
		self.c_add_frame.wm_title("Name the Course")
		self.c_add_frame.resizable(False, False)
		c_entry = tk.Entry(self.c_add_frame)
		c_entry.pack()
		
		ok_button = tk.Button(self.c_add_frame, 
			text="OK", command = lambda: self.funcs.add_new_course(c_entry.get(), self.c_add_frame, self.c_sel_frame))
		cancel_button = tk.Button(self.c_add_frame, text="Cancel",
			command = lambda: self.c_add_frame.withdraw())
		
		cancel_button.pack(side=tk.LEFT)
		ok_button.pack(side=tk.RIGHT)
		self.center(self.c_add_frame)
		
	def edit_notecards_window(self):
		"""
		Spawns a window used for editing flashcards
		"""
		self.questions = []
		self.answers = []
		
		self.edit_cards_frame = tk.Toplevel(self.frame, width=500, height=400)
		self.edit_cards_frame.wm_title("Edit Notecards")
		self.edit_cards_frame.resizable(False, False)

		
		question_label = tk.Label(self.edit_cards_frame, text="Question:",
								 font=("Helvetica", 12))
		answer_label = tk.Label(self.edit_cards_frame, text="Answer:",
							   font=("Helvetica", 12))
		card_answer_box = tk.Text(self.edit_cards_frame, bd = 30, 
				font=("Helvetica", 16), height = 7, width = 40, 
				padx=20, pady=20, relief=tk.SUNKEN, wrap=tk.WORD)
		card_question_box = tk.Text(self.edit_cards_frame, bd = 30, 
				font=("Helvetica", 16), height = 7, width = 40, 
				padx=20, pady=20, relief=tk.SUNKEN, wrap=tk.WORD)
		card_listbox = tk.Listbox(self.edit_cards_frame,bd=5, height=42, 
				 width=25, selectmode = tk.SINGLE)
		card_scrollbar = tk.Scrollbar(card_listbox, orient=tk.VERTICAL)
		card_scrollbar.config(command=card_listbox.yview)
		card_listbox.config(yscrollcommand=card_scrollbar.set)
		
		menu = tk.Menu(self.edit_cards_frame)
		self.edit_cards_frame.config(menu=menu)
		filemenu = tk.Menu(menu, tearoff=0)
		menu.add_cascade(label="File", menu=filemenu)
		filemenu.add_command(label="Select File", 
				 command = lambda: 	self.init_edit_window(
					 card_question_box,card_answer_box,card_listbox))
		
		add_card_button = tk.Button(self.edit_cards_frame, text=">",
				command = lambda: self.funcs.add_new_card( 
				self.questions, self.answers,
				card_question_box, card_answer_box, card_listbox))
		
		edit_card_button = tk.Button(self.edit_cards_frame, text="<",
				command = lambda: self.funcs.retrieve_card(
				self.questions, self.answers,
				card_question_box, card_answer_box, card_listbox))
		
		done_button = tk.Button(self.edit_cards_frame, text="Save",
			command = lambda: self.funcs.save_notecard(card_question_box,
				card_answer_box, self.questions, self.answers, 
					self.funcs.course))
		
		delete_button = tk.Button(self.edit_cards_frame, text="Delete Selected",
			command = lambda: self.funcs.delete_selected_lb_item(
			self.questions, self.answers, card_listbox))
		
		cancel_button = tk.Button(self.edit_cards_frame, text="Cancel",
			command = lambda: self.edit_cards_frame.withdraw())
		
		#keybinds to switch between writing questions and answers
		#Used a seperate method instead of just x.focus
		#in order to stop Tab putting in a tab character
		card_question_box.bind('<Tab>', lambda e: self.kbs.switchFocus(card_answer_box))
		card_answer_box.bind('<Tab>', lambda e: self.kbs.switchFocus(card_question_box))
		
		card_question_box.bind('<Control-Return>', lambda e: 
				self.kbs.addCard(
				self.questions, self.answers,
				card_question_box, card_answer_box, card_listbox))
		card_answer_box.bind('<Control-Return>', lambda e: 
				self.kbs.addCard(
				self.questions, self.answers,
				card_question_box, card_answer_box, card_listbox))

		card_listbox.pack(side=tk.RIGHT)
		add_card_button.pack(side=tk.RIGHT)
		edit_card_button.pack(side=tk.RIGHT)
		question_label.pack(side=tk.TOP)
		card_question_box.pack(side=tk.TOP)
		answer_label.pack(side=tk.TOP)
		card_answer_box.pack(side=tk.TOP)
		done_button.pack(side=tk.LEFT)
		delete_button.pack(side=tk.RIGHT)
		cancel_button.pack(side=tk.BOTTOM)
		
		self.center(self.edit_cards_frame)
		
	def init_edit_window(self, qb, ab, lb):
		"""
		breakout method for the file select lambda to pass
		the question and answer lists back up the chain to populate
		the self.questions and self.answers lists here.
		"""
		self.questions, self.answers = self.funcs.populate_edit_window(
					self.questions, self.answers, qb,
					ab, lb)
		self.edit_cards_frame.lift()
		
		
	def preferences_window(self):
		"""
		Spawns a window for editing preferences on the functionality
		of the program
		"""
		sync_o_option = tk.IntVar().set(self.sync_o)
		dl_o_option = tk.IntVar().set(self.dl_o)
		
		p_frame = tk.Toplevel(self.frame, width=300, height=300)
		p_frame.winfo_toplevel().title("Preferences")
		self.center(p_frame)
		
		sync_o_frame = tk.Frame(p_frame, width=300, height = 200, 
						highlightbackground = "black",
							highlightcolor="black",
								highlightthickness=1, bd=1)
		a_label = tk.Label(sync_o_frame, text="Sync Options")
		a_label.pack(anchor=tk.W)
		tk.Radiobutton(sync_o_frame, text="Overrides Dropbox files",
					  variable = sync_o_option, value = 0).pack(anchor=tk.W)
		tk.Radiobutton(sync_o_frame, text="Asks to override Dropbox files",
					  variable = sync_o_option, value = 1).pack(anchor=tk.W)
		sync_o_frame.pack(anchor=tk.W, fill=tk.X)
		
		dl_o_frame = tk.Frame(p_frame, width=300, height = 200, 
						highlightbackground = "black",
							highlightcolor="black",
								highlightthickness=1, bd=1)
		a_label = tk.Label(dl_o_frame, text="Download Options")
		a_label.pack(anchor=tk.W)
		tk.Radiobutton(dl_o_frame, text="Overrides Local files",
					  variable = dl_o_option, value = 0).pack(anchor=tk.W)
		tk.Radiobutton(dl_o_frame, text="Asks to override Local files",
					  variable = dl_o_option, value = 1).pack(anchor=tk.W)
		dl_o_frame.pack(anchor=tk.W, fill=tk.X)
		
		done_button = tk.Button(p_frame, text="Save",
			command = lambda: self.funcs.save_prefs(p_frame,
							sync_o_option.get(), dl_o_option.get()))
		done_button.pack(side=tk.BOTTOM)
		
		
		
		