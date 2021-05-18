# -*- coding: utf-8 -*-

import tkinter 
import cv2

import PIL.Image, PIL.ImageTk
from tkinter import messagebox
from tkinter import Toplevel
from tkinter import filedialog, Checkbutton, IntVar
from datetime import datetime
from tkinter import ttk
from math import sqrt
from sklearn import neighbors
from shutil import copy2, move
from random import seed
from random import randint
import os
import shutil
from os import listdir
from os.path import isdir, join, isfile, splitext
import pickle
from PIL import Image, ImageFont, ImageDraw, ImageEnhance
import face_recognition
from face_recognition import face_locations
from face_recognition.face_recognition_cli import image_files_in_folder
import sqlite3

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
PATH = os.getcwd()

"""
  __  __          _                 _                       _                                                 _                     _                              _           
 |  \/  |   ___  | |_    ___     __| |   ___    ___      __| |   ___     _ __    ___    ___    ___    _ __   | |__     ___    ___  (_)  _ __ ___     ___   _ __   | |_    ___  
 | |\/| |  / _ \ | __|  / _ \   / _` |  / _ \  / __|    / _` |  / _ \   | '__|  / _ \  / __|  / _ \  | '_ \  | '_ \   / _ \  / __| | | | '_ ` _ \   / _ \ | '_ \  | __|  / _ \ 
 | |  | | |  __/ | |_  | (_) | | (_| | | (_) | \__ \   | (_| | |  __/   | |    |  __/ | (__  | (_) | | | | | | | | | |  __/ | (__  | | | | | | | | |  __/ | | | | | |_  | (_) |
 |_|  |_|  \___|  \__|  \___/   \__,_|  \___/  |___/    \__,_|  \___|   |_|     \___|  \___|  \___/  |_| |_| |_| |_|  \___|  \___| |_| |_| |_| |_|  \___| |_| |_|  \__|  \___/ 
"""  
                                                                                                                                                                             
def train(train_dir, model_save_path, n_neighbors=None, knn_algo='ball_tree', verbose=False):
    
    """Treina o classificador KNN(k-nearest neighbors) para reconhecimento facial"""
    
    X = []
    y = []
    for class_dir in listdir(train_dir):
        if not isdir(join(train_dir, class_dir)):
            continue
        for img_path in image_files_in_folder(join(train_dir, class_dir)):
            image = face_recognition.load_image_file(img_path)
            faces_bboxes = face_locations(image)
            if len(faces_bboxes) != 1:
                if verbose:
                    print("image {} not fit for training: {}".format(img_path, "didn't find a face" if len(faces_bboxes) < 1 else "found more than one face"))
                continue
            X.append(face_recognition.face_encodings(image, known_face_locations=faces_bboxes)[0])
            y.append(class_dir)


    if n_neighbors is None:
        n_neighbors = int(round(sqrt(len(X))))
        if verbose:
            print("Chose n_neighbors automatically as:", n_neighbors)

    knn_clf = neighbors.KNeighborsClassifier(n_neighbors=n_neighbors, algorithm=knn_algo, weights='distance')
    knn_clf.fit(X, y)

    if model_save_path != "":
        with open(model_save_path, 'wb') as f:
            pickle.dump(knn_clf, f)
    messagebox.showinfo("Notificação", "Classificador treinado!")
    return knn_clf
    
def predict(X_img_path,  model_path, knn_clf=None, distance_threshold=0.5):
    """
    Utilizando o classificador já treinado, analiza as imagens e tenta reconhecer os rostos
    Retorna lista de nomes e as coordenadas do rosto
    """

    if not os.path.isfile(X_img_path) or os.path.splitext(X_img_path)[1][1:] not in ALLOWED_EXTENSIONS:
        raise Exception("Invalid image path: {}".format(X_img_path))

    if knn_clf is None and model_path is None:
        raise Exception("Must supply knn classifier either thourgh knn_clf or model_path")

    # Load a trained KNN model (if one was passed in)
    if knn_clf is None:
        with open(model_path, 'rb') as f:
            knn_clf = pickle.load(f)

    # Load image file and find face locations
    X_img = face_recognition.load_image_file(X_img_path)
    X_face_locations = face_recognition.face_locations(X_img)

    # If no faces are found in the image, return an empty result.
    if len(X_face_locations) == 0:
        return []

    # Find encodings for faces in the test iamge
    faces_encodings = face_recognition.face_encodings(X_img, known_face_locations=X_face_locations)

    # Use the KNN model to find the best matches for the test face
    closest_distances = knn_clf.kneighbors(faces_encodings, n_neighbors=1)
    are_matches = [closest_distances[0][i][0] <= distance_threshold for i in range(len(X_face_locations))]

    # Predict classes and remove classifications that aren't within the threshold
    return [(pred, loc) if rec else ("unknown", loc) for pred, loc, rec in zip(knn_clf.predict(faces_encodings), X_face_locations, are_matches)]

def show_prediction_labels_on_image(img_path, predictions):
    """
    Exibe uma imagem marcando o rosto reconhecido. Recebe o caminho onde a imagem deve ficar e os dados de previsão.
    """
    pil_image = Image.open(img_path).convert("RGB")
    draw = ImageDraw.Draw(pil_image)
    conn = sqlite3.connect('usuarios.db')

    for name, (top, right, bottom, left) in predictions:
        # Draw a box around the face using the Pillow module
        draw.rectangle(((left, top), (right, bottom)), outline=(0, 0, 255))

        # There's a bug in Pillow where it blows up with non-UTF-8 text
        # when using the default bitmap font
        
        name = get_nameDB(conn, name)
        name = name.encode("UTF-8")

        # Draw a label with a name below the face
        text_width, text_height = draw.textsize(name)
        draw.rectangle(((left, bottom - text_height - 10), (right, bottom)), fill=(0, 0, 255), outline=(0, 0, 255))
        draw.text((left + 6, bottom - text_height - 5), name, fill=(255, 255, 255, 255))

    # Remove the drawing library from memory as per the Pillow docs
    del draw
    conn.close()
    # Display the resulting image
    pil_image.show()

"""
  ____                                         _            ____                _               
 | __ )    __ _   _ __     ___    ___       __| |   ___    |  _ \    __ _    __| |   ___    ___ 
 |  _ \   / _` | | '_ \   / __|  / _ \     / _` |  / _ \   | | | |  / _` |  / _` |  / _ \  / __|
 | |_) | | (_| | | | | | | (__  | (_) |   | (_| | |  __/   | |_| | | (_| | | (_| | | (_) | \__ \
 |____/   \__,_| |_| |_|  \___|  \___/     \__,_|  \___|   |____/   \__,_|  \__,_|  \___/  |___/
                                                                                                
"""

def check_allAdmDB(conexao):
    cursor = conexao.cursor()

    cursor.execute('SELECT nome FROM usuarios WHERE admin=0;')
    dados = cursor.fetchall()
    
    if len(dados)==0:
        return 1
    else:
        return 0
    
def check_noAdmDB(conexao):
    cursor = conexao.cursor()

    cursor.execute('SELECT nome FROM usuarios WHERE admin=1;')
    dados = cursor.fetchall()
    
    if len(dados)==0:
        return 1
    else:
        return 0
        
def check_ifAdmDB(conexao, codid):
    cursor = conexao.cursor()
    isadm=0
    cursor.execute('SELECT admin FROM usuarios WHERE id=?;', (codid,))
    lista = cursor.fetchall()
    for row in lista:
        isadm=row[0]
    
    cursor.close()
    return isadm
    
def get_nameDB(conexao, codid):
    nome="undefined"
    cursor = conexao.cursor()


    cursor.execute('SELECT nome FROM usuarios WHERE id=?;', (codid,))
    lista = cursor.fetchall()
    for row in lista:
        nome=row[0]
    
    cursor.close()
    return nome

def get_idDB(conexao, codname):
    id=0
    cursor = conexao.cursor()


    cursor.execute('SELECT id FROM usuarios WHERE nome=?;', (codname,))

    id= cursor.fetchone()[0]
    cursor.close()
    return id

def get_tarDB(conexao, codid):
    tar='Folga'
    wekd=''
    if datetime.today().weekday()==0:
        wekd='tarefaseg'
    elif datetime.today().weekday()==1:
        wekd='tarefater'
    elif datetime.today().weekday()==2:
        wekd='tarefaqua'
    elif datetime.today().weekday()==3:
        wekd='tarefaqui'
    elif datetime.today().weekday()==4:
        wekd='tarefasex'
    
    if datetime.today().weekday()<5:
        cursor = conexao.cursor()

    
        cursor.execute('SELECT ' + wekd + ' FROM usuarios WHERE id=?;', (codid,))

        tar= cursor.fetchone()[0]
        cursor.close()
    return tar

def get_UinfoDB(conexao, codname):
    tar=[]
    cursor = conexao.cursor()

    
    cursor.execute('SELECT * FROM usuarios WHERE nome=?;', (codname,))

    tar= cursor.fetchone()
    cursor.close()
    return tar
    
def upd_UinfoDB(conexao, codname, nome, tarseg, tarter, tarqua, tarqui, tarsex, admin):
    
    cursor = conexao.cursor()
    
    cursor.execute("""UPDATE usuarios 
                   SET nome = ?, tarefaseg=?, tarefater=?, tarefaqua=?, tarefaqui=?, tarefasex=?, admin=?
                   WHERE nome=?;""", (nome, tarseg, tarter, tarqua, tarqui, tarsex, admin, codname))

    conexao.commit()
    cursor.close()
    
def del_UserDB(conexao, codname):
    
    cursor = conexao.cursor()
    
    cursor.execute("""DELETE FROM usuarios 
                   WHERE nome=?;""", (codname,))

    conexao.commit()
    cursor.close()
    
def carregarBanco():
    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()
    cursor.execute("""
                      CREATE TABLE IF NOT EXISTS usuarios (
                              id INTEGER NOT NULL PRIMARY KEY ,
                              nome TEXT UNIQUE NOT NULL,
                              tarefaseg TEXT,
                              tarefater TEXT,
                              tarefaqua TEXT,
                              tarefaqui TEXT,
                              tarefasex TEXT,
                              admin INTEGER
                              );""")
    cursor.close()
    conn.close()
    print('Banco OK')
    
def inserirUserDB(idu, nome, tarseg, tarter, tarqua, tarqui, tarsex, admin):
    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()

    # inserindo dados na tabela
    cursor.execute("""
                       INSERT INTO usuarios (id, nome, tarefaseg, tarefater, tarefaqua, tarefaqui, tarefasex, admin)
                       VALUES (?,?,?,?,?,?,?,?)
                       """, (idu, nome, tarseg, tarter, tarqua, tarqui, tarsex, admin))

    conn.commit()
    cursor.close()
    conn.close()
    print("Comando executado")
    
def inserirComandoDB():
    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()
    #cursor.execute("delete from usuarios where id=4525")
    """lista = [(1, 'JoãoVictor', 'Ia', 'Ybarra', 'Metodos', 'IA2', 'EAD'), 
             (2, 'Rubens', 'IA', 'Modelagem', 'Luciano', 'IA2', 'TIM'),
             (3, 'André', 'IA', 'Ybarra', 'Metodos', 'IA2', 'EAD'),
             (4, 'Robson', 'IA', 'Ybarra', 'Metodos', 'IA2', 'EAD'),
             (5, 'ProfJoao', 'IA', 'Machine Learning', 'Python', 'IA2', 'App')
             ]"""
    cursor.execute("UPDATE usuarios set admin = 1")
    # inserindo dados na tabela
    #cursor.executemany("INSERT INTO usuarios (id, nome, tarefaseg, tarefater, tarefaqua, tarefaqui, tarefasex)VALUES (?,?,?,?,?,?,?)", lista)

    conn.commit()
    
    print("Comando executado")
    
"""
  _____                                             
 |  ___|  _   _   _ __     ___    ___     ___   ___ 
 | |_    | | | | | '_ \   / __|  / _ \   / _ \ / __|
 |  _|   | |_| | | | | | | (__  | (_) | |  __/ \__ \
 |_|      \__,_| |_| |_|  \___|  \___/   \___| |___/
                                                    """    

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
    
def limpa_temp():
    files = os.listdir(PATH + '/temp_dir')
    for f in files:
        os.remove(PATH + '/temp_dir/'+f)
        
def conta_temp():
    DIR = PATH + '/temp_dir'
    list = os.listdir(DIR) 
    number_files = len(list)
    return number_files   

"""
      _                          _               
     | |   __ _   _ __     ___  | |   __ _   ___ 
  _  | |  / _` | | '_ \   / _ \ | |  / _` | / __|
 | |_| | | (_| | | | | | |  __/ | | | (_| | \__ \
  \___/   \__,_| |_| |_|  \___| |_|  \__,_| |___/"""

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
        central(self, int(self.vid.width), int(self.vid.height)+30)
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
                show_prediction_labels_on_image(PATH+ '/temp_dir/' + str(rndid) + '.jpg', predict(PATH+ '/temp_dir/' + str(rndid) + '.jpg', PATH + '/model/mod.clf'))
            if self.argwc==2:
                
                tardi = facerecTarefa_tk(None, rndid)
                tardi.focus_force()
                self.withdraw()
                self.wait_window(tardi)
                self.deiconify()
            if self.argwc==3:
                conn = sqlite3.connect('usuarios.db')
                predics = predict(PATH+ '/temp_dir/' + str(rndid) + '.jpg', PATH + '/model/mod.clf')
                try:
                    test = predics[1][0]
                    messagebox.showinfo("Erro", "Mais de uma face foi detectada")
                    conn.close()
                except IndexError:
                    try:
                
                        testadm=check_ifAdmDB(conn, predics[0][0])
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
        central(self, 600, 300)
        
        self.configure(background='#b3d0e3')
        self.title("Editar um Usuário - FaceTask")
        self.iconbitmap('facetaskico.ico')
        self.resizable(0,0)
        limpa_temp()
        self.initialize()
        self.loadCombo()
        self.selectUser.bind('<<ComboboxSelected>>', self.modified)
    
    def modified(self, event):
        conn = sqlite3.connect('usuarios.db')
        info = get_UinfoDB(conn, self.selectUser.get())
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
            upd_UinfoDB(conn, self.selectUser.get(), self.nomeuser.get(), self.tarseg.get(), self.tarter.get(), self.tarqua.get(), self.tarqui.get(), self.tarsex.get(), self.checkad.get())
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
                id = get_idDB(conn, self.selectUser.get())
                shutil.rmtree(PATH + "/train_dir/" + str(id))
                del_UserDB(conn, self.selectUser.get())
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
        central(self, 600, 300)
        self.configure(background='#b3d0e3')
        self.title("Adicionar um Usuário - FaceTask")
        self.iconbitmap('facetaskico.ico')
        self.resizable(0,0)
        limpa_temp()
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
        elif conta_temp()==0:
            messagebox.showinfo("Notificação", "Por favor, escolha sua primeira imagem.")
        else:
            seed(datetime.now())
            rndid=randint(1, 9999)
            if not os.path.exists(PATH + '/train_dir/' + str(rndid)):
                try:
                    inserirUserDB(rndid, self.nomeuser.get(), self.tarseg.get(), self.tarter.get(), self.tarqua.get(), self.tarqui.get(), self.tarsex.get(), self.checkad.get())
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
        central(self, 300, 150)
        self.parent = parent
        self.resizable(0,0)
        self.configure(background='#b3d0e3')
        self.title("Escolher Imagem - FaceTask")
        self.iconbitmap('facetaskico.ico')
        self.initialize()
    def on_closing(self):
        limpa_temp()
        self.destroy()
        
    def initialize(self):    
        self.grid()
        self.lblDig= tkinter.Label(self, text="Escolha como adicionar sua imagem", background='#b3d0e3', font=("Arial",12, 'bold'))

        self.lblCon= tkinter.Label(self, text="Imagens pendentes: " + str(conta_temp()), background='#b3d0e3', font="-size 10 -weight bold")
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
        self.lblCon.config(text="Imagens pendentes: " + str(conta_temp()))
        
    def OnButtonSalvarClick(self):
        self.destroy()

        
    def OnButtonAICarWebClick(self):
        wc = facerecWebCam_tk(self, 1)
        self.wait_window(wc)
        self.lblCon.config(text="Imagens pendentes: " + str(conta_temp()))
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
        central(self, 700, 300)
        self.resizable(0,0)
        self.configure(background='#b3d0e3')
        self.title("Tarefa do Dia - FaceTask")
        self.iconbitmap('facetaskico.ico')
        self.initialize()
    
    def initialize(self):    
        self.grid()
        conn = sqlite3.connect('usuarios.db')
        predics = predict(PATH+ '/temp_dir/' + str(self.idmigt) + '.jpg', PATH + '/model/mod.clf')
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
                
                self.nomet=get_nameDB(conn, predics[0][0])
                self.tarefat=get_tarDB(conn, predics[0][0])
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
        central(self, 350, 150)
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
        if conta_temp()>0:
            pathadd = ei.pathadd
            conn = sqlite3.connect('usuarios.db')
            id = get_idDB(conn, self.selectUser.get())
        
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
        central(self, 420, 300)
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
        if check_allAdmDB(conn)==1 or check_noAdmDB(conn)==1:
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
        central(self, 400, 230)
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
        show_prediction_labels_on_image(pathima, predict(pathima, PATH + '/model/mod.clf'))
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
        show_prediction_labels_on_image(PATH + '/test_image2.jpg', predict(PATH + '/test_image2.jpg', PATH + '/model/mod.clf'))
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


         
#este é ponto onde o programa se inicia
#se foi chamado a partir do interpretador python, o _name_  automaticamente será "__main__"
if __name__ == "__main__":
    limpa_temp()
    carregarBanco()
    
 
    #inserirComandoDB()
    
    menu = facerecMenu_tk(None)
    
  
    menu.mainloop()               
    
