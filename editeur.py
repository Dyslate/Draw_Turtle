import tkinter as tk
from tkinter import filedialog
import subprocess
import threading

class EditeurDeTexte:
    def __init__(self):
        # création des cadres de la grille
        self.tailleCadre = 0
        self.selectedLabel = None
        self.label_list = []

    def right_click(self, event):
        # Créer le menu contextuel
        context_menu = tk.Menu(root2, tearoff=0)
        context_menu.add_command(label="Ajouter ligne au dessus", command=lambda: self.add_line(event))

        # Afficher le menu contextuel
        context_menu.post(event.x_root, event.y_root)

    def add_line(self, event):
        # Ajoutez votre logique pour ajouter une ligne ici
        print("Ajouter une ligne")

        self.augmenter_espaceRow(event.widget.grid_info()['row'])

    def highlight(self, event):
        widget = event.widget
        # Vérifie si le texte du label est égal à '{' ou '}'
        if widget["text"] == "{" or widget["text"] == "}":
            return

        if widget == self.selectedLabel:
            self.selectedLabel.configure(bg="white")
            self.selectedLabel = None
        else:
            if self.selectedLabel:
                self.selectedLabel.configure(bg="white")
            widget.configure(bg="yellow")
            self.selectedLabel = widget


    # Ajout d'un binding pour adapter la taille du canvas lorsque la fenêtre est redimensionnée
    def on_frame_configure(self, event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def importerCommande(self, xml_data):
        def get_attr_value(tag, attr_name):
            if f"{attr_name}='" in tag:
                return int(tag.split(f"{attr_name}='")[1].split("'")[0])
            return None

        def parse_content(content):
            commands = []
            buffer = ""
            i = 0

            while i < len(content):
                c = content[i]

                if c == "<":
                    buffer = "<"
                    while c != ">":
                        i += 1
                        c = content[i]
                        buffer += c

                    if "avancer" in buffer:
                        dist = get_attr_value(buffer, "dist")
                        commands.append(f"AVANCE {dist}")
                    elif "reculer" in buffer:
                        dist = get_attr_value(buffer, "dist")
                        commands.append(f"RECULE {dist}")
                    elif "droite" in buffer:
                        angle = get_attr_value(buffer, "angle")
                        commands.append(f"TOURNEDROITE {angle}")
                    elif "gauche" in buffer:
                        angle = get_attr_value(buffer, "angle")
                        commands.append(f"TOURNEGAUCHE {angle}")
                    elif "lever" in buffer:
                        commands.append("LEVECRAYON")
                    elif "baisser" in buffer:
                        commands.append("BAISSECRAYON")
                    elif "origine" in buffer:
                        commands.append("ORIGINE")
                    elif "restaure" in buffer:
                        commands.append("RESTAURE")
                    elif "nettoyer" in buffer:
                        commands.append("NETTOIE")
                    elif "crayon" in buffer:
                        r = get_attr_value(buffer, "rouge")
                        v = get_attr_value(buffer, "vert")
                        b = get_attr_value(buffer, "bleu")
                        commands.append(f"FCC {r} {v} {b}")
                    elif "cap" in buffer:
                        angle = get_attr_value(buffer, "angle")
                        commands.append(f"FCAP {angle}")
                    elif "position" in buffer:
                        x = get_attr_value(buffer, "x")
                        y = get_attr_value(buffer, "y")
                        commands.append(f"FPOS[{x} {y}]")
                    elif "<répéter" in buffer:
                        repeat_times = get_attr_value(buffer, "fois")
                        commands.append(f"REPETE {repeat_times}")
                        commands.append("{")
                    elif "/répéter" in buffer:
                        commands.append("}")
                else:
                    i += 1

            return commands

        dessin_start = xml_data.find("<dessin>") + 8
        dessin_end = xml_data.find("</dessin>")
        dessin_content = xml_data[dessin_start:dessin_end]

        return parse_content(dessin_content)

    # Fonctions pour les commandes des boutons
    def importer(self):
        xml = ""
        file_path = filedialog.askopenfilename()
        # Vérifier si un fichier a été sélectionné
        if file_path:
            # Ouvrir le fichier et lire son contenu
            with open(file_path, 'r', encoding="utf-8") as f:
                xml_str = f.read()
            # print(xml_str)
            xml = xml_str
        else:
            print('Aucun fichier sélectionné.')

        commands = self.importerCommande(xml)
        for i in commands:
            self.creerLabel(i)

    def exporterCommande(self, commandes):
        i = 0
        res = ""
        while i < len(commandes):
            text = commandes[i]
            if text.startswith("AVANCE"):
                res += "<avancer dist='" + text.split(" ")[1] + "'/>\n"
            elif text.startswith("RECULE"):
                res += "<reculer dist='" + text.split(" ")[1] + "'/>\n"
            elif text.startswith("TOURNEDROITE"):
                res += "<droite angle='" + text.split(" ")[1] + "'/>\n"
            elif text.startswith("TOURNEGAUCHE"):
                res += "<gauche angle='" + text.split(" ")[1] + "'/>\n"
            elif text.startswith("LEVECRAYON"):
                res += "<lever/>" + "\n"
            elif text.startswith("BAISSECRAYON"):
                res += "<baisser/>" + "\n"
            elif text.startswith("ORIGINE"):
                res += "<origine/>" + "\n"
            elif text.startswith("NETTOIE"):
                res += "<nettoyer/>" + "\n"
            elif text.startswith("RESTAURE"):
                res += "<restaurer/>" + "\n"
            elif text.startswith("FCC"):
                res += "<crayon rouge='" + text.split(" ")[1] + "' vert='" + text.split(" ")[2] + "' bleu='" + \
                       text.split(" ")[3] + "'/>\n"
            elif text.startswith("FCAP"):
                res += "<cap angle='" + text.split(" ")[1] + "'/>\n"
            elif text.startswith("FPOS"):
                coords = text.split("[")[1].split("]")[0].split()
                x, y = coords[0], coords[1]
                res += "<position x='{}' y='{}'/>\n".format(x, y)
            elif text.startswith("REPETE"):
                n = int(text.split(" ")[1])
                print("ici nombre de fois: " + str(n))
                i += 1  # Passer à la ligne suivante
                print("ici commande[i] vaut" + commandes[i])
                if commandes[i].startswith("{"):
                    i += 1  # Passer à la ligne suivante
                    inner_commands = []
                    bracket_count = 1
                    print("bracker_count vaut " + str(bracket_count) + "\n")
                    while bracket_count > 0:
                        if commandes[i].startswith("{"):
                            bracket_count += 1
                        elif commandes[i].startswith("}"):
                            bracket_count -= 1
                        if bracket_count > 0:
                            inner_commands.append(commandes[i])
                            print("inner commands ici: " + str(inner_commands) + "\n")
                            i += 1
                    res += "<répéter fois='" + str(n) + "'>\n"
                    res += self.exporterCommande(inner_commands)
                    res += "</répéter>\n"
            i += 1
        return res

    # Adapter la méthode pour utiliser exporterCommande.
    def exporter(self):
        commandes = [label.cget("text") for label in self.label_list]
        del commandes[0]
        del commandes[0]
        print(commandes)
        res = ""
        res += "<dessin>\n"
        res += self.exporterCommande(commandes)
        res += "</dessin>"

        file_path = filedialog.asksaveasfilename(defaultextension='.xml')
        # Écrire le fichier XML avec la variable res
        print(res)
        with open(file_path, 'w', encoding="utf-8") as f:
            f.write(res)

    def clear(self):
        self.label_list = []
        for label in cadre.winfo_children():
            if label.cget("text") == "+" or label.cget("text") == "-":
                self.label_list.append(label)
                continue
            else:
                label.destroy()
        self.selectedLabel = None
        self.tailleCadre = 2

    def run_main_program(self):
        # Remplacez le chemin d'accès au fichier main.py par le vôtre.
        file_path = "visualiseur.py"
        # Lancer le programme en utilisant subprocess
        subprocess.run(["python", file_path])

    def openVisualiseur(self):
        # Créer un nouveau thread pour exécuter le programme
        new_thread = threading.Thread(target=self.run_main_program)
        # Démarrer le nouveau thread
        new_thread.start()

    def avancerCommande(self, valeur):
        res = "AVANCE " + valeur
        if valeur != "":
            if self.selectedLabel:
                self.modify(res)
            else:
                self.creerLabel(res)

    def reculerCommande(self, valeur):
        res = "RECULE " + valeur
        if valeur != "":
            if self.selectedLabel:
                self.modify(res)
            else:
                self.creerLabel(res)

    def tournerDroiteCommande(self, valeur):
        res = "TOURNEDROITE " + valeur
        if valeur != "":
            if self.selectedLabel:
                self.modify(res)
            else:
                self.creerLabel(res)

    def tournerGaucheCommande(self, valeur):
        res = "TOURNEGAUCHE " + valeur
        if valeur != "":
            if self.selectedLabel:
                self.modify(res)
            else:
                self.creerLabel(res)

    def leverCrayonCommande(self):
        res = "LEVECRAYON"
        if self.selectedLabel:
            self.modify(res)
        else:
            self.creerLabel(res)

    def baisserCrayonCommande(self):
        res = "BAISSECRAYON"
        if self.selectedLabel:
            self.modify(res)
        else:
            self.creerLabel(res)

    def origineCommande(self):
        res = "ORIGINE"
        print("test")
        print(self.selectedLabel)

        if self.selectedLabel:
            self.modify(res)
        else:
            self.creerLabel(res)

    def restaurerCommande(self):
        res = "RESTAURE"
        if self.selectedLabel:
            self.modify(res)
        else:
            self.creerLabel(res)

    def nettoyerCommande(self):
        res = "NETTOIE"
        if self.selectedLabel:
            self.modify(res)
        else:
            self.creerLabel(res)

    def refresh(self):
        for widget in cadre.children.values():
            widget.grid_forget()
        for ndex, i in enumerate(self.label_list):
            i.grid(row=ndex)
            print(str(i))

    def diminuer_espace(self):
        if self.selectedLabel:
            row = self.selectedLabel.grid_info()['row']
            deleted_rows = self.delete_labels(row)
            self.refresh()
            self.tailleCadre -= deleted_rows
            self.selectedLabel = None

    def delete_labels(self, row):
        deleted_rows = 0
        is_repete = "REPETE" in self.label_list[row].cget("text")

        if is_repete:
            # Supprimer le label "REPETE" initial
            del self.label_list[row]
            deleted_rows += 1

            # Supprimer les lignes jusqu'à "}"
            while row < len(self.label_list) and "}" not in self.label_list[row].cget("text"):
                if "REPETE" in self.label_list[row].cget("text"):
                    deleted_rows += self.delete_labels(row)
                    row += 1  # Incrémentez row après l'appel récursif
                else:
                    del self.label_list[row]
                    deleted_rows += 1
            if row < len(self.label_list) and "}" in self.label_list[row].cget("text"):
                del self.label_list[row]
                deleted_rows += 1
        elif "{" in self.label_list[row].cget("text") or "}" in self.label_list[row].cget("text"):
            # Cette fonction ne devrait pas être appelée avec un "{" ou "}" sélectionné
            pass
        else:
            del self.label_list[row]
            deleted_rows += 1
        return deleted_rows

    def diminuer_espaceRow(self, row):
        del self.label_list[row]
        self.refresh()
        self.tailleCadre -= 1

    def modify(self, param):
        if self.selectedLabel:
            row = self.selectedLabel.grid_info()['row']
            label = tk.Label(cadre, text=param, bg="white", borderwidth=1, relief="solid", width=20)
            label.grid(row=row, column=0, sticky="nsew")
            label.bind("<Button-1>", self.highlight)
            label.bind("<Button-3>", self.right_click)
            self.label_list[row] = label
            self.refresh()

    def modifyRow(self, param, row):
        label = tk.Label(cadre, text=param, bg="white", borderwidth=1, relief="solid", width=20)
        label.grid(row=row, column=0, sticky="nsew")
        label.bind("<Button-1>", self.highlight)
        label.bind("<Button-3>", self.right_click)
        self.label_list[row] = label
        self.refresh()

    def augmenter_espace(self):
        if self.selectedLabel:
            row = self.selectedLabel.grid_info()['row']
            label_espace = tk.Label(cadre, text=" ", bg="white", borderwidth=1, relief="solid", width=20)
            label_espace.grid(row=self.tailleCadre, column=0, sticky="nsew")
            label_espace.bind("<Button-1>", self.highlight)
            label_espace.bind("<Button-3>", self.right_click)

            self.label_list.insert(row, label_espace)
            self.refresh()
            self.tailleCadre += 1
        else:
            row = self.tailleCadre
            label_espace = tk.Label(cadre, text=" ", bg="white", borderwidth=1, relief="solid", width=20)
            label_espace.grid(row=self.tailleCadre, column=0, sticky="nsew")
            label_espace.bind("<Button-1>", self.highlight)
            self.label_list.insert(row, label_espace)
            self.refresh()
            self.tailleCadre += 1

    def augmenter_espaceRow(self, row):
        label_espace = tk.Label(cadre, text=" ", bg="white", borderwidth=1, relief="solid", width=20)
        label_espace.grid(row=self.tailleCadre, column=0, sticky="nsew")
        label_espace.bind("<Button-1>", self.highlight)
        label_espace.bind("<Button-3>", self.right_click)

        self.label_list.insert(row, label_espace)
        self.refresh()
        self.tailleCadre += 1

    def creerLabel(self, text):
        cadre.grid(row=self.tailleCadre, column=2)
        label = tk.Label(cadre, text=text, bg="white", borderwidth=1, relief="solid", width=20)
        label.grid(row=self.tailleCadre, column=0, sticky="nsew")

        self.label_list.append(label)
        # Ajout des bindings pour delete un label et highlight
        label.bind("<Button-1>", self.highlight)
        label.bind("<Button-3>", self.right_click)
        self.tailleCadre += 1

    def repeatCommande(self, param):
        if param != "":
            if self.selectedLabel:
                cadre.grid(row=self.tailleCadre, column=1)
                row = self.selectedLabel.grid_info()['row']
                # Ajouter une ligne
                self.augmenter_espaceRow(row)

                # Modify le nouvel espace créé
                self.modifyRow("REPETE " + param, row)

                # Ajouter une ligne
                self.augmenter_espaceRow(row + 1)

                # Modify le nouvel espace créé
                self.modifyRow("{", row + 1)

                # Ajouter une ligne
                self.augmenter_espaceRow(row + 2)

                # Ajouter une ligne
                self.augmenter_espaceRow(row + 3)

                # Modify le nouvel espace créé
                self.modifyRow("}", row + 3)

            else:
                cadre.grid(row=self.tailleCadre, column=1)
                label_repeat = tk.Label(cadre, text="REPETE " + param, bg="white", borderwidth=1, relief="solid",
                                        width=20)
                label_repeat.grid(row=self.tailleCadre, column=0, sticky="nsew")
                self.tailleCadre += 1
                self.label_list.append(label_repeat)

                label_debut = tk.Label(cadre, text="{", bg="white", borderwidth=1, relief="solid", width=20)
                label_debut.grid(row=self.tailleCadre, column=0, sticky="nsew")
                self.tailleCadre += 1
                self.label_list.append(label_debut)

                label_espace = tk.Label(cadre, text=" ", bg="white", borderwidth=1, relief="solid", width=20)
                label_espace.grid(row=self.tailleCadre, column=0, sticky="nsew")
                self.tailleCadre += 1
                self.label_list.append(label_espace)

                label_fin = tk.Label(cadre, text="}", bg="white", borderwidth=1, relief="solid", width=20)
                label_fin.grid(row=self.tailleCadre, column=0, sticky="nsew")
                self.tailleCadre += 1

                self.label_list.append(label_fin)

                # Ajout des bindings pour delete un label
                #label_debut.bind("<Button-1>", self.highlight)
                label_repeat.bind("<Button-1>", self.highlight)
                label_debut.bind("<Button-3>", self.right_click)
                label_repeat.bind("<Button-3>", self.right_click)
                label_fin.bind("<Button-3>", self.right_click)
                label_espace.bind("<Button-3>", self.right_click)

                #label_fin.bind("<Button-1>", self.highlight)
                label_espace.bind("<Button-1>", self.highlight)

    def fccCommande(self, valeur1, valeur2, valeur3):
        res = "FCC " + valeur1 + " " + valeur2 + " " + valeur3
        if valeur1 != "" and valeur2 != "" and valeur3 != "":
            if self.selectedLabel:
                self.modify(res)
            else:
                self.creerLabel(res)

    def fCapCommande(self, valeur):
        res = "FCAP " + valeur
        if valeur != "":
            if self.selectedLabel:
                self.modify(res)
            else:
                self.creerLabel(res)

    def fPosCommande(self, valeur1, valeur2):
        res = "FPOS [" + valeur1 + " " + valeur2 + "]"
        if valeur1 != "" and valeur2 != "":
            if self.selectedLabel:
                self.modify(res)
            else:
                self.creerLabel(res)


###################################################
# PARTIE 2: AUTRE FENETRE POUR L'EDITEUR DE TEXTE #
###################################################
editeur = EditeurDeTexte()

root2 = tk.Tk()
root2.title("Editeur de texte")
root2.geometry("850x500")

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

label_list = []

frameLabel.bind("<Configure>", editeur.on_frame_configure)

#######################
# PARTIE 2: FONCTIONS #
#######################


# création des cadres de la grille
cadres = []

tailleCadre = 0
selectedLabel = None
cadre = tk.Frame(frameLabel, highlightthickness=0)

# Avancer
# Création d'un cadre pour le bouton et le champ de texte "Avancer"
avancerFrame = tk.Frame(frameBouton)
avancerFrame.pack(side="top", anchor="w")
# Création d'un bouton "Avancer"
avancerBouton = tk.Button(avancerFrame, text="Avancer", command=lambda: editeur.avancerCommande(avancerTexte.get()),
                          width=20)
avancerBouton.pack(side="left", fill="x")
# Création d'un champ de texte pour entrer du texte pour avancer
avancerTexte = tk.Entry(avancerFrame, width=10)
avancerTexte.pack(side="left", fill="x")

# Reculer
# Création d'un cadre pour le bouton et le champ de texte "Reculer"
reculerFrame = tk.Frame(frameBouton)
reculerFrame.pack(side="top", anchor="w")
# Création d'un bouton "reculer"
reculerBouton = tk.Button(reculerFrame, text="Reculer", command=lambda: editeur.reculerCommande(reculerTexte.get()),
                          width=20)
reculerBouton.pack(side="left", fill="x")
# Création d'un champ de texte pour entrer du texte pour reculer
reculerTexte = tk.Entry(reculerFrame, width=10)
reculerTexte.pack(side="left", fill="x")

# Tourner à droite
# Création d'un cadre pour le bouton et le champ de texte "Tourner à droite"
tournerDroiteFrame = tk.Frame(frameBouton)
tournerDroiteFrame.pack(side="top", anchor="w")
# Création d'un bouton "Tourner à droite"
tournerDroiteBouton = tk.Button(tournerDroiteFrame, text="Tourner à Droite",
                                command=lambda: editeur.tournerDroiteCommande(tournerDroiteTexte.get()), width=20)
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
                                command=lambda: editeur.tournerGaucheCommande(tournerGaucheTexte.get()), width=20)
tournerGaucheBouton.pack(side="left", fill="x")
# Création d'un champ de texte pour entrer du texte pour tourner à droite
tournerGaucheTexte = tk.Entry(tournerGaucheFrame, width=10)
tournerGaucheTexte.pack(side="left", fill="x")

# Lever Crayon Frame
leverCrayonFrame = tk.Frame(frameBouton)
leverCrayonFrame.pack(side="top", anchor="w")
# Création d'un bouton "Lever le crayon"
leverCrayonBouton = tk.Button(leverCrayonFrame, text="Lever le crayon", command=lambda: editeur.leverCrayonCommande(),
                              width=20)
leverCrayonBouton.pack(side="left", fill="x")

# Baisser Crayon Frame
baisserCrayonFrame = tk.Frame(frameBouton)
baisserCrayonFrame.pack(side="top", anchor="w")
# Création d'un bouton "Baisser Crayon"
baisserCrayonBouton = tk.Button(baisserCrayonFrame, text="Baisser le crayon",
                                command=lambda: editeur.baisserCrayonCommande(),
                                width=20)
baisserCrayonBouton.pack(side="left", fill="x")

# Création d'un bouton "Origine"
origineBouton = tk.Button(frameBouton, text="Origine", command=lambda: editeur.origineCommande(), width=20)
origineBouton.pack(side="top", anchor="w")

# Création d'un bouton "Restaurer"
restaurerBouton = tk.Button(frameBouton, text="Restaurer", command=lambda: editeur.restaurerCommande(), width=20)
restaurerBouton.pack(side="top", anchor="w")

# Création d'un bouton "Nettoyer"
nettoyerBouton = tk.Button(frameBouton, text="Nettoyer", command=lambda: editeur.nettoyerCommande(), width=20)
nettoyerBouton.pack(side="top", anchor="w")

# FCC
# Création d'un cadre pour le bouton et le champ de texte "FCC"
fccFrame = tk.Frame(frameBouton)
fccFrame.pack(side="top", anchor="w")
# Création d'un bouton "FCC r v b"
fccBouton = tk.Button(fccFrame, text="FCC",
                      command=lambda: editeur.fccCommande(fccRed.get(), fccGreen.get(), fccBlue.get()), width=20)
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
fCapBouton = tk.Button(fCapFrame, text="FCAP", command=lambda: editeur.fCapCommande(fCapTexte.get()), width=20)
fCapBouton.pack(side="left", fill="x")
# Création d'un champ de texte pour entrer du texte pour fCap
fCapTexte = tk.Entry(fCapFrame, width=10)
fCapTexte.pack(side="left", fill="x")

# Repeat
# Création d'un cadre pour le bouton et le champ de texte "Repeat"
repeatFrame = tk.Frame(frameBouton)
repeatFrame.pack(side="top", anchor="w")
# Création d'un bouton "repeat"
repeatBouton = tk.Button(repeatFrame, text="Repeat", command=lambda: editeur.repeatCommande(repeatTexte.get()),
                         width=20)
repeatBouton.pack(side="left", fill="x")
# Création d'un champ de texte pour entrer du texte pour Repeat
repeatTexte = tk.Entry(repeatFrame, width=10)
repeatTexte.pack(side="left", fill="x")

# fPos
# Création d'un cadre pour le bouton et le champ de texte "fPos"
fPosFrame = tk.Frame(frameBouton)
fPosFrame.pack(side="top", anchor="w")
# Création d'un bouton "fPos x y"
fPosBouton = tk.Button(fPosFrame, text="FPOS", command=lambda: editeur.fPosCommande(fPosX.get(), fPosY.get()), width=20)
fPosBouton.pack(side="left", fill="x")
# Création d'un champ de texte pour entrer du texte pour fPosX
fPosX = tk.Entry(fPosFrame, width=10)
fPosX.pack(side="left", fill="x")
# Création d'un champ de texte pour entrer du texte pour fPosY
fPosY = tk.Entry(fPosFrame, width=10)
fPosY.pack(side="left", fill="x")

bouton_plus = tk.Button(cadre, text="+", command=lambda: editeur.augmenter_espace(), width=20)
bouton_plus.grid(row=editeur.tailleCadre, column=0, sticky="nsew")
editeur.tailleCadre += 1

editeur.label_list.append(bouton_plus)

bouton_moins = tk.Button(cadre, text="-", command=lambda: editeur.diminuer_espace(), width=20)
bouton_moins.grid(row=editeur.tailleCadre, column=0, sticky="nsew")
editeur.tailleCadre += 1

editeur.label_list.append(bouton_moins)

# Création d'un bouton "Import"
importerBouton = tk.Button(frameBouton, text="Import", command=lambda: editeur.importer(), width=20)
importerBouton.pack(side="left", anchor="w")

# Création d'un bouton "Export"
exportBouton = tk.Button(frameBouton, text="Export", command=lambda: editeur.exporter(), width=20)
exportBouton.pack(side="left", anchor="w")

# Création d'un bouton "Clear"
clearBouton = tk.Button(frameBouton, text="Clear", command=lambda: editeur.clear(), width=20)
clearBouton.pack(side="left", anchor="w")

# Création d'un bouton "Send"
sendBouton = tk.Button(frameBouton, text="Ouvrir Visualiseur", command=lambda: editeur.openVisualiseur(), width=20)
sendBouton.pack(side="left", anchor="w")

# Bucle secondaire de tkinter pour afficher l'éditeur de texte
root2.mainloop()
