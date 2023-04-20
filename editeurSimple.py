import tkinter as tk
import subprocess
import threading
import queue

root = tk.Tk()
root.geometry("210x20")  # Largeur x Hauteur en pixels
root.title("Editeur Simple")

commands_queue = queue.Queue()


def command_sender():
    '''
    Les commandes sont envoyées au processus en boucle dans une queue pour optimiser le thread
    '''
    while True:
        command = commands_queue.get()
        process.stdin.write(command + '\n')
        process.stdin.flush()
        commands_queue.task_done()


def run_command():
    '''
    Fonction qui récupère la commande et l'envoie au processus
    '''
    command = command_text.get()
    commands_queue.put(command)
    command_text.config(state=tk.NORMAL)


def on_enter_key(event):
    """
    Fonction qui est appelée quand on appuie sur la touche entrée: appelle run_command

    :param event: evenement de la touche entrée
    """
    command_text.config(state=tk.DISABLED)
    print("Envoyer : "+str(command_text.get()))
    run_command()


command_text = tk.Entry(root, width=25)
command_text.bind("<Return>", on_enter_key)
command_text.pack()

process = subprocess.Popen(['python3', 'ivyprobe.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, text=True)

command_sender_thread = threading.Thread(target=command_sender)
command_sender_thread.daemon = True
command_sender_thread.start()

root.mainloop()