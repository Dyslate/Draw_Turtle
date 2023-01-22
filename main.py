import tkinter as tk
import xml.etree.ElementTree as ET
from typing import Tuple

from ivy.std_api import *
from pathlib import Path
import os


def get_project_root() -> str:
    return os.path.join(str(Path(__file__).parent), "dessin.xml")


# Fonction qui efface toute les traces à l'écrans
def clear_widgets():
    canvas.delete("all")


class Tortue:
    def __init__(self):
        self.x = 50
        self.y = 50
        self.xBase = 50
        self.yBase = 50
        self.penActivated = True
        self.orientation = 0  # 0 pour le nord, 1 pour l'est, 2 pour le sud, 3 pour l'ouest
        self.commands = []  # pour save le dessin en xml.

    def avancer(self, agent, value):
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
        self.commands.append(("AVANCE", value))

    def reculer(self, agent, value):
        value = int(value)
        self.avancer(self, -value)
        self.commands.append(("RECULE", value))

    def tournerDroite(self, agent, value):
        self.orientation += 1
        if self.orientation > 3:
            self.orientation = 0
        self.avancer(self, value)
        self.commands.append(("TOURNERDROITE", value))

    def tournerGauche(self, agent, value):
        self.orientation -= 1
        if self.orientation < 0:
            self.orientation = 3
        self.avancer(self, value)
        self.commands.append(("TOURNERGAUCHE", value))

    def leverCrayon(self, agent):
        self.penActivated = False
        self.commands.append("LEVERCRAYON")

    def baisserCrayon(self, agent):
        self.penActivated = True
        self.commands.append("BAISSERCRAYON")

    def origine(self, agent):
        self.x, self.y, self.orientation = self.xBase, self.yBase, 0
        self.commands.append("ORIGINE")

    def restaurer(self, agent):
        self.x = self.xBase
        self.y = self.yBase
        self.commands.append("RESTAURER")

    def nettoyer(self, agent):
        canvas.delete("all")
        tortue.origine(self)
        self.commands.append("NETTOYER")

    def changerCouleur(self, r, v, b):
        # code pour changer la couleur du crayon à partir des composantes r v b
        print("changer couleur")

    # def fixerCap(self,value):
    # code pour fixer le cap de la tortue de manière absolue
    def fixerPosition(self, agent, x, y):
        self.x, self.y = x, y

    def lancerCommandes(self, commandes):
        print("Jouer")
        # Splitter les commandes par lignes
        commands = commandes.split("\n")
        for command in commands:
            print(command)
            # Traiter chaque commande séparément
            self.traiterCommande(command)

    def traiterCommande(self, command):
        # Vérifier la validité de la commande et exécuter la fonction appropriée
        if command == "LEVECRAYON":
            self.penActivated = False
        elif command == "BAISSECRAYON":
            self.penActivated = True
        elif command.startswith("AVANCE"):
            value = int(command.split(" ")[1])
            self.avancer(self, value)
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
        elif command.startswith("NETTOYER"):
            self.nettoyer(self)

    def sauver(self):
        print("sauver")
        root = ET.Element("dessin")
        for cmd in self.commands:
            if cmd[0] == "AVANCE":
                ET.SubElement(root, "avancer", dist=str(cmd[1]))
            elif cmd[0] == "TOURNEDROITE":
                ET.SubElement(root, "droite", angle=str(cmd[1]))
            elif cmd[0] == "TOURNEGAUCHE":
                ET.SubElement(root, "gauche", angle=str(cmd[1]))
            elif cmd[0] == "LEVECRAYON":
                ET.SubElement(root, "lever")
            elif cmd[0] == "BAISSECRAYON":
                ET.SubElement(root, "baisser")

        tree = ET.ElementTree(root)
        print(tree)
        print(get_project_root())
        tree.write(get_project_root())


root = tk.Tk()
root.title("Application de dessin à la tortue-logo")

# Crée un canvas pour dessiner sur
canvas = tk.Canvas(root, width=600, height=400)
canvas.pack()

IvyInit("test")
IvyStart()
# Enregistre une fonction pour intercepter les commandes de la tortue
# IvyBindMsg(move_turtle, "^tortue command=(.*)$")

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
# Boucle principale de tkinter pour afficher l'application
root.mainloop()
