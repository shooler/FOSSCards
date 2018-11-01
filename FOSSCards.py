import lib.tk_functions as tk_functions
import lib.tk_windows as tk_windows
import sys
if sys.version.startswith('2'):
	pyver = 2
	import Tkinter as tk
	import tkFileDialog	
else:
	import tkinter as tk
	from tkinter import filedialog
	tkFileDialog = filedialog
root = tk.Tk()
root.geometry("1250x450+450+450")
	
def main():
	tk_windows.spawnWindows(root)
	root.mainloop()
if __name__ == '__main__':
    main()
