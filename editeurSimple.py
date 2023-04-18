import tkinter as tk
import subprocess
import threading
import queue

root = tk.Tk()
root.geometry("210x20")  # Largeur x Hauteur en pixels
root.title("Editeur Simple")

commands_queue = queue.Queue()


def command_sender():
    while True:
        command = commands_queue.get()
        process.stdin.write(command + '\n')
        process.stdin.flush()
        commands_queue.task_done()


def run_command():
    command = command_text.get()
    commands_queue.put(command)
    command_text.config(state=tk.NORMAL)


def on_enter_key(event):
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