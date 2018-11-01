#Dependencies
import pip
import sys
import platform
from subprocess import STDOUT, check_call
import os

pl3m = '''
	It looks like you are on Linux and using python3,
	I'm just making sure that tkinter is installed as it is
	not by default in python 3.x.
	I'l try to install it but theres a chance you will
	just have to run "apt-get install python3-tk" yourself
	'''

def install(package):
	pip.main(['install', package])
	if sys.version.startswith('3'):
		if platform.system() != 'Windows':
			print(pl3m)
			check_call(['apt-get', 'install', '-y', 'python3-tk'],
	     			stdout=open(os.devnull,'wb'), stderr=STDOUT) 
	
if __name__ == '__main__':
	install('dropbox')
