import platform
import os
import glob
import sys
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

class Funcs:
	def __init__(self, root_folder):
		self.root_folder = root_folder
		if platform.system() != 'Windows':
			self.lib_path = (root_folder + '/lib/')
		else:
			self.lib_path = (root_folder + '\\lib\\')
			
	def set_prefs(self):
		"""
		Updates preferences for the class when such a time should arise
		"""
		pass
		
	def create_dir(self, course_name):
		"""
		Used for creating directories for various functions
		"""
		os.chdir(self.root_folder)
		folder_list = os.getcwd().split()
		if platform.system() != 'Windows':
			fp = os.getcwd() + '/' + course_name
		else:
			fp = os.getcwd() + '\\' + course_name
		if not os.path.exists(fp):
			os.makedirs(fp)
		os.chdir(fp)
		return fp

	def get_questions(self, course):
		"""
		iterates over all files in the selected course folder
		and then pulls the contents, and sorts them into 
		questions and answers lists, then returns them, unless
		the set is empty, then it returns as such.
		"""
		questions = []
		answers = []
		q_from = []
		#Split about /\ of cwd and check if == course name
		if platform.system() != 'Windows':
			if os.getcwd().split('/')[-1] != course:
				os.chdir("./" + course + "/")
		elif os.getcwd().split('\\')[-1] != course:
				os.chdir(".\\" + course + "\\")
		if glob.glob("*.txt") == []:
				questions = [u"Empty"]
				answers = [u"Empty"]
				q_from = [u"N/A"]
				return questions,answers, q_from
		temp_string = ""
		for file in glob.glob("*.txt"):
			with open(file, 'r') as f:
				qa_list = json.load(f)
				for i in qa_list.keys():
					q_from.append(file)
					questions.append(str(i))
				for i in qa_list.values():
					answers.append(str(i))
		return questions, answers, q_from

	def create_file(self, ql, al, course):
		"""
		Used for creating a notecard file from the create 
		or edit notecards dialog windows, converts the lists
		to json, then saves
		"""
		if platform.system() != 'Windows':
			if os.getcwd().split('/')[-1] != course:
				os.chdir("./" + course + "/")
		elif os.getcwd().split('\\')[-1] != course:
				os.chdir(".\\" + course + "\\")
		f = tkFileDialog.asksaveasfile(mode='w', defaultextension=".txt")
		if f is None:
			return
		if ql == []:
			ql = [u'Empty']
		if al == []:
			al = [u'Empty']
		json_out = dict(zip(ql, al))
		json.dump(json_out, f)
		f.close()


	def open_notecard_file(self):
		"""
		Opens up a notecard file and passes back the list
		of questions/answers
		"""
		questions = []
		answers = []
		file_path = tkFileDialog.askopenfilename()
		with open (file_path, 'r') as f:
			qa_list = json.load(f)
			for i in qa_list.keys():
				questions.append(str(i))
			for i in qa_list.values():
				answers.append(str(i))
		return questions, answers

	def save_prefs(self, sync, download):
		"""
		Saves the preferences to the file 'prefs' so that
		they may be retrieved for later use
		"""
		out = {}
		out["sync"] = sync
		out["download"] = download
		with open((self.lib_path+'prefs'), 'w') as f:
			json.dump(out, f)
			
	def retrieve_prefs(self):
		"""
		retrieves preference setting from the prefs file,
		and passes them back to tk_window so that they may
		be then passed to tk_functions to set the preferences
		for all classes
		"""
		with open((self.lib_path+'prefs'), 'r') as f:
			load = json.load(f)
		return (load['download'], load['sync'])