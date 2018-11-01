import sys
import os
import fs_functions
import dropbox
import random
import platform
import tk_windows

if sys.version.startswith('2'):
	import Tkinter as tk
	import tkFileDialog	
	import tkMessageBox as messagebox
else:
	import tkinter as tk
	from tkinter import filedialog
	tkFileDialog = filedialog
	from tkinter import messagebox

#This class is just called to setup the dbx variable to allow for file manipulation
class TransferData:
	def __init__(self, access_token):
		self.access_token = access_token
		self.dbx = dropbox.Dropbox(self.access_token)

	def upload_file(self, file_from, file_to):
		with open(file_from, 'rb') as f:
			self.dbx.files_upload(f.read(), file_to)

class tkFuncs:
	def __init__(self, db_functions, fs_functions, 
				 flashText, progressText, q_text, frame, transferData):
		frame.resizable(False, False)
		#Setting up class variables
		self.fs_functions = fs_functions
		self.db_functions = db_functions
		self.course_folder = ''
		self.course = ''
		self.frame = frame
		self.answers = ['empty']
		self.questions = ['empty']
		self.q_from = ['empty']
		self.q_text = q_text
		self.isQ = 1
		self.flashText = flashText
		self.progressText = progressText
		
		#set the window title, will rename when a new course is selected
		frame.title('Flashcards For: ' + self.course)
	
	def init_fcard(self, fcard):
		"""
		Initializes the self.fcard variable passed in from tk_windows
		"""
		self.fcard = fcard
	
	def set_card(self):
		""" 
		Used to ensure that the next flashcard will be Question first,
		not answer first, via the isQ variable
		"""
		if self.isQ == 0:
			self.flip_card()
		self.flashText.set(self.questions[0])
		self.q_text.set("From: "+self.q_from[0])

	def flip_card(self):
		"""
		If the card is currently showing the answer, then show the
		question, and vice versa, via the isQ variable and the
		2 lists (questions and answers) of the same index
		"""
		if self.flashText.get() == 'Finished!':
			return
		if self.isQ == 1:
			self.isQ = 0
			self.fcard.configure(font = 'Helvetica 32 bold')
			self.flashText.set(self.answers[0])
		else:
			self.isQ = 1
			self.fcard.configure(font = 'Helvetica 32')
			self.flashText.set(self.questions[0])

	def call_right(self):
		"""
		When the Right answer button is pressed, the card is removed
		from the stack, and if the last card was pulled out of the 
		stack then it lets you know you are done, and you won't
		be able to keep pressing right afterwards
		"""
		if len(self.questions) == 1:
			self.flashText.set("Finished!")
			self.progressText.set('Finished!')
			return
		del self.questions[0]
		del self.answers[0]
		del self.q_from[0]
		self.progressText.set(str(len(self.questions)-1) + ' Left')
		self.set_card()
	

	def call_wrong(self):
		"""
		When the Wrong answer button is pressed, the card is moved
		to the bottom of the stack, if the text is Finished! though,
		We just won't do anything since we are done with the cards.
		"""
		if self.flashText.get() == 'Finished!':
			return
		self.questions.append(self.questions.pop(0))
		self.answers.append(self.answers.pop(0))
		self.q_from.append(self.q_from.pop(0))
		self.set_card()

	def shuffle_set(self):
		"""
		A basic function to randomize the order of the cards by
		popping a random value from the list and appending it to the end
		"""	
		shuffler = random.sample(xrange(len(self.questions)), len(self.questions))
		for i in shuffler:
			self.questions.append(self.questions.pop(i))
			self.answers.append(self.answers.pop(i))
			self.q_from.append(self.q_from.pop(i))
		self.set_card()

	def restart(self):
		"""
		Resets the questions and answers lists to original downloaded
		values, and calls set_card()
		"""
		self.frame.title('Flashcards For: ' + self.course)
		self.questions, self.answers, self.q_from = self.fs_functions.get_questions(self.course)
		self.set_card()
		self.progressText.set(str(len(self.questions)-1) + ' Left')
		
	def add_new_course(self, name, add_frame, sel_frame):
		"""
		checks if the course the user is trying to create already exists,
		if it does an error message is thrown, otherwise it closes out of
		the creating windows and calls necessary functions for creation
		"""
		if name in self.db_functions.get_all_folders():
			messagebox.showerror("Error", "Folder already exists")
			return
		self.db_functions.add_new_course(name)
		add_frame.withdraw()
		self.select_new_course(name, sel_frame)
	
	def select_new_course(self, name, frame):
		"""
		Changes the name of the selected course for all functions in the class,
		as well as path, and then downloads the files and restarts the main window
		"""
		self.course = name
		self.course_folder = (self.course + '/')
		self.db_functions.download(self.course_folder)
		if platform.system() != 'Windows':
			if os.getcwd().split('/')[-1] != self.course:
				os.chdir("./" + self.course + "/")
		elif os.getcwd().split('\\')[-1] != self.course:
			os.chdir(".\\" + self.course + "\\")
		self.restart()
		frame.withdraw()
		
	#####	END MAIN WINDOW FUNCTIONS	#####
	
	def add_new_card(self, ql, al, q, a, lb):
		"""
		Used for adding a complete card (question and answer) to the listbox
		in the card creating dialog, as well as add them to question and answer
		lists for that set
		
		At some point this should probably check for any amount of whitespace
		"""
		#set variables for the text, and only the text, no newlines!
		qt = q.get("1.0", tk.END).rstrip()
		at = a.get("1.0", tk.END).rstrip()
		
		#dont make anything if its just blank
		if at == '' or at == '':
			return
		
		#add to class variables to hold the created q's and a's
		ql.append(qt)
		al.append(at)
		
		#update the listbox to show you added the card(s)
		lb.insert(lb.size(), qt)
		
		#clear out the boxes
		q.delete("1.0", tk.END)
		a.delete("1.0", tk.END)
		
		#returns break because this is a keybound function
		return("break")
		
	def retrieve_card(self, ql, al, q, a, lb):
		"""
		Retrieves a card from the listbox, and adds the question and answers
		into their respective boxes, while removing them from the stack
		"""
		#curselection returns an index as a tuple for whatever reason
		cs = lb.curselection()[0]
		
		#if there is a question in the boxes, add it to the list
		self.add_new_card(ql, al, q, a, lb)
		
		#make sure there is no text in the boxes
		q.delete("1.0", tk.END)
		a.delete("1.0", tk.END)

		#insert the text from the two lists corresponding to the index
		#of the selection in the listbox
		q.insert(tk.END, ql[cs])
		a.insert(tk.END, al[cs])
		
		#clear out the listbox selection and the lists indexed selection
		lb.delete(cs)
		del ql[cs]
		del al[cs]
		
	def delete_selected_lb_item(self, ql, al, lb):
		"""
		Deletes the item currently selected in the listbox
		of cards
		"""
		cs = lb.curselection()[0]
		lb.delete(cs)
		del ql[cs]
		del al[cs]
		
	def populate_edit_window(self, q, a, qb, ab, lb):
		"""
		Pulls in the questions and makes the list for the 
		edit notecard window
		"""
		#clear out the listbox
		lb.delete(0, tk.END)
		q, a = self.fs_functions.open_notecard_file()
		for i in q:
			lb.insert(lb.size(), i)
		lb.select_set(0)
		lb.event_generate("<<ListboxSelect>>")
		self.retrieve_card(q, a, qb, ab, lb)
		return q,a
	
	def save_notecard(self, qb, ab, ql, al, course):
		"""
		Used for saving a new/edited card, just calls the
		create_file method from fs_functions, and calls a restart
		here in order to update the main screen.
		"""
		q = qb.get("1.0", tk.END).rstrip()
		a = ab.get("1.0", tk.END).rstrip()
		if q != "" and a != "":
			ql.append(q)
			al.append(a)
		
		self.fs_functions.create_file(ql, al, course)
		self.restart()
	
	def save_prefs(self, frame, sync, download):
		"""
		This method will be used to pass necessary preference settings 
		to the appropriate class and update their class variables to let
		them know which preference the user has selected for their functions
		It will be scaled up from its current iteration as complexity of 
		preferences increases
		"""
		self.db_functions.set_prefs(sync, download)
		self.fs_functions.save_prefs(sync, download)
		#frame can technically be blank or pass, because this function is called
		#either at the beginning of runtime or whenever the user chooses
		if frame != "pass":
			frame.withdraw()