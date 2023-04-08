import tkinter as tk
import xml.etree.ElementTree as ET
import os
import re
from tkinter import messagebox
class EditeurTexte:
    def __init__(self):
        self.root2 = tk.Tk()
        self.root2.title("Editeur de texte")
        self.root2.geometry("400x800")

        self.frameBouton = tk.Frame(self.root2)
        self.frameBouton.pack(side="left", fill="y")

        self.canvas = tk.Canvas(self.root2, highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        self.scrollbar = tk.Scrollbar(self.root2, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.frameLabel = tk.Frame(self.root2)
        self.frameLabel.pack(side="right", expand=True)
        self.canvas.create_window((0, 0), window=self.frameLabel, anchor="nw")

        self.label_list = []
        self.tailleCadre = 0
        self.selectedLabel = None
        self.cadre = tk.Frame(self.frameLabel, highlightthickness=0)
        self.cadres = []

        def on_frame_configure(event):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        self.frameLabel.bind("<Configure>", on_frame_configure)

        self.boutons = [("Importer", self.importerCommande), ("Exporter", self.exporterCommande),
                        ("Avancer", self.avancerCommande), ("Reculer", self.reculerCommande),
                        ("Tourner à droite", self.tournerDroiteCommande),
                        ("Tourner à gauche", self.tournerGaucheCommande),
                        ("Lever le crayon", self.leverCrayonCommande),
                        ("Baisser le crayon", self.baisserCrayonCommande), ("Origine", self.origineCommande),
                        ("Restaurer", self.restaurerCommande), ("Nettoyer", self.nettoyerCommande),
                        ("Diminuer l'espace", self.diminuer_espace), ("Augmenter l'espace", self.augmenter_espace)]

        for b in self.boutons:
            button = tk.Button(self.frameBouton, text=b[0], command=b[1])
            button.pack(fill="x")

    def highlight(self, event):
        if self.selectedLabel:
            self.selectedLabel.configure(bg="white")
        self.selectedLabel = event.widget
        self.selectedLabel.configure(bg="yellow")

    def importerCommande(self):
        print("test import")

    def exporterCommande(self):
        print("test export")

    def avancerCommande(self, valeur):
        if valeur != "":
            if self.selectedLabel:
                res = "avancer " + valeur
                self.modify(res)
            else:
                res = "avancer " + valeur
                self.creerLabel(res)

    def reculerCommande(self, valeur):
        if valeur != "":
            if self.selectedLabel:
                res = "reculer " + valeur
                self.modify(res)
            else:
                res = "reculer " + valeur
                self.creerLabel(res)

    def tournerDroiteCommande(self, valeur):
        if valeur != "":
            if self.selectedLabel:
                res = "tournerDroite " + valeur
                self.modify(res)
            else:
                res = "tournerDroite " + valeur
                self.creerLabel(res)

    def tournerGaucheCommande(self, valeur):
        if valeur != "":
            if self.selectedLabel:
                res = "tournerGauche " + valeur
                self.modify(res)
            else:
                res = "tournerGauche " + valeur
                self.creerLabel(res)

    def leverCrayonCommande(self):
        if self.selectedLabel:
            res = "leverCrayon"
            self.modify(res)
        else:
            res = "leverCrayon"
            self.creerLabel(res)

    def baisserCrayonCommande(self):
        if self.selectedLabel:
            res = "baisserCrayon"
            self.modify(res)
        else:
            res = "baisserCrayon"
            self.creerLabel(res)

    def origineCommande(self):
        if self.selectedLabel:
            res = "origine"
            self.modify(res)
        else:
            res = "origine"
            self.creerLabel(res)

    def restaurerCommande(self):
        if self.selectedLabel:
            res = "restaurer"
            self.modify(res)
        else:
            res = "restaurer"
            self.creerLabel(res)

    def nettoyerCommande(self):
        if self.selectedLabel:
            res = "nettoyer"
            self.modify(res)
        else:
            res = "nettoyer"
            self.creerLabel(res)

    def creerLabel(self, text):
        label = tk.Label(self.cadre, text=text, bg="white")
        label.bind("<Button-1>", self.highlight)
        label.pack(fill="x")
        self.label_list.append(label)
        self.tailleCadre += 1
        self.cadre.configure(height=self.tailleCadre * 25)
        self.cadre.pack_propagate(0)
        self.canvas.itemconfigure(self.cadre.id, height=self.tailleCadre * 25)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def modify(self, text):
        index = self.label_list.index(self.selectedLabel)
        self.label_list[index].configure(text=text)

    def augmenter_espace(self):
        if self.selectedLabel:
            res = "augmenter_espace"
            self.modify(res)
        else:
            res = "augmenter_espace"
            self.creerLabel(res)

    def diminuer_espace(self):
        if self.selectedLabel:
            res = "diminuer_espace"
            self.modify(res)
        else:
            res = "diminuer_espace"
            self.creerLabel(res)
    def run(self):
        self.root2.mainloop()

editeur = EditeurTexte()
editeur.run()