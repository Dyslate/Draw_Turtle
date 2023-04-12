import subprocess
import threading
import time
import tkinter as tk
from tkinter import filedialog

from PIL import Image, ImageDraw
from ivy.std_api import *


# Fonction qui efface toute les traces à l'écrans
def clear_widgets():
    canvas2.delete("all")


class Tortue():
    def __init__(self):
        self.x = 300
        self.y = 300
        self.xBase = 300
        self.yBase = 300
        self.penActivated = True
        self.angle = 90
        self.commands = []  # pour save le dessin en xml.
        self.couleur = "#FF0000"
        self.nombreCommande = 0
        self.liste_historique = []
        self.sleep_time = 1.0
        self.is_closed = False
        self.cap = 100
    def close_visualizer(self, event):
        self.is_closed = True  # Ajoutez cette ligne pour mettre à jour l'attribut is_closed

    def avancer(self, agent, value, ajouterCommande=True):
        value = int(value)

        # Série de tailor pour ne pas utiliser la bibliothèque math et calculer cos et sinus
        def cos(angle):
            result = 0
            term = 1
            for i in range(20):
                result += term
                term *= -angle * angle / (2 * i + 1) / (2 * i + 2)
            return result

        def sin(angle):
            result = 0
            term = angle
            for i in range(1, 20):
                result += term
                term *= -angle * angle / (2 * i) / (2 * i + 1)
            return result

        # Conversion de l'angle en radians
        angle_degrees = self.angle
        angle_radians = angle_degrees * (3.141592653589793 / 180)

        longueur = value

        # Calcul des coordonnées du point d'arrivée sans utiliser la bibliothèque math
        x2 = self.x + longueur * cos(angle_radians)
        y2 = self.y - longueur * sin(angle_radians)

        print("x1 : ", self.x, "y1 : ", self.y)
        print("x2 : ", x2, "y2 : ", y2)
        print("longueur " + str(longueur))
        # Création de la ligne
        canvas2.create_line(self.x, self.y, x2, y2, fill=self.couleur)

        print("couleur " + self.couleur)
        self.x = x2
        self.y = y2

        if ajouterCommande:
            self.commands.append(("AVANCE", value))

    def reculer(self, agent, value):
        value = int(value)
        self.avancer(self, -value, False)
        self.commands.append(("RECULE", value))

    def tournerDroite(self, agent, value):
        self.angle -= int(value)
        self.commands.append(("TOURNEDROITE", value))

    def tournerGauche(self, agent, value):
        self.angle += int(value)
        self.commands.append(("TOURNEGAUCHE", value))

    def leverCrayon(self, agent):
        self.penActivated = False
        self.commands.append("LEVECRAYON")

    def baisserCrayon(self, agent):
        self.penActivated = True
        self.commands.append("BAISSECRAYON")

    def origine(self, agent):
        self.x, self.y = self.xBase, self.yBase
        self.angle = 90
        self.commands.append("ORIGINE")

    def restaurer(self, agent):
        self.x = self.xBase
        self.y = self.yBase
        self.commands.append("RESTAURER")

    def run_command(self):
        command = command_text.get()
        terminal.insert(tk.END, f'{command}\n')
        process.stdin.write(command + '\n')
        process.stdin.flush()
        command_text.config(state=tk.NORMAL)

    def run_command_text(self, text):
        command = text
        terminal.insert(tk.END, f'{command}\n')
        process.stdin.write(command + '\n')
        process.stdin.flush()
        command_text.config(state=tk.NORMAL)

    def on_enter_key(self, event):
        command_text.config(state=tk.DISABLED)
        thread = threading.Thread(target=self.run_command)
        thread.start()

    def nettoyer(self, agent):
        canvas2.delete("all")
      #  tortue.origine(self)
        self.commands.append("NETTOYER")

    def clear(self):
        canvas2.delete("all")
        for label in self.liste_historique:
            label.destroy()
        self.liste_historique = []
        self.x, self.y = self.xBase, self.yBase
        self.angle = 90
        self.commands.append("ORIGINE")

    def changerCouleur(self, agent, r, v, b):
        r, v, b = int(r), int(v), int(b)  # Convertir les chaînes de caractères en entiers
        # code pour changer la couleur du crayon à partir des composantes r v b
        hex_code = '#{0:02X}{1:02X}{2:02X}'.format(r, v, b)
        self.couleur = hex_code
        print("changer couleur en :" + hex_code)

    # code pour fixer le cap de la tortue de manière absolue
    def fixerCap(self, agent, x):
        self.cap = x

    def setPosition(self, agent, x, y):
        self.x, self.y = int(x), int(y)
    def jouer(self):
        print("Lancement de jouer")

        def execute_commands(commandes, labels):
            index = 0
            while index < len(commandes):
                commande = commandes[index]
                label = labels[index]
                label.config(bg="yellow")  # Mettre en évidence le label en jaune
                history_frame.update()  # Mettre à jour l'affichage pour montrer le changement de couleur
                if commande.startswith("REPETE"):
                    repetitions = int(commande.split()[1])
                    index += 1
                    nested_commands, nested_labels, index = extract_nested_commands(commandes, labels, index)
                    for _ in range(repetitions):
                        execute_commands(nested_commands, nested_labels)
                else:
                    self.run_command_text(commande)
                    print(commande)
                    time.sleep(self.sleep_time.get())
                    index += 1
                label.config(bg="SystemButtonFace")  # Restaurer la couleur d'arrière-plan d'origine
                history_frame.update()  # Mettre à jour l'affichage pour montrer le changement de couleur

        def extract_nested_commands(commandes, labels, start_index):
            nested_commands = []
            nested_labels = []
            brace_count = 0
            index = start_index

            while index < len(commandes):
                current_command = commandes[index]
                current_label = labels[index]
                if current_command == '{':
                    brace_count += 1
                elif current_command == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        return nested_commands, nested_labels, index + 1
                if brace_count > 0:
                    nested_commands.append(current_command)
                    nested_labels.append(current_label)
                index += 1
            return nested_commands, nested_labels, index

        liste_commandes = [label.cget("text") for label in self.liste_historique]
        thread = threading.Thread(target=lambda: execute_commands(liste_commandes, self.liste_historique))
        thread.start()

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

        print(xml)
        commands = editeur.importerCommande(xml)
        #        self.lancerCommandes(commands)

        for i in commands:
            label = tk.Label(right_panel, text=i, bg="white", borderwidth=1, relief="solid", width=20)
            self.nombreCommande += 1
            label.grid(row=self.nombreCommande + 1, column=1, sticky="nsew")
            self.liste_historique.append(label)

    def sauver(self):
        # Créer une image PIL avec les mêmes dimensions que le canvas
        image = Image.new("RGB", (canvas2.winfo_width(), canvas2.winfo_height()), "white")
        draw = ImageDraw.Draw(image)
        filename = filedialog.asksaveasfilename(defaultextension='.JPEG')

        # Redessiner les objets du canvas sur l'image PIL
        for item in canvas2.find_all():
            item_type = canvas2.type(item)
            item_coords = canvas2.coords(item)
            #TODO gestion couleur
            if item_type == "line":
                draw.line(item_coords, fill="blue")

        # Sauvegarder l'image PIL en format JPEG
        image.save(filename, "JPEG")


root = tk.Tk()
root.title("Visualiseur")
tortue = Tortue()

root.bind('<Destroy>', tortue.close_visualizer)



# Crée un canvas pour dessiner sur

def on_connection(agent, connected):
    if connected:
        print(f"{agent} s'est connecté")
    else:
        print(f"{agent} s'est déconnecté")


def on_message(agent, *larg):
    print(f"Agent {agent}: Message reçu {larg}")


def on_command(agent, *larg):
    print(f"Agent {agent}: Commande reçue {larg}")


def start_ivy(app_name):
    IvyInit(app_name, f"{app_name} is ready", 1, on_connection, on_message)
    IvyStart()


app_name = "BusTortue"
start_ivy(app_name)

IvyBindMsg(tortue.avancer, "^AVANCE\s+(\d+(?:\.\d+)?)$")
IvyBindMsg(tortue.reculer, "^RECULE\s+(\d+(?:\.\d+)?)$")
IvyBindMsg(tortue.tournerDroite, "^TOURNEDROITE\s+(\d+(?:\.\d+)?)$")
IvyBindMsg(tortue.tournerGauche, "^TOURNEGAUCHE\s+(\d+(?:\.\d+)?)$")
IvyBindMsg(tortue.leverCrayon, "^LEVECRAYON$")
IvyBindMsg(tortue.baisserCrayon, "^BAISSECRAYON$")
IvyBindMsg(tortue.origine, "^ORIGINE$")
IvyBindMsg(tortue.restaurer, "^RESTAURE$")
IvyBindMsg(tortue.nettoyer, "^NETTOIE$")
IvyBindMsg(tortue.fixerCap, "^FCAP\s+(\d+(?:\.\d+)?)$")
IvyBindMsg(tortue.setPosition, r"^FPOS\s+\[(\d+)\s+(\d+)\]$")
IvyBindMsg(tortue.changerCouleur,"^FCC (\d{1,2}|1\d{2}|2[0-4]\d|25[0-5]) (\d{1,2}|1\d{2}|2[0-4]\d|25[0-5]) (\d{1,2}|1\d{2}|2[0-4]\d|25[0-5])$")

# Création d'un frame pour les boutons, la zone de saisie et l'historique
right_panel = tk.Frame(root)
right_panel.pack(side=tk.LEFT, anchor="ne", padx=10, pady=10)

# Création d'un frame pour les boutons, la zone de saisie et l'historique
south_panel = tk.Frame(root)
south_panel.pack(side=tk.BOTTOM, anchor="s", padx=10, pady=10)

canvas2 = tk.Canvas(south_panel, width=600, height=400)
canvas2.pack(side=tk.TOP, anchor="n", padx=10, pady=10)

# Création d'un label "Historique"
history_label = tk.Label(right_panel, text="Historique")
history_label.grid(row=1, column=1, pady=5)

# Création d'un frame pour l'historique
history_frame = tk.Frame(right_panel)
history_frame.grid(row=1, column=1)

# Création d'un bouton "play"
play_button = tk.Button(south_panel, text="Jouer", command=lambda: tortue.jouer())
play_button.pack()

# Création d'un bouton "importer"
importer_button = tk.Button(south_panel, text="Importer", command=lambda: tortue.importer())
importer_button.pack()

# Création d'un bouton "save"
save_button = tk.Button(south_panel, text="Enregistrer", command=lambda: tortue.sauver())
save_button.pack()

# Création d'un bouton "save"
clear_button = tk.Button(south_panel, text="Clear", command=lambda: tortue.clear())
clear_button.pack()


# Création du widget "Text" pour afficher le contenu du terminal
terminal = tk.Text(south_panel, wrap=tk.WORD)
terminal.pack(expand=True, fill=tk.BOTH)

# Slideur
tortue.sleep_time = tk.DoubleVar()
tortue.sleep_time.set(1.0)  # Valeur initiale du délai en secondes
slider = tk.Scale(south_panel, from_=0.1, to=5.0, resolution=0.1, orient=tk.HORIZONTAL, label="Temps de pause (s)",
                  variable=tortue.sleep_time)
slider.pack()

# Création d'une zone de saisie pour les commandes
command_text = tk.Entry(south_panel)
# Lier la touche "Enter" à la fonction on_enter_key
command_text.bind("<Return>", tortue.on_enter_key)
command_text.pack()

# Exécuter python ivyprobe.py en utilisant subprocess
process = subprocess.Popen(['python', 'ivyprobe.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, text=True)


# Créer un thread pour lire la sortie du processus et l'afficher dans le widget "Text"
def read_output():
    while True:
        output = process.stdout.readline()
        if output:
            terminal.insert(tk.END, output)
        else:
            break


output_thread = threading.Thread(target=read_output)
output_thread.start()


class EditeurDeTexte:
    def __init__(self):
        # création des cadres de la grille
        self.tailleCadre = 0
        self.selectedLabel = None
        self.label_list = []

    def highlight(self, event):
        widget = event.widget
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

    def send(self):
        commandes = [label.cget("text") for label in self.label_list]
        del commandes[0]
        del commandes[0]
        print(commandes)
        if tortue.is_closed:
            tk.messagebox.showerror("Erreur", "Le visualiseur est fermé")
        else:
            for i in commandes:
                label = tk.Label(right_panel, text=i, bg="white", borderwidth=1, relief="solid", width=20)
                tortue.nombreCommande += 1
                label.grid(row=tortue.nombreCommande + 1, column=1, sticky="nsew")
                tortue.liste_historique.append(label)


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
        #TODO DEBUG
        if self.selectedLabel:
            row = self.selectedLabel.grid_info()['row']
            deleted_rows = 0
            if "REPETE" in self.label_list[row].cget("text"):
                # Supprimer les lignes jusqu'à "}"
                while row < len(self.label_list) and "}" not in self.label_list[row].cget("text"):
                    del self.label_list[row]
                    deleted_rows += 1
                if row < len(self.label_list) and "}" in self.label_list[row].cget("text"):
                    del self.label_list[row]
                    deleted_rows += 1
            elif "{" in self.label_list[row].cget("text"):
                # Supprimer les lignes jusqu'à "}" et "REPETE"
                initial_row = row  # Ajoutez cette ligne pour conserver la position initiale de la ligne
                row += 1
                while row < len(self.label_list) and "}" not in self.label_list[row].cget("text"):
                    del self.label_list[row]
                    deleted_rows += 1
                if row < len(self.label_list) and "}" in self.label_list[row].cget("text"):
                    del self.label_list[row]
                    deleted_rows += 1
                    row -= 1
                if row > 0 and "REPETE" in self.label_list[row - 1].cget("text"):
                    del self.label_list[row - 1]
                    deleted_rows += 1
                initial_row -= (deleted_rows - 1)  # Ajustez l'index initial_row
                del self.label_list[initial_row + 1]  # Supprimez le label avec "{"
                deleted_rows += 1  # Mettez à jour le nombre de lignes supprimées
            elif "}" in self.label_list[row].cget("text"):
                # Supprimer les lignes en remontant jusqu'à "REPETE"
                del self.label_list[row]
                deleted_rows += 1
                row -= 1
                while row > 0 and "REPETE" not in self.label_list[row].cget("text"):
                    del self.label_list[row]
                    deleted_rows += 1
                    row -= 1
                if row >= 0 and "REPETE" in self.label_list[row].cget("text"):
                    del self.label_list[row]
                    deleted_rows += 1
            else:
                del self.label_list[row]
                deleted_rows += 1
            self.refresh()
            self.tailleCadre -= deleted_rows
            self.selectedLabel = None

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

            self.label_list[row] = label
            self.refresh()

    def modifyRow(self, param, row):
        label = tk.Label(cadre, text=param, bg="white", borderwidth=1, relief="solid", width=20)
        label.grid(row=row, column=0, sticky="nsew")
        label.bind("<Button-1>", self.highlight)

        self.label_list[row] = label
        self.refresh()

    def augmenter_espace(self):
        if self.selectedLabel:
            row = self.selectedLabel.grid_info()['row']
            label_espace = tk.Label(cadre, text=" ", bg="white", borderwidth=1, relief="solid", width=20)
            label_espace.grid(row=self.tailleCadre, column=0, sticky="nsew")
            label_espace.bind("<Button-1>", self.highlight)
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
                label_debut.bind("<Button-1>", self.highlight)
                label_repeat.bind("<Button-1>", self.highlight)
                label_fin.bind("<Button-1>", self.highlight)
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
sendBouton = tk.Button(frameBouton, text="Send", command=lambda: editeur.send(), width=20)
sendBouton.pack(side="left", anchor="w")

# Boucle principale de tkinter pour afficher le visualisateur
root.mainloop()
# Bucle secondaire de tkinter pour afficher l'éditeur de texte
root2.mainloop()
