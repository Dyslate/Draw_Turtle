import math
import tkinter as tk
from turtle import Turtle
import ivy
import tkinter as tk
from ivy import *
from ivy.std_api import *

global x
global y
global penActivated


# Fonction qui efface toute les traces à l'écrans
def clear_widgets():
    for widget in root.winfo_children():
        widget.destroy()


def move_turtle(agent, args):
    global x
    global y
    global penActivated
    label.place(x=x+0.5*turtleSize, y=y-0.5*turtleSize)

    if str(args).__contains__(" "):
        command, value = args.split(" ")
        command = str(command).strip()
        value = str(value).strip()
        print("value:", value)
        print("commande:", command)
        value = int(value)

    else:
        print("pas d'espace")
        command = args
        command = str(command).strip()
        print("commande:", command)

    if command == "AVANCE":
        if penActivated:
            canvas.create_line(x, y, x + value, y)
        x += value
    elif command == "RECULE":
        if penActivated:
            canvas.create_line(x, y, x - value, y)
        x -= value
    elif command == "TOURNEDROITE":
        if penActivated:
            canvas.create_line(x, y, x, y + value)
        y += value
    elif command == "TOURNEGAUCHE":
        if penActivated:
            canvas.create_line(x, y, x, y - value)
        y -= value
    elif command == "LEVECRAYON":
        # code pour lever le crayon
        penActivated = False
    elif command == "BAISSECRAYON":
        # code pour baisser le crayon
        penActivated = True
    elif command == "ORIGINE":
        x, y = 50, 50
    elif command == "RESTAURE":
        # code pour restaurer l'état initial
        x = xBase
        y = yBase
    elif command == "NETTOIE":
        # code pour effacer toutes les traces de l'écran
        clear_widgets()
    elif command == "FCC":
        r, v, b = value.split()
        # code pour changer la couleur du crayon à partir des composantes r v b
    # elif command == "FCAP":
    # code pour fixer le cap de la tortue de manière absolue
    elif command == "FPOS":
        x, y = value.split()


root = tk.Tk()
root.title("Application de dessin à la tortue-logo")

# Initialise les variables de position de la tortue
x = 50
y = 50
xBase = 50
yBase = 50
# Initialise le tracé de la tortue
penActivated = True
#Taille de la tortue
turtleSize = 72

# Crée un canvas pour dessiner sur
canvas = tk.Canvas(root, width=600, height=400)
canvas.pack()

# Créé l'objet qui se déplace
label = tk.Label(root, text=">", font=("Courier", turtleSize))

IvyInit("test")
IvyStart()
# Enregistre une fonction pour intercepter les commandes de la tortue
IvyBindMsg(move_turtle, "^tortue command=(.*)$")

# Boucle principale de tkinter pour afficher l'application
root.mainloop()
