import os
import glob
import tk_functions
import fs_functions
import sys
import platform
import errno
import filecmp
from shutil import copyfile

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
	def  __init__(self, dbx, fs_functions,db_root,fs_root):
		self.dbx = dbx
		self.db_root = db_root
		self.fs_functions = fs_functions
		self.fs_root = fs_root
	
	def set_prefs(self, sync, download):
		"""
		updates preferences for the class
		"""
		self.sync_o = sync
		self.download_o = download
		
	def sync(self, transferData, course_folder):
		"""
		Syncs up all files in the courses folder to dropbox in said course folder
		local to Dropbox
		"""
		dblist = []
		dblist_o = []
		if platform.system() != 'Windows':
			os.chdir(str(self.fs_root + '/' + course_folder + '/'))
		else:
			os.chdir(str(self.fs_root + '\\' + course_folder + '\\'))
		#the follow gets files from dbx, and then pares down the metadata
		for entry in self.dbx.files_list_folder(self.db_root + course_folder).entries:
			dblist.append(str(entry).split(',')[0].split("\'"))
		for entry in dblist:
			dblist_o.append(entry[1])
		#option 0 is when sync doesn't ask, and just overwrites any discrepancies
		if self.sync_o == 0:
			for file in glob.glob("*.txt"):
				if file not in dblist_o:
					transferData.upload_file(file, self.db_root+course_folder+file)
				else:
					#I havent figured out how to overwrite in place yet, so it just
					#deletes and remakes the file to sync it in this option
					self.dbx.files_delete(self.db_root+course_folder+file)
					transferData.upload_file(file, self.db_root+course_folder+file)
		elif self.sync_o == 1:
			for file in glob.glob("*.txt"):
				if file not in dblist_o:
					transferData.upload_file(file, self.db_root+course_folder+file)
				else:
					tfile = file+'.test'
					self.dbx.files_download_to_file((tfile),
						(self.db_root+course_folder+file))
					if filecmp.cmp(file, tfile):
						os.remove(tfile)
						continue
					else:
						os.remove(tfile)
						result = messagebox.askquestion("Delete", (file 
							+"\'s contents have changed locally,"
							+" overwrite in DropBox?"), icon='warning')
						
						if result == 'yes':
							self.dbx.files_delete(self.db_root+course_folder+file)
							transferData.upload_file(file, 
								self.db_root+course_folder+file)

	def upload(self, file_path, transferData, course_folder, cwd):
		"""
		Gets the filepath of what you want to upload, makes sure it is a text file,
		then uploads it to the current course folder.
		"""
		fp_check = file_path.split('/')[-1].split('.')[-1]
		fp_to = (self.db_root + course_folder + file_path.split('/')[-1])
		if fp_check != 'txt':
			messagebox.showerror("Error, Please upload txt file")
			pass
		else:
			transferData.upload_file(file_path, fp_to)

	def add_new_course(self, course_name):
		"""
		Creates an empty directory at root of the DB
		"""
		self.dbx.files_create_folder(self.db_root + course_name)


	def download(self, course_folder_path):
		"""
		Downloads the files from the current course folder in DB
		to the course folder on the local machine
		"""
		if self.db_root == '':
			self.db_root = '/'
		cfp = self.db_root+course_folder_path
		#Should I not just remake it? Would it matter? I dont know
		if not os.path.isdir(course_folder_path):
			fp = self.fs_functions.create_dir(course_folder_path)
		else:
			if platform.system() != 'Windows':
				fp = (self.fs_root + '/' + course_folder_path)
			else:
				fp = (self.fs_root + '\\' + course_folder_path)
		os.chdir(fp)
		if self.download_o == 0:
			for entry in self.dbx.files_list_folder(cfp).entries:
				if not entry:
					return
				course_file_path = cfp + entry.name
				self.dbx.files_download_to_file(entry.name, course_file_path)
		else:
			for entry in self.dbx.files_list_folder(cfp).entries:
				if not entry:
					return
				course_file_path = cfp + entry.name
				if os.path.exists(entry.name):
					tfile = entry.name+'.test'
					self.dbx.files_download_to_file(tfile,course_file_path)
					if filecmp.cmp(entry.name, tfile):
						os.remove(tfile)
						continue
					else:
						os.remove(tfile)
						result = messagebox.askquestion("Delete", (entry.name 
							+"\'s contents have changed in Dropbox,"
							+" overwrite on local system?"),
								icon='warning')
						if result == 'yes':
							self.dbx.files_download_to_file(entry.name,
								course_file_path)
				else:
					self.dbx.files_download_to_file(entry.name,course_file_path)
					

	def get_all_folders(self):
		"""
		Returns all folders in the root directory of DB
		"""
		folder_list = []
		for entry in self.dbx.files_list_folder(self.db_root).entries:
			folder_list.append(entry.name)
		return folder_list