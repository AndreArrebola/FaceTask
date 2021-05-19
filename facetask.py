# -*- coding: utf-8 -*-
"""
import tkinter 
import cv2

import PIL.Image, PIL.ImageTk
from tkinter import messagebox, Toplevel, filedialog, Checkbutton, IntVar
from datetime import datetime
from tkinter import ttk
from math import sqrt
from sklearn import neighbors
from shutil import copy2, move
from random import seed, randint

import shutil
from os import listdir
from os.path import isdir, join, isfile, splitext
import pickle
from PIL import Image, ImageFont, ImageDraw, ImageEnhance
import face_recognition
from face_recognition import face_locations
from face_recognition.face_recognition_cli import image_files_in_folder
import sqlite3"""

import facetask_func as func
import facetask_rec as frec
import facetask_db as dbm
import facetask_ui as ui
import os

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
PATH = os.getcwd()
         
if __name__ == "__main__":
    func.limpa_temp(PATH)
    dbm.carregarBanco()
        
    menu = ui.facerecMenu_tk(None) 
    menu.mainloop()               
    
