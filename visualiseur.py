import subprocess
import threading
import time
import tkinter as tk
from tkinter import filedialog

from PIL import Image, ImageDraw
from ivy.std_api import *

from tkinter import simpledialog


class CustomDialog(simpledialog.Dialog):
    def __init__(self, parent, title, items):
        self.items = items
        self.selected_item = None
        self.entries = []
        super().__init__(parent, title)

    def body(self, frame):
        self.listbox = tk.Listbox(frame, selectmode=tk.SINGLE, exportselection=False)
        self.listbox.pack(side=tk.TOP, padx=5, pady=5)

        for item in self.items:
            self.listbox.insert(tk.END, item)

        self.listbox.bind("<<ListboxSelect>>", self.on_item_selected)

        self.entries_frame = tk.Frame(frame)
        self.entries_frame.pack(side=tk.TOP, padx=5, pady=5)

    def on_item_selected(self, event):
        index = self.listbox.curselection()[0]
        self.selected_item = self.items[index]

        # Map items to the number of parameters required
        item_parameters = {
            "AVANCE": 1,
            "RECULE": 1,
            "TOURNEDROITE": 1,
            "TOURNEGAUCHE": 1,
            "LEVECRAYON": 0,
            "BAISSECRAYON": 0,
            "RESTAURE": 0,
            "NETTOIE": 0,
            "FCC": 3,
            "FCAP": 1,
            "FPOS": 2,
        }

        # Clear entries frame
        for widget in self.entries_frame.winfo_children():
            widget.destroy()
        self.entries.clear()

        # Create entries based on the number of parameters
        num_params = item_parameters.get(self.selected_item, 0)
        for i in range(num_params):
            label = tk.Label(self.entries_frame, text=f"Paramètre {i + 1}:")
            entry = tk.Entry(self.entries_frame)
            label.grid(row=i, column=0, sticky="e", padx=5, pady=5)
            entry.grid(row=i, column=1, sticky="w", padx=5, pady=5)
            self.entries.append(entry)

    def apply(self):
        params = " ".join(entry.get() for entry in self.entries)
        if self.selected_item == "FPOS":
            params = f"[{params}]"
        self.result = f"{self.selected_item} {params}".strip()


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
        self.capFixed = False
        self.items = ["AVANCE", "RECULE", "TOURNEDROITE", "TOURNEGAUCHE", "LEVECRAYON", "BAISSECRAYON", "ORIGINE", "RESTAURE", "NETTOIE", "FCC", "FCAP", "FPOS"]  # Add other items as needed


        menubar = tk.Menu(root)
        # Créer un menu déroulant
        actions_menu = tk.Menu(menubar, tearoff=0)

        # Ajouter des boutons au menu déroulant
        actions_menu.add_command(label="Import", command=self.importer)
        actions_menu.add_command(label="Save", command=self.sauver)
        actions_menu.add_command(label="Clear", command=self.clear)
        actions_menu.add_command(label="Open Editor", command=self.openEditeur)

        # Ajouter le menu déroulant à la barre de menus
        menubar.add_cascade(label="File", menu=actions_menu)

        # Afficher la barre de menus
        root.config(menu=menubar)


        # Créer le menu contextuel
        self.context_menu = tk.Menu(root, tearoff=0)
        self.context_menu.add_command(label="Add", command=lambda: self.ajouter(self.clicked_label))
        self.context_menu.add_command(label="Modify", command=lambda: self.modifier(self.clicked_label))
        self.context_menu.add_command(label="Delete", command=lambda: self.supprimer(self.clicked_label))


    def show_context_menu(self, event):
        # Afficher le menu contextuel à la position du curseur
        self.context_menu.post(event.x_root, event.y_root)
        self.clicked_label = event.widget

    def ajouter(self, label):
        # Trouver l'index du label sélectionné dans la liste_historique
        label_index = self.liste_historique.index(label)

        dialog = CustomDialog(root, "Ajouter un nouvel élément", self.items)
        if dialog.result:
            new_label_text = dialog.result

            new_label = tk.Label(label.master, text=new_label_text, bg="white", borderwidth=1, relief="solid", width=20)

            # Insérer le nouveau label dans la liste_historique au-dessus du label sélectionné
            self.liste_historique.insert(label_index, new_label)

            # Mettre à jour les positions des labels existants
            for i, hist_label in enumerate(self.liste_historique):
                hist_label.grid(row=i + 1, column=1, sticky="nsew")

            # Associer le clic droit au menu contextuel pour le nouveau label
            new_label.bind("<Button-3>", self.show_context_menu)
        else:
            tk.messagebox.showerror("Error", "Wrong Selected!")


    def modifier(self, label):
        # Demander le nouveau texte à l'utilisateur

        dialog = CustomDialog(root, "Ajouter un nouvel élément", self.items)
        if dialog.result:
            new_label_text = dialog.result
            # Mettre à jour le texte du label sélectionné
            label.config(text=new_label_text)

            # Trouver l'index du label sélectionné dans la liste_historique
            label_index = self.liste_historique.index(label)

            # Mettre à jour l'objet label dans liste_historique avec le nouveau texte
            self.liste_historique[label_index].config(text=new_label_text)


        else:
            tk.messagebox.showerror("Error", "Wrong Selected!")



    def supprimer(self, label):
        for i, hist_label in enumerate(self.liste_historique):
            if hist_label == label:
                del self.liste_historique[i]
                break
        label.destroy()


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
        if self.capFixed:
            self.angle += self.cap
            print(self.capFixed)
            print(str("l'angle vaut: "+str(angle_degrees)))
        else:
            angle_degrees = self.angle
            print(str(angle_degrees))

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
        self.cap = float(x)
        if self.capFixed:
            self.capFixed = False
        else:
            self.capFixed = True

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
                label.config(bg="White")  # Restaurer la couleur d'arrière-plan d'origine
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
                        commands.append(f"FPOS [{x} {y}]")
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
        commands = self.importerCommande(xml)
        self.clear()
        for i in commands:
            label = tk.Label(right_panel, text=i, bg="white", borderwidth=1, relief="solid", width=20)
            self.nombreCommande += 1
            label.grid(row=self.nombreCommande + 1, column=1, sticky="nsew")
            label.bind("<Button-3>", self.show_context_menu)

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

            # Récupérer la couleur de l'objet
            item_color = canvas2.itemcget(item, "fill")

            if item_type == "line":
                draw.line(item_coords, fill=item_color)

        # Sauvegarder l'image PIL en format JPEG
        image.save(filename, "JPEG")

    def run_main_program(self):
        # Remplacez le chemin d'accès au fichier main.py par le vôtre.
        file_path = "editeur.py"

        # Lancer le programme en utilisant subprocess
        subprocess.run(["python", file_path])

    def openEditeur(self):
        # Créer un nouveau thread pour exécuter le programme
        new_thread = threading.Thread(target=self.run_main_program)

        # Démarrer le nouveau thread
        new_thread.start()


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
IvyBindMsg(tortue.changerCouleur,
           "^FCC (\d{1,2}|1\d{2}|2[0-4]\d|25[0-5]) (\d{1,2}|1\d{2}|2[0-4]\d|25[0-5]) (\d{1,2}|1\d{2}|2[0-4]\d|25[0-5])$")

# Création d'un frame pour les boutons, la zone de saisie et l'historique
right_panel = tk.Frame(root)
right_panel.pack(side=tk.LEFT, anchor="ne", padx=10, pady=10)

# Création d'un frame pour les boutons, la zone de saisie et l'historique
south_panel = tk.Frame(root)
south_panel.pack(side=tk.BOTTOM, anchor="s", padx=10, pady=10)

canvas2 = tk.Canvas(south_panel, width=600, height=400)
canvas2.pack(side=tk.TOP, anchor="n", padx=10, pady=10)

# Création d'un label "Historique"
history_label = tk.Label(right_panel, text="History")
history_label.grid(row=1, column=1, pady=5)

# Création d'un frame pour l'historique
history_frame = tk.Frame(right_panel)
history_frame.grid(row=1, column=1)

# Création d'un bouton "play"
play_button = tk.Button(south_panel, text="Play", command=lambda: tortue.jouer(), width=20)
play_button.pack()

# Création d'un bouton "Clear"
clear_button = tk.Button(south_panel, text="Clear", command=lambda: tortue.clear(), width=20)
clear_button.pack()



# Création du widget "Text" pour afficher le contenu du terminal
terminal = tk.Text(south_panel, wrap=tk.WORD)
terminal.pack_forget()

# Slideur
tortue.sleep_time = tk.DoubleVar()
tortue.sleep_time.set(1.0)  # Valeur initiale du délai en secondes
slider = tk.Scale(south_panel, from_=0.1, to=5.0, resolution=0.1, orient=tk.HORIZONTAL,
                  label="Pause Time (s)", variable=tortue.sleep_time,
                  length=150, sliderlength=20)
slider.pack()

# Création d'une zone de saisie pour les commandes
command_text = tk.Entry(south_panel, width=25)
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


# Boucle principale de tkinter pour afficher le visualisateur
root.mainloop()
