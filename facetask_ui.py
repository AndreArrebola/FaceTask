import tkinter 
import os
import shutil
import sqlite3
import cv2
import PIL.Image, PIL.ImageTk

from tkinter import ttk, messagebox, Toplevel, filedialog, Checkbutton, IntVar
from os import listdir
from os.path import isdir, join, isfile, splitext
from PIL import Image, ImageFont, ImageDraw, ImageEnhance
from shutil import copy2, move

import facetask_func as func
import facetask_rec as frec
import facetask_db as dbm

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
PATH = os.getcwd()


class objetoWebcam:
     def __init__(self, video_source=0):
          # Obtém a Webcam em funcionamento
          self.vid = cv2.VideoCapture(video_source)
          if not self.vid.isOpened():
              raise ValueError("Falha ao abrir webcam:", video_source)
  
          # Obtém altura e largura do vídeo
          self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
          self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
 
     # Libera a Webcam após terminar de ser utilizada
     def __del__(self):
         if self.vid.isOpened():
             self.vid.release()
         
         
     def tirar_foto(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                  # Retorna o frame obtido em RGB
                  return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                  return (ret, None)
        else:
            return (ret, None)
    
    
class facerecWebCam_tk(tkinter.Toplevel):
    argwc=0
    def __init__(self,parent, arg, video_source=0):
        tkinter.Toplevel.__init__(self,parent)
        self.argwc=arg
        self.video_source = video_source
        self.delay = 15
        self.resizable(0,0)
        self.vid = objetoWebcam(video_source)
        self.canvas = tkinter.Canvas(self, width = self.vid.width, height = self.vid.height)
        self.canvas.pack()
        self.parent = parent
        
        self.iconbitmap('facetaskico.ico')
        #self.geometry("500x500")
        func.central(self, int(self.vid.width), int(self.vid.height)+30)
        self.title("Tire uma foto - FaceTask")
        self.btn_foto=tkinter.Button(self, text="Tirar foto", width=50, command=self.salvar_foto, background='#b3d0e3')
        self.btn_foto.pack(anchor=tkinter.CENTER, expand=True)
        

        self.update()
        
        
    def salvar_foto(self):
        ret, frame = self.vid.tirar_foto()
        
        if ret:
            seed(datetime.now())
            rndid=randint(1, 9999)
            cv2.imwrite(PATH + '/temp_dir/' + str(rndid) + '.jpg', cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
            if self.argwc==0:
                frec.show_prediction_labels_on_image(PATH+ '/temp_dir/' + str(rndid) + '.jpg', frec.predict(PATH+ '/temp_dir/' + str(rndid) + '.jpg', PATH + '/model/mod.clf'))
            if self.argwc==2:
                
                tardi = facerecTarefa_tk(None, rndid)
                tardi.focus_force()
                self.withdraw()
                self.wait_window(tardi)
                self.deiconify()
            if self.argwc==3:
                conn = sqlite3.connect('usuarios.db')
                predics = frec.predict(PATH+ '/temp_dir/' + str(rndid) + '.jpg', PATH + '/model/mod.clf')
                try:
                    test = predics[1][0]
                    messagebox.showinfo("Erro", "Mais de uma face foi detectada")
                    conn.close()
                except IndexError:
                    try:
                
                        testadm=dbm.check_ifAdmDB(conn, predics[0][0])
                        if testadm==1:
                            
                            app = facerecApp_tk(None)
        
                            app.configure(background='#b3d0e3')     
                            app.title('Administração e Testes - FaceTask')
                            app.focus_force()
                            self.withdraw()
                            self.wait_window(app)
                            self.deiconify()
                        else:
                            messagebox.showinfo("Erro", "Acesso negado")
                        conn.close()
                    except IndexError:
                        messagebox.showinfo("Erro","Nenhuma face foi detectada")
                        conn.close()
                    except TypeError:
                        messagebox.showinfo("Erro", "Face desconhecida. Por favor, peça a inserção a um administrador")
                        conn.close()
                
            
    def update(self):         
        ret, frame = self.vid.tirar_foto()
 
        if ret:
            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image = self.photo, anchor = tkinter.NW)
        self.after(self.delay, self.update)  
        
        
         
    pass     
 

                
class facerecEdiUse_tk(tkinter.Toplevel):
    priima="none"
    checkad=0
    def __init__(self,parent):
        tkinter.Toplevel.__init__(self,parent)
        self.parent = parent
        self.geometry("600x300")
        func.central(self, 600, 300)
        
        self.configure(background='#b3d0e3')
        self.title("Editar um Usuário - FaceTask")
        self.iconbitmap('facetaskico.ico')
        self.resizable(0,0)
        func.limpa_temp(PATH)
        self.initialize()
        self.loadCombo()
        self.selectUser.bind('<<ComboboxSelected>>', self.modified)
    
    def modified(self, event):
        conn = sqlite3.connect('usuarios.db')
        info = dbm.get_UinfoDB(conn, self.selectUser.get())
        self.nomeuser.delete(0, "end")
        self.nomeuser.insert(0, info[1])
        self.tarseg.delete(0, "end")
        self.tarseg.insert(0, info[2])
        self.tarter.delete(0, "end")
        self.tarter.insert(0, info[3])
        self.tarqua.delete(0, "end")
        self.tarqua.insert(0, info[4])
        self.tarqui.delete(0, "end")
        self.tarqui.insert(0, info[5])
        self.tarsex.delete(0, "end")
        self.tarsex.insert(0, info[6])
        self.checkad.set(info[7])
        
        
    def initialize(self):    
        self.grid()
        
        self.lblDig= tkinter.Label(self, text="Nome de usuário", background='#b3d0e3', font="-size 10 -weight bold")
        self.lblSta= tkinter.Label(self, text="Editar ou excluir um usuário", background='#b3d0e3', font=("Arial",12, 'bold'))
        self.btnAddU=tkinter.Button(self,text=u"Salvar Usuário", command=self.OnButtonSalUClick)
        self.btnDelU=tkinter.Button(self,text=u"Excluir Usuário", command=self.OnButtonDelUClick, background='#f7746a')

        self.nomeuser = tkinter.Entry(self)
        self.tarseg = tkinter.Entry(self)
        self.tarter = tkinter.Entry(self)
        self.tarqua = tkinter.Entry(self)
        self.tarqui = tkinter.Entry(self)
        self.tarsex = tkinter.Entry(self)
        self.lblSeg= tkinter.Label(self, text="Segunda", background='#b3d0e3', font="-size 10 -weight bold")
        self.lblTer= tkinter.Label(self, text="Terça", background='#b3d0e3', font="-size 10 -weight bold")
        self.lblQua= tkinter.Label(self, text="Quarta", background='#b3d0e3', font="-size 10 -weight bold")
        self.lblQui= tkinter.Label(self, text="Quinta", background='#b3d0e3', font="-size 10 -weight bold")
        self.lblSex= tkinter.Label(self, text="Sexta", background='#b3d0e3', font="-size 10 -weight bold")
        self.checkad= IntVar()
        self.checkAdm = Checkbutton(self, text="Administrador", variable=self.checkad, background='#b3d0e3', font="-size 10 -weight bold")
        
        self.lblDig.place(x=62, y=95)
        self.lblSta.place(x=190,y=10)
        self.btnAddU.place(x=315, y=250)
        self.btnDelU.place(x=190, y=250)
        self.nomeuser.place(x=62, y=115)
        self.tarseg.place(x=415, y=55)
        self.tarter.place(x=415, y=95)
        self.tarqua.place(x=415, y=135)
        self.tarqui.place(x=415, y=175)
        self.tarsex.place(x=415, y=215)
        self.lblSeg.place(x=330, y=53)
        self.lblTer.place(x=330, y=93)
        self.lblQua.place(x=330, y=133)
        self.lblQui.place(x=330, y=173)
        self.lblSex.place(x=330, y=213)
        self.checkAdm.place(x=60, y=160)
        
            
        
        
        
        pass     
    def loadCombo(self):
        box_value=tkinter.StringVar()
        self.selectUser = ttk.Combobox(self, values=[], textvariable=box_value, state='readonly')
        self.selectUser.place(x=60, y=55)
        
        
        conn = sqlite3.connect('usuarios.db')
        cursor = conn.cursor()

        cursor.execute("""
                   SELECT nome FROM usuarios;
                   """)

        for linha in cursor.fetchall():
            if str(linha) not in self.selectUser['values']:
                self.selectUser['values'] = (*self.selectUser['values'], linha)
        self.selectUser.current(0)
        conn.close()
        
        
        #copy2(pathadd, PATH + '/train_dir/' + self.selectUser.get())
    def OnButtonSalUClick(self):
        
        if self.nomeuser.get()=="":
            messagebox.showinfo("Notificação", "Um nome é necessário para o usuário.")
        else:
            
            conn = sqlite3.connect('usuarios.db')
            dbm.upd_UinfoDB(conn, self.selectUser.get(), self.nomeuser.get(), self.tarseg.get(), self.tarter.get(), self.tarqua.get(), self.tarqui.get(), self.tarsex.get(), self.checkad.get())
            conn.close()
            
            messagebox.showinfo("Notificação", "Usuário atualizado com sucesso.")
            
            self.destroy()
    
    def OnButtonDelUClick(self):
        
        if self.selectUser.get()=="":
            messagebox.showinfo("Notificação", "Selecione um usuário para excluir.")
        else:
            escolha = messagebox.askquestion('Atenção', 'Tem certeza que deseja excluir este usuário? Esta ação não pode ser desfeita.')
            if escolha == 'yes':
                conn = sqlite3.connect('usuarios.db')
                id = dbm.get_idDB(conn, self.selectUser.get())
                shutil.rmtree(PATH + "/train_dir/" + str(id))
                dbm.del_UserDB(conn, self.selectUser.get())
                conn.close()
            
                messagebox.showinfo("Notificação", "Usuário excluído com sucesso. Treine o classificador para evitar conflitos.")
            
                self.destroy()
            
    
class facerecAddUse_tk(tkinter.Toplevel):
    priima="none"
    checkad=0
    def __init__(self,parent):
        tkinter.Toplevel.__init__(self,parent)
        self.parent = parent
        #self.geometry("600x300")
        func.central(self, 600, 300)
        self.configure(background='#b3d0e3')
        self.title("Adicionar um Usuário - FaceTask")
        self.iconbitmap('facetaskico.ico')
        self.resizable(0,0)
        func.limpa_temp(PATH)
        self.initialize()
    
    def initialize(self):    
        self.grid()
        
        self.lblDig= tkinter.Label(self, text="Nome de usuário", background='#b3d0e3', font="-size 10 -weight bold")
        self.lblSta= tkinter.Label(self, text="Adicionar um usuário", background='#b3d0e3', font=("Arial",12, 'bold'))
        self.btnAddIma = tkinter.Button(self,text=u"Carregar Imagem", command=self.OnButtonAICarImaClick)
        self.btnAddU=tkinter.Button(self,text=u"Adicionar Usuário", command=self.OnButtonAddUClick)
        self.nomeuser = tkinter.Entry(self)
        self.tarseg = tkinter.Entry(self)
        self.tarter = tkinter.Entry(self)
        self.tarqua = tkinter.Entry(self)
        self.tarqui = tkinter.Entry(self)
        self.tarsex = tkinter.Entry(self)
        self.lblSeg= tkinter.Label(self, text="Segunda", background='#b3d0e3', font="-size 10 -weight bold")
        self.lblTer= tkinter.Label(self, text="Terça", background='#b3d0e3', font="-size 10 -weight bold")
        self.lblQua= tkinter.Label(self, text="Quarta", background='#b3d0e3', font="-size 10 -weight bold")
        self.lblQui= tkinter.Label(self, text="Quinta", background='#b3d0e3', font="-size 10 -weight bold")
        self.lblSex= tkinter.Label(self, text="Sexta", background='#b3d0e3', font="-size 10 -weight bold")
        self.checkad= IntVar()
        self.checkAdm = Checkbutton(self, text="Administrador", variable=self.checkad, background='#b3d0e3', font="-size 10 -weight bold")

        self.lblDig.place(x=65, y=80)
        self.lblSta.place(x=215,y=10)
        self.btnAddIma.place(x=65,y=170)
        self.btnAddU.place(x=250, y=250)
        self.nomeuser.place(x=65, y=100)
        self.tarseg.place(x=410, y=55)
        self.tarter.place(x=410, y=95)
        self.tarqua.place(x=410, y=135)
        self.tarqui.place(x=410, y=175)
        self.tarsex.place(x=410, y=215)
        self.lblSeg.place(x=330, y=55)
        self.lblTer.place(x=330, y=95)
        self.lblQua.place(x=330, y=135)
        self.lblQui.place(x=330, y=175)
        self.lblSex.place(x=330, y=215)
        self.checkAdm.place(x=60, y=135)
        
        
        
        pass     
    def OnButtonAICarImaClick(self):
        ei = facerecEscIma_tk(None)
        
        #pathadd =  filedialog.askopenfilename(initialdir = PATH + '/',title = "Escolha uma imagem",filetypes = (("Arquivos JPG","*.jpg"),("Arquivos PNG","*.png"),("all files","*.*")))
        ei.focus_force()
        self.withdraw()
        self.wait_window(ei)
        self.deiconify()
        self.priima = 'ok'
        
        #copy2(pathadd, PATH + '/train_dir/' + self.selectUser.get())
    def OnButtonAddUClick(self):
        if self.nomeuser.get()=="":
            messagebox.showinfo("Notificação", "Por favor, digite seu nome.")
        elif func.conta_temp(PATH)==0:
            messagebox.showinfo("Notificação", "Por favor, escolha sua primeira imagem.")
        else:
            seed(datetime.now())
            rndid=randint(1, 9999)
            if not os.path.exists(PATH + '/train_dir/' + str(rndid)):
                try:
                    dbm.inserirUserDB(rndid, self.nomeuser.get(), self.tarseg.get(), self.tarter.get(), self.tarqua.get(), self.tarqui.get(), self.tarsex.get(), self.checkad.get())
                    os.makedirs(PATH + '/train_dir/' + str(rndid))
                 
                    files = os.listdir(PATH + '/temp_dir')
                    for f in files:
                        move(PATH + '/temp_dir/'+f, PATH + '/train_dir/' + str(rndid))
                        messagebox.showinfo("Notificação", "Usuário adicionado! Não se esqueça de treinar o classificador.")
                    self.destroy()
                except sqlite3.IntegrityError:
                    messagebox.showinfo("Notificação", "Esse usuário já existe!")
            else:
                messagebox.showinfo("Notificação", "Esse usuário já existe!")
                
class facerecEscIma_tk(tkinter.Toplevel):
    pathadd=''
    def __init__(self,parent):
        tkinter.Toplevel.__init__(self,parent)
        #self.geometry("300x150")
        func.central(self, 300, 150)
        self.parent = parent
        self.resizable(0,0)
        self.configure(background='#b3d0e3')
        self.title("Escolher Imagem - FaceTask")
        self.iconbitmap('facetaskico.ico')
        self.initialize()
    def on_closing(self):
        func.limpa_temp(PATH)
        self.destroy()
        
    def initialize(self):    
        self.grid()
        self.lblDig= tkinter.Label(self, text="Escolha como adicionar sua imagem", background='#b3d0e3', font=("Arial",12, 'bold'))

        self.lblCon= tkinter.Label(self, text="Imagens pendentes: " + str(func.conta_temp(PATH)), background='#b3d0e3', font="-size 10 -weight bold")
        self.btnAddIma = tkinter.Button(self,text=u"Escolher\n Arquivo", command=self.OnButtonAICarImaClick)
        self.btnAddWC = tkinter.Button(self,text=u"Utilizar\n Webcam", command=self.OnButtonAICarWebClick)
        self.btnSalvar = tkinter.Button(self,text=u"Salvar", command=self.OnButtonSalvarClick)
        self.protocol("WM_DELETE_WINDOW", self.on_closing) 
        self.btnAddIma.place(x=55,y=70)
        self.btnAddWC.place(x=185,y=70)
        
        
        self.lblDig.place(x=7, y=20)
        self.lblCon.place(x=80, y=45)
        self.btnSalvar.place(x=130, y=115)
        
        pass 
    

       
    def OnButtonAICarImaClick(self):
        copy2(filedialog.askopenfilename(initialdir = PATH + '/',title = "Escolha uma imagem",filetypes = (("Arquivos JPG","*.jpg"),("Arquivos PNG","*.png"),("all files","*.*"))), PATH + '/temp_dir')
        self.lblCon.config(text="Imagens pendentes: " + str(func.conta_temp(PATH)))
        
    def OnButtonSalvarClick(self):
        self.destroy()

        
    def OnButtonAICarWebClick(self):
        wc = facerecWebCam_tk(self, 1)
        self.wait_window(wc)
        self.lblCon.config(text="Imagens pendentes: " + str(func.conta_temp(PATH)))
        #self.pathadd =  PATH+ "/temp.jpg"
        
        #messagebox.showinfo("Notificação", self.selectUser.get())

class facerecTarefa_tk(tkinter.Toplevel):
    nomet=''
    tarefat=''
    idmigt=''
    
    def __init__(self,parent, idimg):
        tkinter.Toplevel.__init__(self,parent)
        self.parent = parent
        
        self.idmigt=idimg
        #self.geometry("500x300")
        func.central(self, 700, 300)
        self.resizable(0,0)
        self.configure(background='#b3d0e3')
        self.title("Tarefa do Dia - FaceTask")
        self.iconbitmap('facetaskico.ico')
        self.initialize()
    
    def initialize(self):    
        self.grid()
        conn = sqlite3.connect('usuarios.db')
        predics = frec.predict(PATH+ '/temp_dir/' + str(self.idmigt) + '.jpg', PATH + '/model/mod.clf')
        try:
            test = predics[1][0]
            self.lblDig= tkinter.Label(self, text="Um erro ocorreu", background='#b3d0e3')
            self.lblSta= tkinter.Label(self, text="Mais de uma face foi detectada", background='#b3d0e3')
            self.lblSta.place(x=130,y=80)
            self.lblDig.place(x=70, y=20)
            self.lblDig.config(font=("Arial", 25))
            self.lblSta.config(font=("Arial", 20))
            conn.close()
        except IndexError:
            try:
                
                self.nomet=dbm.get_nameDB(conn, predics[0][0])
                self.tarefat=dbm.get_tarDB(conn, predics[0][0])
                self.lblDig= tkinter.Label(self, text="Bem vindo, " + self.nomet + "!", background='#b3d0e3')
                self.lblSta= tkinter.Label(self, text="Sua tarefa de hoje é: " + self.tarefat, background='#b3d0e3')
                self.lblSta.place(x=30,y=150)
                self.lblDig.place(x=30, y=90)
                self.lblDig.config(font=("Arial", 25, 'bold'))
                self.lblSta.config(font=("Arial", 20))
                conn.close()
            except IndexError:
                self.lblDig= tkinter.Label(self, text="Um erro ocorreu", background='#b3d0e3')
                self.lblSta= tkinter.Label(self, text="Nenhuma face foi detectada", background='#b3d0e3')
                self.lblSta.place(x=30,y=150)
                self.lblDig.place(x=30, y=90)
                self.lblDig.config(font=("Arial", 25, 'bold'))
                self.lblSta.config(font=("Arial", 20))
                conn.close()
            except TypeError:
                self.lblDig= tkinter.Label(self, text="Um erro ocorreu")
                self.lblSta= tkinter.Label(self, text="Face desconhecida.\nSolicitar cadastro no sistema.")
                self.lblSta.place(x=30,y=150)
                self.lblDig.place(x=30, y=90)
                self.lblDig.config(font=("Arial", 25, 'bold'))
                self.lblSta.config(font=("Arial", 20))
                conn.close()
        pass     

class facerecAddima_tk(tkinter.Toplevel):
    
    def __init__(self,parent):
        tkinter.Toplevel.__init__(self,parent)
        self.parent = parent
        self.resizable(0,0)
        #self.geometry("350x150")
        func.central(self, 350, 150)
        self.initialize()
        self.configure(background='#b3d0e3')
        self.title("Adicionar Imagem - FaceTask")
        self.iconbitmap('facetaskico.ico')
    
    def initialize(self):    
        self.grid()
        self.lblDig= tkinter.Label(self, text="Adicionar imagem ao sistema", background='#b3d0e3', font=("Arial",12, 'bold'))

        self.btnAddIma = tkinter.Button(self,text=u"Carregar Imagem", command=self.OnButtonAICarImaClick)
        self.btnAddIma.place(x=120,y=110)

        self.lblSta= tkinter.Label(self, text="Escolha um usuário existente:" , background='#b3d0e3', font="-size 10 -weight bold")
        self.lblDig.place(x=60,y=20)
        self.lblSta.place(x=80, y=50)
        
       
        box_value=tkinter.StringVar()
        self.selectUser = ttk.Combobox(self, values=[], textvariable=box_value, state='readonly')
        self.selectUser.place(x=100, y=80)
        
        
        
        conn = sqlite3.connect('usuarios.db')
        cursor = conn.cursor()

        cursor.execute("""
                   SELECT nome FROM usuarios;
                   """)

        for linha in cursor.fetchall():
            if str(linha) not in self.selectUser['values']:
                self.selectUser['values'] = (*self.selectUser['values'], linha)
        self.selectUser.current(0)
        conn.close()
        
        
        pass     
    def OnButtonAICarImaClick(self):
        ei = facerecEscIma_tk(None)
        
        #pathadd =  filedialog.askopenfilename(initialdir = PATH + '/',title = "Escolha uma imagem",filetypes = (("Arquivos JPG","*.jpg"),("Arquivos PNG","*.png"),("all files","*.*")))
        ei.focus_force()
        self.withdraw()
        self.wait_window(ei)
        self.deiconify()
        if func.conta_temp(PATH)>0:
            pathadd = ei.pathadd
            conn = sqlite3.connect('usuarios.db')
            id = dbm.get_idDB(conn, self.selectUser.get())
        
            conn.close()
            files = os.listdir(PATH + '/temp_dir')
            for f in files:
                move(PATH + '/temp_dir/'+f, PATH + '/train_dir/' + str(id))
            messagebox.showinfo("Notificação", "Imagem adicionada! Para que ela seja utilizada pelo sistema, treinar o classificador.")

class facerecMenu_tk(tkinter.Tk):
    action=0
    def __init__(self,parent):
        tkinter.Tk.__init__(self,parent)
        
        #self.geometry("420x300")
        func.central(self, 420, 300)
        self.configure(background='#b3d0e3')
        self.title("Menu Principal - FaceTask")
        self.iconbitmap('facetaskico.ico')
        self.resizable(0,0)
        self.parent = parent
        self.initialize()
        
    def initialize(self):    
        self.grid()
        
        #iconetask = iconet.resize((25,25), Image.ANTIALIAS)
        self.btnLogar = tkinter.Button(self,text=u"Tarefa \ndo Dia", command=self.OnButtonCarTarClick, height = 3, width = 18, font=("Arial",12, 'bold'))
        self.btnLogar.place(x=117,y=165)
        self.btnLogAdm = tkinter.Button(self,text=u"Administração e Testes", command=self.OnButtonCarAdmClick, height = 2, width = 20, font=("Arial",11, 'bold'))
        self.btnLogAdm.place(x=117, y=240)
        imgload = Image.open("facetask.png")
        render = PIL.ImageTk.PhotoImage(imgload, master=self)
        self.logo = tkinter.Label(self, image=render)
        self.logo.image = render
        self.logo.place(x=0, y=0)
        self.logo.configure(background='#b3d0e3')
        self.focus_force()
        
        pass      
    def OnButtonCarTarClick(self):

        webtar = facerecWebCam_tk(None, 2)
        webtar.focus_force()
        self.withdraw()
        self.wait_window(webtar)
        self.deiconify()
        pass
    def OnButtonCarAdmClick(self):
        conn = sqlite3.connect('usuarios.db')
        if dbm.check_allAdmDB(conn)==1 or dbm.check_noAdmDB(conn)==1:
            app = facerecApp_tk(None)
        
            app.configure(background='#b3d0e3')     
            app.title('Administração e Testes - FaceTask')
            app.focus_force()
            self.withdraw()
            self.wait_window(app)
            self.deiconify()
        else:
            wc = facerecWebCam_tk(self, 3)
            wc.focus_force()
            self.withdraw()
            self.wait_window(wc)
            self.deiconify()
        pass

class facerecApp_tk(tkinter.Toplevel):
    action=0
    def __init__(self,parent):
        tkinter.Toplevel.__init__(self,parent)
        
        self.parent = parent
        self.resizable(0,0)
        #self.geometry("400x230")
        func.central(self, 400, 230)
        self.initialize()
        
        self.iconbitmap('facetaskico.ico')
         
    def changestatus(self):
        self.lblSta.config(text='Status: Trabalhando')
        
    def initialize(self):    
        self.grid()
        
        self.lblDig= tkinter.Label(self, text="Gerenciar Usuários", background='#b3d0e3')
        self.lblDig.config(font=("Arial",12, 'bold'))
        self.lblTes= tkinter.Label(self, text="Testar e Treinar", background='#b3d0e3')
        self.lblTes.config(font=("Arial",12, 'bold'))
        self.lblSta= tkinter.Label(self, text="Status: Ocioso", width=57)
        self.lblSta.place(x=0, y=209)
        self.lblDig.place(x=125,y=10)
        self.lblTes.place(x=135,y=110)
        self.btnAddIma = tkinter.Button(self,text=u"Adicionar \nImagem", command=self.OnButtonAddImaClick, width=8, height=3)

        self.btnTreRe = tkinter.Button(self,text=u"Treinar", command=self.OnButtonTreinarClick, width=8, height=3)
        self.btnTestaIma = tkinter.Button(self,text=u"Testar \nWebcam", command=self.OnButtonImaTesteClick, width=8, height=3)
        self.btnCarIma = tkinter.Button(self,text=u"Testar \nImagem", command=self.OnButtonCarImaClick, width=8, height=3)
        self.btnAddUse = tkinter.Button(self,text=u"Adicionar \nUsuário", command=self.OnButtonAddUseClick, width=8, height=3)
        self.btnEdiUse = tkinter.Button(self,text=u"Editar \nUsuário", command=self.OnButtonEdiUseClick, width=8, height=3)

        self.btnAddUse.place(x=85, y=40)
        self.btnTestaIma.place(x=165, y=140)
        self.btnTreRe.place(x=245, y=140)
        
        self.btnCarIma.place(x=85, y=140)
        self.btnAddIma.place(x=165,y=40)
        self.btnEdiUse.place(x=245, y=40)
        #test = facerecTarefa_tk(self, '', '')
       
        #criamos o objeto botão
        pass        
    def OnButtonCarImaClick(self):
        
        pathima =  filedialog.askopenfilename(initialdir = PATH + '/',title = "Escolha uma imagem",filetypes = (("Arquivos JPG","*.jpg"),("Arquivos PNG","*.png"),("all files","*.*")))
        self.changestatus()
        self.update_idletasks()
        frec.show_prediction_labels_on_image(pathima, frec.predict(pathima, PATH + '/model/mod.clf'))
        self.lblSta.config(text='Status: Ocioso')
        
    def OnButtonAddUseClick(self):
        
        addu = facerecAddUse_tk(None)
        addu.focus_force()
        self.withdraw()
        self.wait_window(addu)
        self.deiconify()
        
    def OnButtonEdiUseClick(self):
        
        ediu = facerecEdiUse_tk(None)
        ediu.focus_force()
        self.withdraw()
        self.wait_window(ediu)
        self.deiconify()
        
        

    def OnButtonTreinarClick(self):     
        self.changestatus()
        self.update_idletasks()
        train(PATH +'/train_dir/', PATH + '/model/mod.clf')
        self.lblSta.config(text='Status: Ocioso')
    def OnButtonImaTesteClick(self):     
        """self.changestatus()
        self.update_idletasks()
        frec.show_prediction_labels_on_image(PATH + '/test_image2.jpg', frec.predict(PATH + '/test_image2.jpg', PATH + '/model/mod.clf'))
        self.lblSta.config(text='Status: Ocioso')"""
        wc = facerecWebCam_tk(self, 0)
        wc.focus_force()
        self.withdraw()
        self.wait_window(wc)
        self.deiconify()
        
        
    def OnButtonAddImaClick(self):
        top = facerecAddima_tk(None)
        
        
        
        top.focus_force()
        self.withdraw()
        self.wait_window(top)
        self.deiconify()

