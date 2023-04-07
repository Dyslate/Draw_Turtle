import tkinter as tk
import xml.etree.ElementTree as ET
import os
import re
from tkinter import messagebox

from ivy.std_api import *
from pathlib import Path


def get_project_root() -> str:
    return os.path.join(str(Path(__file__).parent), "dessin.xml")


# Fonction qui efface toute les traces à l'écrans
def clear_widgets():
    canvas.delete("all")


class Tortue:
    def __init__(self):
        self.x = 300
        self.y = 300
        self.xBase = 300
        self.yBase = 300
        self.penActivated = True
        self.orientation = 0  # 0 pour le nord, 1 pour l'est, 2 pour le sud, 3 pour l'ouest
        self.commands = []  # pour save le dessin en xml.

    def avancer(self, agent, value, ajouterCommande=True):
        value = int(value)
        if self.orientation == 0:
            if self.penActivated:
                canvas.create_line(self.x, self.y, self.x, self.y - value)
            self.y -= value
        elif self.orientation == 1:
            if self.penActivated:
                canvas.create_line(self.x, self.y, self.x + value, self.y)
            self.x += value
        elif self.orientation == 2:
            if self.penActivated:
                canvas.create_line(self.x, self.y, self.x, self.y + value)
            self.y += value
        elif self.orientation == 3:
            if self.penActivated:
                canvas.create_line(self.x, self.y, self.x - value, self.y)
            self.x -= value
        if ajouterCommande:
            self.commands.append(("AVANCE", value))

    def reculer(self, agent, value):
        value = int(value)
        self.avancer(self, -value, False)
        self.commands.append(("RECULE", value))

    def tournerDroite(self, agent, value):
        self.orientation += 1
        if self.orientation > 3:
            self.orientation = 0
        self.avancer(self, value, False)
        self.commands.append(("TOURNEDROITE", value))

    def tournerGauche(self, agent, value):
        self.orientation -= 1
        if self.orientation < 0:
            self.orientation = 3
        self.avancer(self, value, False)
        self.commands.append(("TOURNEGAUCHE", value))

    def leverCrayon(self, agent):
        self.penActivated = False
        self.commands.append("LEVECRAYON")

    def baisserCrayon(self, agent):
        self.penActivated = True
        self.commands.append("BAISSECRAYON")

    def origine(self, agent):
        self.x, self.y, self.orientation = self.xBase, self.yBase, 0
        self.commands.append("ORIGINE")

    def restaurer(self, agent):
        self.x = self.xBase
        self.y = self.yBase
        self.commands.append("RESTAURER")

    def nettoyer(self, agent):
        canvas.delete("all")
        #  tortue.origine(self)
        self.commands.append("NETTOYER")

    def changerCouleur(self, r, v, b):
        # code pour changer la couleur du crayon à partir des composantes r v b
        print("changer couleur")

    # def fixerCap(self,value):
    # code pour fixer le cap de la tortue de manière absolue
    def fixerPosition(self, agent, x, y):
        self.x, self.y = x, y

    def lancerCommandes(self, commands):
        #  print(commands)
        commands = commands.split("\n")
        for cmd in commands:
            """Créé une regex qui récupère ce qu'il y a après REPETE dans un premier groupe, exemple: REPETE3
            Recupère dans un groupe deux l'interieur de []"""

            match = re.match(r'^REPETE (\d+) \[(.+)+]', cmd)
            print(match)
            if match:
                print("HIT")
                n = int(match.group(1))
                print(n)
                actions = match.group(2)
                actions = actions.split("\n")
                print("Actions : ", actions)
                for i in range(n):
                    for j in range(len(actions)):
                        self.lancerCommandes(actions[j])
                    #  print(actions[j])
            else:
                print("Commande à traiter: ", cmd)
                self.traiterCommande(cmd)

    def traiterCommande(self, command):
        # Vérifier la validité de la commande et exécuter la fonction appropriée
        if command == "LEVECRAYON":
            self.penActivated = False
        elif command == "BAISSECRAYON":
            self.penActivated = True
        elif command.startswith("AVANCE"):
            value = int(command.split(" ")[1])
            self.avancer(self, value, True)
        elif command.startswith("TOURNEDROITE"):
            value = int(command.split(" ")[1])
            self.tournerDroite(self, value)
        elif command.startswith("TOURNEGAUCHE"):
            value = int(command.split(" ")[1])
            self.tournerGauche(self, value)
        elif command.startswith("RECULE"):
            value = int(command.split(" ")[1])
            self.reculer(self, value)
        elif command.startswith("ORIGINE"):
            self.origine(self)
        elif command.startswith("NETTOIE"):
            self.nettoyer(self)

    def sauver(self):
        print("sauver")
        root = ET.Element("dessin")
        # print(self.commands)
        for cmd in self.commands:
            print("CECI EST LA COMMANDE: ", cmd)
            if cmd[0] == "AVANCE":
                ET.SubElement(root, "avance", dist=str(cmd[1]))
            elif cmd[0] == "TOURNEDROITE":
                ET.SubElement(root, "droite", dist=str(cmd[1]))
            elif cmd[0] == "TOURNEGAUCHE":
                ET.SubElement(root, "gauche", dist=str(cmd[1]))
            elif cmd == "LEVECRAYON":
                ET.SubElement(root, "lever")
            elif cmd == "BAISSECRAYON":
                ET.SubElement(root, "baisser")
            elif cmd[0] == "RECULE":
                ET.SubElement(root, "recule", dist=str(cmd[1]))
            elif cmd == "ORIGINE":
                ET.SubElement(root, "origine")
            elif cmd == "NETTOIE":
                ET.SubElement(root, "nettoie\n")
        tree = ET.ElementTree(root)

        tree.write(get_project_root())


root = tk.Tk()
root.title("Visualiseur")

# Crée un canvas pour dessiner sur
canvas = tk.Canvas(root, width=600, height=400)
canvas.pack()

IvyInit("test")
IvyStart()

# Création d'un bouton "play"
play_button = tk.Button(root, text="Jouer", command=lambda: tortue.lancerCommandes(command_text.get("1.0", "end-1c")))
play_button.pack()

# Création d'un bouton "save"
save_button = tk.Button(root, text="Enregistrer", command=lambda: tortue.sauver())
save_button.pack()

# Création d'une zone de saisie pour les commandes
command_text = tk.Text(root)
command_text.pack()

tortue = Tortue()
IvyBindMsg(tortue.avancer, "^AVANCE\s(.*)$")
IvyBindMsg(tortue.reculer, "^RECULE\s(.*)$")
IvyBindMsg(tortue.tournerDroite, "^TOURNEDROITE\s(.*)$")
IvyBindMsg(tortue.tournerGauche, "^TOURNEGAUCHE\s(.*)$")
IvyBindMsg(tortue.leverCrayon, "^LEVECRAYON$")
IvyBindMsg(tortue.baisserCrayon, "^BAISSECRAYON$")
IvyBindMsg(tortue.origine, "^ORIGINE$")
IvyBindMsg(tortue.restaurer, "^RESTAURE$")
IvyBindMsg(tortue.nettoyer, "^NETTOIE$")
IvyBindMsg(tortue.changerCouleur, "^FCC\s")

###################################################
# PARTIE 2: AUTRE FENETRE POUR L'EDITEUR DE TEXTE #
###################################################


root2 = tk.Tk()
root2.title("Editeur de texte")
root2.geometry("400x800")

frameBouton = tk.Frame(root2)
frameBouton.pack(side="left", fill="y")

# Création d'un canvas contenant les labels
canvas = tk.Canvas(root2, highlightthickness=0)
canvas.pack(side="left", fill="both", expand=True)

# Ajout d'une scrollbar pour le canvas
scrollbar = tk.Scrollbar(root2, orient="vertical", command=canvas.yview)
scrollbar.pack(side="right", fill="y")
canvas.configure(yscrollcommand=scrollbar.set)

frameLabel = tk.Frame(root2)
frameLabel.pack(side="right", expand=True)
canvas.create_window((0, 0), window=frameLabel, anchor="nw")


# Ajout d'un binding pour adapter la taille du canvas lorsque la fenêtre est redimensionnée
def on_frame_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))


frameLabel.bind("<Configure>", on_frame_configure)


#######################
# PARTIE 2: FONCTIONS #
#######################

def deleteLabel(event):
    """Fonction appelée lorsqu'un label est cliqué."""
    if messagebox.askyesno("Supprimer", "Voulez-vous supprimer ce label ?"):
        event.widget.destroy()


# création des cadres de la grille
cadres = []
label_list = []

tailleCadre = 0
selectedLabel = None
cadre = tk.Frame(frameLabel, highlightthickness=0)


def highlight(event):
    global selectedLabel
    if selectedLabel:
        selectedLabel.configure(bg="white")
    selectedLabel = event.widget
    selectedLabel.configure(bg="yellow")


def creerLabel(text):
    global tailleCadre, selectedLabel, cadre, label_list
    cadre.grid(row=tailleCadre, column=1)
    cadres.append(cadre)
    label = tk.Label(cadre, text=text, bg="white", borderwidth=1, relief="solid", width=15)
    label.grid(row=tailleCadre, column=0, sticky="nsew")
    label_list.append(label)
    # Ajout des bindings pour delete un label et highlight
    label.bind("<Button-3>", deleteLabel)
    label.bind("<Button-1>", highlight)
    tailleCadre += 1
    print(tailleCadre)


# Fonctions pour les commandes des boutons
def importerCommande():
    print("test import")


def exporterCommande():
    print("test export")


def avancerCommande(valeur):
    if valeur != "":
        res = "avancer " + valeur
        creerLabel(res)


def reculerCommande(valeur):
    if valeur != "":
        res = "reculer " + valeur
        creerLabel(res)


def tournerDroiteCommande(valeur):
    if valeur != "":
        res = "tournerDroite " + valeur
        creerLabel(res)


def tournerGaucheCommande(valeur):
    if valeur != "":
        res = "tournerGauche " + valeur
        creerLabel(res)


def leverCrayonCommande():
    creerLabel("leverCrayon")


def baisserCrayonCommande():
    creerLabel("baisserCrayon")


def origineCommande():
    creerLabel("origine")


def restaurerCommande():
    creerLabel("restaurer")



def nettoyerCommande():
    creerLabel("nettoyer")


def diminuer_espace():
    print("test")


def augmenter_espace():
    global selectedLabel, tailleCadre, cadre,  label_list
    print(cadre.grid_size())
    row = selectedLabel.grid_info()['row']

    label_list.insert(row, tk.Label(cadre, text="<<New Data>>"))

    for widget in cadre.children.values():
        widget.grid_forget()

    for ndex, i in enumerate(label_list):
        i.grid(row=ndex)


  # if selectedLabel:
     #   row = selectedLabel.grid_info()['row']
        #print("Ligne sélectionnée: " + str(row))
    #    tailleCadre += 1



def repeatCommande(param):
    global tailleCadre, cadre, label_list
    cadres.append(cadre)
    bouton_plus = tk.Button(cadre, text="+", command=lambda: augmenter_espace(), width=2)
    bouton_plus.grid(row=tailleCadre, column=0, sticky="nsew")
    tailleCadre += 1

    label_list.append(bouton_plus)

    bouton_moins = tk.Button(cadre, text="-", command=lambda: diminuer_espace, width=2)
    bouton_moins.grid(row=tailleCadre, column=0, sticky="nsew")
    tailleCadre += 1

    label_list.append(bouton_moins)


    label_repeat = tk.Label(cadre, text="repeat " + param, bg="white", borderwidth=1, relief="solid", width=15)
    label_repeat.grid(row=tailleCadre, column=0, sticky="nsew")
    tailleCadre += 1

    label_list.append(label_repeat)

    label_debut = tk.Label(cadre, text="{", bg="white", borderwidth=1, relief="solid", width=15)
    label_debut.grid(row=tailleCadre, column=0, sticky="nsew")
    tailleCadre += 1

    label_list.append(label_debut)


    global taille_espace
    taille_espace = 3
    for i in range(taille_espace):
        label_espace = tk.Label(cadre, text=" ", bg="white", borderwidth=1, relief="solid", width=15)
        label_espace.grid(row=tailleCadre, column=0, sticky="nsew")
        label_espace.bind("<Button-1>", highlight)
        tailleCadre += 1

        label_list.append(label_espace)

    label_fin = tk.Label(cadre, text="}    ", bg="white", borderwidth=1, relief="solid", width=15)
    label_fin.grid(row=tailleCadre, column=0, sticky="nsew")
    tailleCadre+=1


    label_list.append(label_fin)

    # Ajout des bindings pour delete un label
    label_debut.bind("<Button-3>", deleteLabel)
    label_repeat.bind("<Button-3>", deleteLabel)
    label_espace.bind("<Button-3>", deleteLabel)
    label_fin.bind("<Button-3>", deleteLabel)
    bouton_plus.bind("<Button-3>", deleteLabel)
    bouton_moins.bind("<Button-3>", deleteLabel)


def fccCommande(valeur1, valeur2, valeur3):
    if valeur1 != "" and valeur2 != "" and valeur3 != "":
        res = "FCC " + valeur1 + " " + valeur2 + " " + valeur3
        creerLabel(res)


def fCapCommande(valeur):
    if valeur != "":
        res = "fCap " + valeur
        creerLabel(res)


def fPosCommande(valeur1, valeur2):
    if valeur1 != "" and valeur2 != "":
        res = "fPos " + valeur1 + " " + valeur2
        creerLabel(res)


# Avancer
# Création d'un cadre pour le bouton et le champ de texte "Avancer"
avancerFrame = tk.Frame(frameBouton)
avancerFrame.pack(side="top", anchor="w")
# Création d'un bouton "Avancer"
avancerBouton = tk.Button(avancerFrame, text="Avancer", command=lambda: avancerCommande(avancerTexte.get()), width=20)
avancerBouton.pack(side="left", fill="x")
# Création d'un champ de texte pour entrer du texte pour avancer
avancerTexte = tk.Entry(avancerFrame, width=10)
avancerTexte.pack(side="left", fill="x")

# Reculer
# Création d'un cadre pour le bouton et le champ de texte "Reculer"
reculerFrame = tk.Frame(frameBouton)
reculerFrame.pack(side="top", anchor="w")
# Création d'un bouton "reculer"
reculerBouton = tk.Button(reculerFrame, text="Reculer", command=lambda: reculerCommande(reculerTexte.get()), width=20)
reculerBouton.pack(side="left", fill="x")
# Création d'un champ de texte pour entrer du texte pour reculer
reculerTexte = tk.Entry(reculerFrame, width=10)
reculerTexte.pack(side="left", fill="x")

# Tourner à droite
# Création d'un cadre pour le bouton et le champ de texte "Tourner à droite"
tournerDroiteFrame = tk.Frame(frameBouton)
tournerDroiteFrame.pack(side="top", anchor="w")
# Création d'un bouton "Tourner à droite"
tournerDroiteBouton = tk.Button(tournerDroiteFrame, text="Tourner à Droite", command=lambda: tournerDroiteCommande(tournerDroiteTexte.get()), width=20)
tournerDroiteBouton.pack(side="left", fill="x")
# Création d'un champ de texte pour entrer du texte
tournerDroiteTexte = tk.Entry(tournerDroiteFrame, width=10)
tournerDroiteTexte.pack(side="left", fill="x")

# Tourner à gauche
# Création d'un cadre pour le bouton et le champ de texte "Tourner à droite"
tournerGaucheFrame = tk.Frame(frameBouton)
tournerGaucheFrame.pack(side="top", anchor="w")
# Création d'un bouton "Tourner à droite"
tournerGaucheBouton = tk.Button(tournerGaucheFrame, text="Tourner à Gauche",
                                command=lambda: tournerGaucheCommande(tournerGaucheTexte.get()), width=20)
tournerGaucheBouton.pack(side="left", fill="x")
# Création d'un champ de texte pour entrer du texte pour tourner à droite
tournerGaucheTexte = tk.Entry(tournerGaucheFrame, width=10)
tournerGaucheTexte.pack(side="left", fill="x")

# Lever Crayon Frame
leverCrayonFrame = tk.Frame(frameBouton)
leverCrayonFrame.pack(side="top", anchor="w")
# Création d'un bouton "Lever le crayon"
leverCrayonBouton = tk.Button(leverCrayonFrame, text="Lever le crayon", command=lambda: leverCrayonCommande(), width=20)
leverCrayonBouton.pack(side="left", fill="x")

# Baisser Crayon Frame
baisserCrayonFrame = tk.Frame(frameBouton)
baisserCrayonFrame.pack(side="top", anchor="w")
# Création d'un bouton "Baisser Crayon"
baisserCrayonBouton = tk.Button(baisserCrayonFrame, text="Baisser le crayon", command=lambda: baisserCrayonCommande(),
                                width=20)
baisserCrayonBouton.pack(side="left", fill="x")

# Création d'un bouton "Origine"
origineBouton = tk.Button(frameBouton, text="Origine", command=lambda: origineCommande(), width=20)
origineBouton.pack(side="top", anchor="w")

# Création d'un bouton "Restaurer"
restaurerBouton = tk.Button(frameBouton, text="Restaurer", command=lambda: restaurerCommande(), width=20)
restaurerBouton.pack(side="top", anchor="w")

# Création d'un bouton "Nettoyer"
nettoyerBouton = tk.Button(frameBouton, text="Nettoyer", command=lambda: nettoyerCommande(), width=20)
nettoyerBouton.pack(side="top", anchor="w")

# FCC
# Création d'un cadre pour le bouton et le champ de texte "FCC"
fccFrame = tk.Frame(frameBouton)
fccFrame.pack(side="top", anchor="w")
# Création d'un bouton "FCC r v b"
fccBouton = tk.Button(fccFrame, text="FCC", command=lambda: fccCommande(fccRed.get(), fccGreen.get(), fccBlue.get()),
                      width=20)
fccBouton.pack(side="left", fill="x")

# Création d'un champ de texte pour entrer du texte pour fcc r
fccRed = tk.Entry(fccFrame, width=10)
fccRed.pack(side="left", fill="x")
# Création d'un champ de texte pour entrer du texte pour fcc v
fccGreen = tk.Entry(fccFrame, width=10)
fccGreen.pack(side="left", fill="x")
# Création d'un champ de texte pour entrer du texte pour fcc b
fccBlue = tk.Entry(fccFrame, width=10)
fccBlue.pack(side="left", fill="x")

# fCap
# Création d'un cadre pour le bouton et le champ de texte "fCap"
fCapFrame = tk.Frame(frameBouton)
fCapFrame.pack(side="top", anchor="w")
# Création d'un bouton "fCap angle"
fCapBouton = tk.Button(fCapFrame, text="FCAP", command=lambda: fCapCommande(fCapTexte.get()), width=20)
fCapBouton.pack(side="left", fill="x")
# Création d'un champ de texte pour entrer du texte pour fCap
fCapTexte = tk.Entry(fCapFrame, width=10)
fCapTexte.pack(side="left", fill="x")

# Repeat
# Création d'un cadre pour le bouton et le champ de texte "Repeat"
repeatFrame = tk.Frame(frameBouton)
repeatFrame.pack(side="top", anchor="w")
# Création d'un bouton "repeat"
repeatBouton = tk.Button(repeatFrame, text="Repeat", command=lambda: repeatCommande(repeatTexte.get()), width=20)
repeatBouton.pack(side="left", fill="x")
# Création d'un champ de texte pour entrer du texte pour Repeat
repeatTexte = tk.Entry(repeatFrame, width=10)
repeatTexte.pack(side="left", fill="x")

# fPos
# Création d'un cadre pour le bouton et le champ de texte "fPos"
fPosFrame = tk.Frame(frameBouton)
fPosFrame.pack(side="top", anchor="w")
# Création d'un bouton "fPos x y"
fPosBouton = tk.Button(fPosFrame, text="FPOS", command=lambda: fPosCommande(fPosX.get(), fPosY.get()), width=20)
fPosBouton.pack(side="left", fill="x")
# Création d'un champ de texte pour entrer du texte pour fPosX
fPosX = tk.Entry(fPosFrame, width=10)
fPosX.pack(side="left", fill="x")
# Création d'un champ de texte pour entrer du texte pour fPosY
fPosY = tk.Entry(fPosFrame, width=10)
fPosY.pack(side="left", fill="x")

# Création d'un bouton "Import"
importerBouton = tk.Button(frameBouton, text="Import", command=lambda: importerCommande(), width=20)
importerBouton.pack(side="left", anchor="w")

# Création d'un bouton "Export"
exportBouton = tk.Button(frameBouton, text="Export", command=lambda: exporterCommande(), width=20)
exportBouton.pack(side="left", anchor="w")

# Boucle principale de tkinter pour afficher le visualisateur
root.mainloop()
# Bucle secondaire de tkinter pour afficher l'éditeur de texte
root2.mainloop()
