import os
from os import listdir
from os.path import isdir, join, isfile, splitext
import tkinter 



def central(win, larg, alt):
    """Centraliza a janela"""    
    width = larg
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = alt
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    
def limpa_temp(PATH):
    files = os.listdir(PATH + '/temp_dir')
    for f in files:
        os.remove(PATH + '/temp_dir/'+f)
        
def conta_temp(PATH):
    DIR = PATH + '/temp_dir'
    list = os.listdir(DIR) 
    number_files = len(list)
    return number_files  