![FaceTask](https://raw.githubusercontent.com/AndreArrebola/FaceTask/master/facetask.png)

 O **FaceTask** é um programa em **Python** que utiliza *machine learning* para analisar rostos utilizando técnicas e bibliotecas de reconhecimento facial. 
 Basicamente, o sistema analisa múltiplos rostos, utiliza uma câmera conectada ao computador para identificar a pessoa e exibe a ela uma tarefa semanal. 
 
## 📝 Tabela de Conteúdos
<!--ts-->
   * [Visão Geral](#visao-geral)
   * [O que foi utilizado](#util)
   * [Instalação](#instal)
     * [Linux](#instlin)
<!--te-->

<a name="visao-geral"></a>

## 💻 Visão Geral
O programa foi construído para resolver um problema comum em algumas empresas: a divisão de tarefas semanais entre os funcionários. 
Assim, o sistema é alimentado com os dados de cada usuário, incluindo as tarefas de cada dia da semana e fotos de seu rosto, que podem ser obtidas por webcam ou um seletor de arquivos. 
Após o cadastro ser feito, ele poderá tirar uma foto utilizando a câmera e exibirá na tela qual será a tarefa do dia.
O FaceTask está funcional de forma básica, mas ainda pode ser expandido e possui algumas coisas a serem corrigidas. Então, não é necessariamente um programa concluído, mas ainda pode ser utilizado sem maiores problemas.

<a name="util"></a>

## 📦 O que foi utilizado
<!--ts-->
   * **Python 3**
   * **Biblioteca para interface gráfica:** [tkinter](https://docs.python.org/3/library/tkinter.html)
   * **Bibliotecas de machine learning e reconhecimento facial:** [Dlib](https://github.com/davisking/dlib), [OpenCV](https://github.com/opencv/opencv), [scikit-learn](https://github.com/scikit-learn/scikit-learn), [face_recognition](https://github.com/ageitgey/face_recognition) 
   * **Editores de texto:** [Spyder](https://www.spyder-ide.org) e [VS Code](https://code.visualstudio.com)
   * **Ambientes virtuais:** [Anaconda](https://www.anaconda.com
   )(Windows), [VMWare Player](https://www.vmware.com/br/products/workstation-player.html)(Linux). Outro tipo de ambiente para Linux está sendo estudado.

<!--te-->

## 🛠 Instalação

* Verifique se o Python está instalado em sua máquina. Caso não esteja, instale-o através [deste link](https://www.python.org/downloads/release/python-395/). 
* Faça a clonagem do projeto através desta página, a GUI de sua preferência ou o seguinte comando do Git:
`git clone https://github.com/AndreArrebola/FaceTask.git`

#### Linux

No Terminal, digite os seguintes comandos para instalar as bibliotecas necessárias:
```
sudo apt install python3-tk
sudo apt install python3-pil
sudo apt install python3-pil.imagetk
sudo apt install cmake

pip install opencv-python
pip install scikit-learn
pip install face_recognition
```
Caso não possua o pip, instale-o:
``sudo apt install python3-pip``

Os comandos acima são baseados em Ubuntu/Debian, mas todas as bibliotecas devem estar disponíveis em outras versões, apenas com comandos diferentes. 

Após tudo instalado, abra a pasta do projeto pelo terminal e execute-o:

``python3 facetask.py``







 
 
 


