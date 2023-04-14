import subprocess
import threading
import time
import tkinter as tk
from tkinter import filedialog

from PIL import Image, ImageDraw
from ivy.std_api import *

from tkinter import simpledialog


class CustomDialog(simpledialog.Dialog):
    def __init__(self, parent, title, items, tortue_instance):
        self.items = items
        self.selected_item = None
        self.entries = []
        self.tortue_instance = tortue_instance

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

        if self.selected_item == "REPETE":
            num_repeats = int(params.split()[0])
            params = params.split()[0]  # Conserve uniquement le premier paramètre (nombre de répétitions)
            #    self.result = (f"{self.selected_item} {params}", num_repeats)

            # Ajouter les labels REPETE, {, lignes vides et }
            self.tortue_instance.ajouter_repete_labels(num_repeats, self.tortue_instance.clicked_label)
        else:
            self.result = (f"{self.selected_item} {params}".strip(), None)


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
        self.items = ["AVANCE", "RECULE", "TOURNEDROITE", "TOURNEGAUCHE", "LEVECRAYON", "BAISSECRAYON", "ORIGINE",
                      "RESTAURE", "NETTOIE", "FCC", "FCAP", "FPOS"]

        self.zoom_scale = 1.0
        self.zoom_increment = 0.1
        self.pan_start = None

        self.gomme_active = tk.BooleanVar()

        menubar = tk.Menu(root)
        # Créer un menu déroulant
        actions_menu = tk.Menu(menubar, tearoff=0)

        # Ajouter des boutons au menu déroulant
        actions_menu.add_command(label="Import", command=self.importer)
        actions_menu.add_command(label="Save in JPEG", command=self.sauver)
        actions_menu.add_command(label="Save in XML", command=self.sauverXML)

        actions_menu.add_command(label="Clear", command=self.clear)
        actions_menu.add_command(label="Open Editor", command=self.openEditeur)

        # Ajouter le menu déroulant à la barre de menus
        menubar.add_cascade(label="File", menu=actions_menu)

        # Afficher la barre de menus
        root.config(menu=menubar)

        # 1. Créez un nouveau menu déroulant pour "Outils"
        tools_menu = tk.Menu(menubar, tearoff=0)

        # 2. Ajoutez un menuitem "Activer Gomme" avec la fonction `add_checkbutton()`
        # 4. Créez une variable tkinter `BooleanVar` pour suivre l'état de la gomme (activée ou désactivée)
        gomme_active = tk.BooleanVar()
        tools_menu.add_checkbutton(label="Activer Gomme", variable=self.gomme_active, command=self.toggle_gomme)

        # 3. Ajoutez le menu déroulant "Outils" à la barre de menus
        menubar.add_cascade(label="Outils", menu=tools_menu)

        # Créer le menu contextuel
        self.context_menu = tk.Menu(root, tearoff=0)
        self.context_menu.add_command(label="Add", command=lambda: self.ajouter(self.clicked_label))
        self.context_menu.add_command(label="Modify", command=lambda: self.modifier(self.clicked_label))
        self.context_menu.add_command(label="Delete", command=lambda: self.supprimer(self.clicked_label))

        self.context_menu.add_command(label="Add a blank line below",
                                      command=lambda: self.ajouterligneblanche(self.clicked_label))

    def toggle_gomme(self):
        if self.gomme_active.get():
            print("gomme activé")
            pass
        else:
            print("gomme désactivé")
            # Désactivez la gomme ici
            pass

    def gomme(self, event):
        if self.gomme_active.get():
            # Taille de la gomme
            gomme_taille = 10

            # Dessinez un rectangle blanc sur le canvas
            canvas2.create_rectangle(event.x - gomme_taille / 2,
                                          event.y - gomme_taille / 2,
                                          event.x + gomme_taille / 2,
                                          event.y + gomme_taille / 2,
                                          fill="white",
                                          outline="white")


    def display_cursor_position(self, event):
        x = canvas2.canvasx(event.x)
        y = canvas2.canvasy(event.y)
        position_text = f"({x}, {y})"

        # Supprimer le texte précédent (s'il existe)
        canvas2.delete('position_text')

        # Afficher la position du curseur à côté de la souris
        canvas2.create_text(
            x + 10, y + 10, text=position_text,
            anchor='nw', tags='position_text', font=('Arial', 12, 'bold')
        )

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
    def sauverXML(self):
        commandes = [label.cget("text") for label in self.liste_historique]
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

    def pan_start(self, event):
        canvas2.scan_mark(event.x, event.y)

    def pan_move(self, event):
        x = int(canvas2.canvasx(event.x))
        y = int(canvas2.canvasy(event.y))
        canvas2.scan_dragto(x, y, gain=1)

    def pan_end(self, event):
        canvas2.config(cursor="")

    def show_zoom_menu(self, event):
        context_menu = tk.Menu(canvas2, tearoff=0)
        context_menu.add_command(label="Zoom In", command=lambda: self.zoom(event.x, event.y, self.zoom_increment))
        context_menu.add_command(label="Zoom Out", command=lambda: self.zoom(event.x, event.y, -self.zoom_increment))
        context_menu.post(event.x_root, event.y_root)

    def zoom(self, x, y, increment):
        self.zoom_scale += increment
        self.zoom_scale = max(0.1, self.zoom_scale)
        canvas2.scale('all', x, y, 1 + increment, 1 + increment)

    def show_context_menu(self, event):
        # Afficher le menu contextuel à la position du curseur
        self.context_menu.post(event.x_root, event.y_root)
        self.clicked_label = event.widget

    def ajouter_repete_labels(self, num_repeats, clicked_label):
        # Trouver l'index du label sélectionné dans la liste_historique
        label_index = self.liste_historique.index(clicked_label)

        # Créer les labels REPETE, {, lignes vides et }
        repete_label = tk.Label(clicked_label.master, text=f"REPETE {num_repeats}", bg="white", borderwidth=1,
                                relief="solid", width=20)
        open_brace_label = tk.Label(clicked_label.master, text="{", bg="white", borderwidth=1, relief="solid", width=20)
        empty_labels = [tk.Label(clicked_label.master, text="", bg="white", borderwidth=1, relief="solid", width=20) for
                        _ in range(num_repeats)]
        close_brace_label = tk.Label(clicked_label.master, text="}", bg="white", borderwidth=1, relief="solid",
                                     width=20)

        # Insérer les labels dans la liste_historique en dessous du label sélectionné
        insert_index = label_index + 2
        self.liste_historique.insert(insert_index, repete_label)
        self.liste_historique.insert(insert_index + 2, open_brace_label)
        for i, empty_label in enumerate(empty_labels):
            self.liste_historique.insert(insert_index + 3 + i, empty_label)
        self.liste_historique.insert(insert_index + 3 + num_repeats, close_brace_label)

        # Mettre à jour les positions des labels existants
        for i, hist_label in enumerate(self.liste_historique):
            hist_label.grid(row=i + 2, column=1, sticky="nsew")

        # Associer le clic droit au menu contextuel pour les nouveaux labels
        repete_label.bind("<Button-3>", self.show_context_menu)
        open_brace_label.bind("<Button-3>", self.show_context_menu)
        for empty_label in empty_labels:
            empty_label.bind("<Button-3>", self.show_context_menu)
        close_brace_label.bind("<Button-3>", self.show_context_menu)

    def ajouter(self, label):
        # Trouver l'index du label sélectionné dans la liste_historique
        label_index = self.liste_historique.index(label)

        dialog = CustomDialog(root, "Ajouter un nouvel élément", self.items, self)
        if dialog.result:
            new_label_text, params = dialog.result

            new_label = tk.Label(label.master, text=new_label_text, bg="white", borderwidth=1, relief="solid", width=20)

            # Insérer le nouveau label dans la liste_historique au-dessus du label sélectionné
            self.liste_historique.insert(label_index, new_label)

            # Mettre à jour les positions des labels existants
            for i, hist_label in enumerate(self.liste_historique):
                hist_label.grid(row=i + 2, column=1, sticky="nsew")

            # Associer le clic droit au menu contextuel pour le nouveau label
            new_label.bind("<Button-3>", self.show_context_menu)

    def ajouterligneblanche(self, label):
        # Trouver l'index du label sélectionné dans la liste_historique
        label_index = self.liste_historique.index(label)

        new_label = tk.Label(label.master, text="", bg="white", borderwidth=1, relief="solid", width=20)

        # Insérer le nouveau label dans la liste_historique au-dessus du label sélectionné
        self.liste_historique.insert(label_index + 1, new_label)

        # Mettre à jour les positions des labels existants
        for i, hist_label in enumerate(self.liste_historique):
            hist_label.grid(row=i + 2, column=1, sticky="nsew")

        # Associer le clic droit au menu contextuel pour le nouveau label
        new_label.bind("<Button-3>", self.show_context_menu)

    def modifier(self, label):
        # Demander le nouveau texte à l'utilisateur

        dialog = CustomDialog(root, "Ajouter un nouvel élément", self.items, self)
        if dialog.result:
            new_label_text, params = dialog.result
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

    def avancer(self, agent, value, ajouterCommande=True, ajouterHistorique=True):
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
            print(str("l'angle vaut: " + str(angle_degrees)))
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
        canvas2.create_line(self.x, self.y, x2, y2, fill=self.couleur, tags='all')

        print("couleur " + self.couleur)
        self.x = x2
        self.y = y2

        if ajouterHistorique:
            self.nombreCommande += 1
            label = tk.Label(history_frame, text="AVANCE " + str(value), bg="white", borderwidth=1, relief="solid",
                             width=20)
            label.grid(row=self.nombreCommande + 1, column=1, sticky="nsew")
            label.bind("<Button-3>", self.show_context_menu)
            self.liste_historique.append(label)
            history_frame.update()  # Mettre à jour l'affichage pour montrer le changement de couleur
            history_frame.update_idletasks()
            history_canvas.config(scrollregion=history_canvas.bbox("all"))

        if ajouterCommande:
            self.commands.append(("AVANCE", value))

    def reculer(self, agent, value, ajouterCommande=True, ajouterHistorique=True):
        value = int(value)
        self.avancer(self, -value, False)
        self.commands.append(("RECULE", value))
        if ajouterHistorique:
            self.nombreCommande += 1
            label = tk.Label(history_frame, text="RECULE " + str(value), bg="white", borderwidth=1, relief="solid",
                             width=20)
            label.grid(row=self.nombreCommande + 1, column=1, sticky="nsew")
            label.bind("<Button-3>", self.show_context_menu)
            self.liste_historique.append(label)
            history_frame.update()  # Mettre à jour l'affichage pour montrer le changement de couleur
            # Mettre à jour la zone de défilement
            history_frame.update_idletasks()
            history_canvas.config(scrollregion=history_canvas.bbox("all"))

    def tournerDroite(self, agent, value, ajouterHistorique=True):
        self.angle -= int(value)
        self.commands.append(("TOURNEDROITE", value))
        if ajouterHistorique:
            self.nombreCommande += 1
            label = tk.Label(history_frame, text="TOURNEDROITE " + str(value), bg="white", borderwidth=1,
                             relief="solid", width=20)
            label.grid(row=self.nombreCommande + 1, column=1, sticky="nsew")
            label.bind("<Button-3>", self.show_context_menu)
            self.liste_historique.append(label)
            history_frame.update()  # Mettre à jour l'affichage pour montrer le changement de couleur
            # Mettre à jour la zone de défilement
            history_frame.update_idletasks()
            history_canvas.config(scrollregion=history_canvas.bbox("all"))

    def tournerGauche(self, agent, value, ajouterHistorique=True):
        self.angle += int(value)
        self.commands.append(("TOURNEGAUCHE", value))
        if ajouterHistorique:
            self.nombreCommande += 1
            label = tk.Label(history_frame, text="TOURNEGAUCHE " + str(value), bg="white", borderwidth=1,
                             relief="solid", width=20)
            label.grid(row=self.nombreCommande + 1, column=1, sticky="nsew")
            label.bind("<Button-3>", self.show_context_menu)
            self.liste_historique.append(label)
            history_frame.update()  # Mettre à jour l'affichage pour montrer le changement de couleur
            # Mettre à jour la zone de défilement
            history_frame.update_idletasks()
            history_canvas.config(scrollregion=history_canvas.bbox("all"))

    def leverCrayon(self, agent, ajouterHistorique=True):
        self.penActivated = False
        self.commands.append("LEVECRAYON")
        if ajouterHistorique:
            self.nombreCommande += 1
            label = tk.Label(history_frame, text="LEVECRAYON", bg="white", borderwidth=1, relief="solid", width=20)
            label.grid(row=self.nombreCommande + 1, column=1, sticky="nsew")
            label.bind("<Button-3>", self.show_context_menu)
            self.liste_historique.append(label)
            history_frame.update()  # Mettre à jour l'affichage pour montrer le changement de couleur
            # Mettre à jour la zone de défilement
            history_frame.update_idletasks()
            history_canvas.config(scrollregion=history_canvas.bbox("all"))

    def baisserCrayon(self, agent, ajouterHistorique=True):
        self.penActivated = True
        self.commands.append("BAISSECRAYON")
        if ajouterHistorique:
            self.nombreCommande += 1
            label = tk.Label(history_frame, text="BAISSECRAYON ", bg="white", borderwidth=1, relief="solid", width=20)
            label.grid(row=self.nombreCommande + 1, column=1, sticky="nsew")
            label.bind("<Button-3>", self.show_context_menu)
            self.liste_historique.append(label)
            history_frame.update()  # Mettre à jour l'affichage pour montrer le changement de couleur
            # Mettre à jour la zone de défilement
            history_frame.update_idletasks()
            history_canvas.config(scrollregion=history_canvas.bbox("all"))

    def origine(self, agent, ajouterHistorique=True):
        self.x, self.y = self.xBase, self.yBase
        self.angle = 90
        self.commands.append("ORIGINE")
        if ajouterHistorique:
            self.nombreCommande += 1
            label = tk.Label(history_frame, text="ORIGINE", bg="white", borderwidth=1, relief="solid", width=20)
            label.grid(row=self.nombreCommande + 1, column=1, sticky="nsew")
            label.bind("<Button-3>", self.show_context_menu)
            self.liste_historique.append(label)
            history_frame.update()  # Mettre à jour l'affichage pour montrer le changement de couleur
            # Mettre à jour la zone de défilement
            history_frame.update_idletasks()
            history_canvas.config(scrollregion=history_canvas.bbox("all"))

    def restaurer(self, agent, ajouterHistorique=True):
        self.x = self.xBase
        self.y = self.yBase
        self.commands.append("RESTAURER")
        if ajouterHistorique:
            self.nombreCommande += 1
            label = tk.Label(history_frame, text="RESTAURER", bg="white", borderwidth=1, relief="solid", width=20)
            label.grid(row=self.nombreCommande + 1, column=1, sticky="nsew")
            label.bind("<Button-3>", self.show_context_menu)
            self.liste_historique.append(label)
            history_frame.update()  # Mettre à jour l'affichage pour montrer le changement de couleur
            # Mettre à jour la zone de défilement
            history_frame.update_idletasks()
            history_canvas.config(scrollregion=history_canvas.bbox("all"))

    def nettoyer(self, agent, ajouterHistorique=True):
        canvas2.delete("all")
        #  tortue.origine(self)
        self.commands.append("NETTOYER")

        if ajouterHistorique:
            self.nombreCommande += 1
            label = tk.Label(history_frame, text="NETTOYER", bg="white", borderwidth=1, relief="solid", width=20)
            label.grid(row=self.nombreCommande + 1, column=1, sticky="nsew")
            label.bind("<Button-3>", self.show_context_menu)
            self.liste_historique.append(label)
            history_frame.update()  # Mettre à jour l'affichage pour montrer le changement de couleur
            # Mettre à jour la zone de défilement
            history_frame.update_idletasks()
            history_canvas.config(scrollregion=history_canvas.bbox("all"))

    def nettoyerDessin(self):
        self.x = self.xBase
        self.y = self.yBase
        self.penActivated = True
        self.angle = 90
        canvas2.delete("all")

    def clear(self):
        canvas2.delete("all")
        for label in self.liste_historique:
            label.destroy()
        self.liste_historique = []
        self.x, self.y = self.xBase, self.yBase
        self.angle = 90
        self.commands.append("ORIGINE")

    def changerCouleur(self, agent, r, v, b, ajouterHistorique=True):
        r, v, b = int(r), int(v), int(b)  # Convertir les chaînes de caractères en entiers
        # code pour changer la couleur du crayon à partir des composantes r v b
        hex_code = '#{0:02X}{1:02X}{2:02X}'.format(r, v, b)
        self.couleur = hex_code
        print("changer couleur en :" + hex_code)
        if ajouterHistorique:
            self.nombreCommande += 1
            label = tk.Label(history_frame, text="FCC " + str(r) + " " + str(v) + " " + str(b), bg="white",
                             borderwidth=1, relief="solid", width=20)
            label.grid(row=self.nombreCommande + 1, column=1, sticky="nsew")
            label.bind("<Button-3>", self.show_context_menu)
            self.liste_historique.append(label)
            history_frame.update()  # Mettre à jour l'affichage pour montrer le changement de couleur
            # Mettre à jour la zone de défilement
            history_frame.update_idletasks()
            history_canvas.config(scrollregion=history_canvas.bbox("all"))

    # code pour fixer le cap de la tortue de manière absolue
    def fixerCap(self, agent, x, ajouterHistorique=True):
        self.cap = float(x)
        if self.capFixed:
            self.capFixed = False
        else:
            self.capFixed = True
        if ajouterHistorique:
            self.nombreCommande += 1
            label = tk.Label(history_frame, text="FCAP " + str(x), bg="white", borderwidth=1, relief="solid", width=20)
            label.grid(row=self.nombreCommande + 1, column=1, sticky="nsew")
            label.bind("<Button-3>", self.show_context_menu)
            self.liste_historique.append(label)
            history_frame.update()  # Mettre à jour l'affichage pour montrer le changement de couleur
            # Mettre à jour la zone de défilement
            history_frame.update_idletasks()
            history_canvas.config(scrollregion=history_canvas.bbox("all"))

    def setPosition(self, agent, x, y, ajouterHistorique=True):
        self.x, self.y = int(x), int(y)
        if ajouterHistorique:
            self.nombreCommande += 1
            label = tk.Label(history_frame, text="FPOS [" + str(x) + " " + str(y) + "]", bg="white", borderwidth=1,
                             relief="solid", width=20)
            label.grid(row=self.nombreCommande + 1, column=1, sticky="nsew")
            label.bind("<Button-3>", self.show_context_menu)
            self.liste_historique.append(label)
            history_frame.update()  # Mettre à jour l'affichage pour montrer le changement de couleur
            # Mettre à jour la zone de défilement
            history_frame.update_idletasks()
            history_canvas.config(scrollregion=history_canvas.bbox("all"))

    def commande_label(self):
        liste_commandes = [label.cget("text") for label in self.liste_historique]
        for i, label_text in enumerate(liste_commandes):
            label = self.liste_historique[i]  # Récupérer le label correspondant
            label.config(bg="yellow")  # Mettre en évidence le label en jaune
            history_frame.update()  # Mettre à jour l'affichage pour montrer le changement de couleur
            if label_text.split(" ")[0] == "AVANCE":
                self.avancer(False, label_text.split(" ")[1], False, False)
            if label_text.split(" ")[0] == "RECULE":
                self.reculer(False, label_text.split(" ")[1], False, False)
            if label_text.split(" ")[0] == "TOURNEDROITE":
                self.tournerDroite(False, label_text.split(" ")[1], False)
            if label_text.split(" ")[0] == "TOURNEGAUCHE":
                self.tournerGauche(False, label_text.split(" ")[1], False)
            if label_text.split(" ")[0] == "LEVECRAYON":
                self.leverCrayon(False, False)
            if label_text.split(" ")[0] == "BAISSECRAYON":
                self.baisserCrayon(False, False)
            if label_text.split(" ")[0] == "ORIGINE":
                self.origine(False, False)
            if label_text.split(" ")[0] == "RESTAURE":
                self.restaurer(False, False)
            if label_text.split(" ")[0] == "NETTOIE":
                self.nettoyer(False, False)
            if label_text.split(" ")[0] == "FCC":
                self.changerCouleur(False, label_text.split(" ")[1], label_text.split(" ")[2], label_text.split(" ")[3],
                                    False)
            if label_text.split(" ")[0] == "FCAP":
                self.fixerCap(False, label_text.split(" ")[1], False)
            if label_text.split(" ")[0] == "FPOS":
                coords = label_text.split("[")[1].split("]")[0].split()
                x, y = coords[0], coords[1]
                self.setPosition(False, x, y, False)
            time.sleep(self.sleep_time.get())
            label.config(bg="White")  # Restaurer la couleur d'arrière-plan d'origine
            history_frame.update()  # Mettre à jour l'affichage pour montrer le changement de couleur

    def jouer(self):
        print("Lancement de jouer")
        self.nettoyerDessin()
        thread = threading.Thread(target=lambda: self.commande_label())
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
            label = tk.Label(history_frame, text=i, bg="white", borderwidth=1, relief="solid", width=20)
            self.nombreCommande += 1
            label.grid(row=self.nombreCommande + 1, column=1, sticky="nsew")
            label.bind("<Button-3>", self.show_context_menu)

            self.liste_historique.append(label)
            # Mettre à jour la zone de défilement
            history_frame.update_idletasks()
            history_canvas.config(scrollregion=history_canvas.bbox("all"))

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
        file_path = "editeur.py"
        # Lancer le programme en utilisant subprocess
        subprocess.run(["python3", file_path])

    def openEditeur(self):
        # Créer un nouveau thread pour exécuter le programme
        new_thread = threading.Thread(target=self.run_main_program)

        # Démarrer le nouveau thread
        new_thread.start()


# Lancement de root
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

# Création d'un frame conteneur pour le right_panel
container_frame = tk.Frame(root, width=200)
container_frame.pack(side=tk.LEFT, anchor="e", padx=10, pady=10, fill="y")

# Création d'un frame pour les boutons, la zone de saisie et l'historique
right_panel = tk.Frame(container_frame)
right_panel.pack(fill="both", expand=True)
right_panel.columnconfigure(0, weight=1)
right_panel.rowconfigure(1, weight=1)



# Création d'un frame pour les boutons, la zone de saisie et l'historique
south_panel = tk.Frame(root)
south_panel.pack(side=tk.BOTTOM, anchor="s", padx=10, pady=10)

canvas2 = tk.Canvas(root, bg='white')
canvas2.pack(fill=tk.BOTH, expand=True)

canvas2.bind('<Button-3>', tortue.show_zoom_menu)
canvas2.bind('<ButtonPress-2>', tortue.pan_start)
canvas2.bind('<B2-Motion>', tortue.pan_move)
canvas2.bind('<ButtonRelease-2>', tortue.pan_end)
canvas2.bind('<Button-1>', tortue.display_cursor_position)
canvas2.bind('<B1-Motion>', tortue.gomme)

# Création d'un frame pour l'historique
history_frame = tk.Frame(right_panel)
history_frame.grid(row=1, column=1)

# Création d'un canvas pour l'historique
history_canvas = tk.Canvas(right_panel)
history_canvas.grid(row=1, column=0, sticky="nsew")

# Ajouter une scrollbar
scrollbar = tk.Scrollbar(right_panel, orient="vertical", command=history_canvas.yview)
scrollbar.grid(row=1, column=1, sticky="ns")
history_canvas.configure(yscrollcommand=scrollbar.set)

# Création d'un frame interne pour contenir les éléments de l'historique
history_frame = tk.Frame(history_canvas)
history_canvas.create_window((0, 0), window=history_frame)

# Configurez la grille de right_panel pour qu'elle s'étende correctement
right_panel.columnconfigure(0, weight=1)
right_panel.rowconfigure(1, weight=1)


# Mise à jour de la taille du canvas en fonction de la taille du history_frame
def update_scrollregion(event):
    history_canvas.configure(scrollregion=history_canvas.bbox("all"))


history_frame.bind("<Configure>", update_scrollregion)

# Création d'un bouton "play"
play_button = tk.Button(south_panel, text="Replay", command=lambda: tortue.jouer(), width=20)
play_button.pack()

# Création d'un bouton "Clear"
clear_button = tk.Button(south_panel, text="Clear", command=lambda: tortue.clear(), width=20)
clear_button.pack()

# Slideur
tortue.sleep_time = tk.DoubleVar()
tortue.sleep_time.set(1.0)  # Valeur initiale du délai en secondes
slider = tk.Scale(south_panel, from_=0.1, to=5.0, resolution=0.1, orient=tk.HORIZONTAL,
                  label="Pause Time (s)", variable=tortue.sleep_time,
                  length=150, sliderlength=20)
slider.pack()

# Boucle principale de tkinter pour afficher le visualisateur
root.mainloop()
