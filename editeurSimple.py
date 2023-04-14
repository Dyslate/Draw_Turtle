import tkinter as tk
import subprocess
import threading

root = tk.Tk()
root.geometry("210x20")  # Largeur x Hauteur en pixels

root.title("Editeur Simple")


def run_command():
    command = command_text.get()
    #  terminal.insert(tk.END, f'{command}\n')
    process.stdin.write(command + '\n')
    process.stdin.flush()
    command_text.config(state=tk.NORMAL)


# Création d'une zone de saisie pour les commandes
command_text = tk.Entry(root, width=25)


# Lier la touche "Enter" à la fonction on_enter_key
def on_enter_key(event):
    command_text.config(state=tk.DISABLED)
    print("Envoyer : "+str(command_text.get()))

    thread = threading.Thread(target=run_command)
    thread.start()


command_text.bind("<Return>", on_enter_key)
command_text.pack()

# output_thread = threading.Thread(target=read_output)
# #output_thread.start()

# Exécuter python ivyprobe.py en utilisant subprocess
process = subprocess.Popen(['python3', 'ivyprobe.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, text=True)

root.mainloop()
