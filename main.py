import tkinter as tk

from ivy.std_api import *

global x
global y
global penActivated
global orientation


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

    def reculer(self, agent, value):
        value = int(value)
        self.avancer(self,-value)

    def tournerDroite(self, agent, value):
        self.orientation += 1
        if self.orientation > 3:
            self.orientation = 0
        self.avancer(self,value)

    def tournerGauche(self, agent, value):
        self.orientation -= 1
        if self.orientation < 0:
            self.orientation = 3
        self.avancer(self,value)

    def leverCrayon(self, agent):
        self.penActivated = False

    def baisserCrayon(self, agent):
        self.penActivated = True

    def origine(self, agent):
        self.x, self.y, self.orientation = self.xBase, self.yBase, 0


    def restaurer(self, agent):
        self.x = self.xBase
        self.y = self.yBase

    def nettoyer(self, agent):
        canvas.delete("all")
        tortue.origine(self)

     def changerCouleur(self,r,v,b):
     #code pour changer la couleur du crayon à partir des composantes r v b
        print("changer couleur")
    # def fixerCap(self,value):
    # code pour fixer le cap de la tortue de manière absolue
    def fixerPosition(self, agent, x, y):
        self.x, self.y = x, y


root = tk.Tk()
root.title("Application de dessin à la tortue-logo")

# Initialise les variables de position de la tortue
x = 50
y = 50
xBase = 50
yBase = 50
# Initialise le tracé de la tortue
penActivated = True
# Taille de la tortue
turtleSize = 72

# Crée un canvas pour dessiner sur
canvas = tk.Canvas(root, width=600, height=400)
canvas.pack()

# Créé l'objet qui se déplace
label = tk.Label(root, text=">", font=("Courier", turtleSize))

IvyInit("test")
IvyStart()
# Enregistre une fonction pour intercepter les commandes de la tortue
# IvyBindMsg(move_turtle, "^tortue command=(.*)$")

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
