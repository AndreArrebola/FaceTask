# -*- coding: utf-8 -*-

import facetask_func as func
import facetask_rec as frec
import facetask_db as dbm
import facetask_ui as ui
import os

PATH = os.getcwd()
         
if __name__ == "__main__":
    func.limpa_temp(PATH)
    dbm.carregarBanco()
        
    menu = ui.facerecMenu_tk(None) 
    menu.mainloop()               
    
