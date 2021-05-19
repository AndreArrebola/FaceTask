import sqlite3

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