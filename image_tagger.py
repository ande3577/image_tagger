import tkinter as tk
from tkinter import simpledialog, messagebox
import tkinter.filedialog as filedialog
import tkinter.ttk as ttk
import json

PEOPLE_FILENAME = "settings.json"

def load_settings():
    global people
    global directory_variable

    people = []
    directory_variable.set("")

    try:
        with open(PEOPLE_FILENAME, mode="r") as f:
            settings = json.load(f)
            try:
                people = settings['people']
            except Exception:
                pass
            try:
                directory_variable.set(settings['directory'])
            except Exception:
                pass
    except Exception as ex:
        pass

def draw_people():
    global people_frame
    global people

    for child in people_frame.winfo_children():
        child.destroy()

    if len(people) == 0:
        ttk.Label(people_frame, text="No people present").grid(row=0,column=0, sticky=[tk.E, tk.W])
    else:
        for i in range(0, len(people)):
            p = people[i]
            name = ttk.Label(people_frame, text=p)
            name.grid(row=i,column=0, sticky=[tk.E, tk.W])
            e = ttk.Button(people_frame, text="Edit", command=lambda p=p, name=name: edit_person_pressed(p))
            e.grid(row=i, column=1, sticky=[tk.E])
            b = ttk.Button(people_frame, text="Delete", command=lambda p=p: delete_person_pressed(p))
            b.grid(row=i, column=2, sticky=[tk.E])

        people_frame.columnconfigure(0, weight=1)

def save_settings():
    global people
    global directory_variable
    try:
        with open(PEOPLE_FILENAME, mode="w") as f:
            settings = dict()
            settings['people'] = people
            settings['directory'] = directory_variable.get()
            json.dump(settings, f)
    except Exception as ex:
        messagebox.showerror("Error", ex)


def edit_person_pressed(p):
    global people

    new_name = simpledialog.askstring("Name", "Enter new name", initialvalue=p)
    if new_name == None:
        return

    new_name = new_name.strip()
    if len(new_name) == 0:
        messagebox.showerror("Error", "Must enter a name!")
        return

    try:
        people[people.index(p)] = new_name
        draw_people()
        save_settings()
    except ValueError:
        messagebox.showerror("Error", "%s not in list of people!" % p)

def delete_person_pressed(p):
    global people

    try:
        people.remove(p)
        draw_people()
        save_settings()
    except ValueError:
        messagebox.showerror("Error", "%s not in list of people!" % p)


def browse_button_pressed():
    global directory_variable
    dir_ = filedialog.askdirectory()
    if dir_ and len(dir_) > 0:
        directory_variable.set(dir_)
        save_settings()

def add_person_button_pressed():
    global people
    name = simpledialog.askstring("Name", "Enter name.")
    if name == None:
        return
    name = name.strip()
    if len(name) == 0:
        messagebox.showerror("Error", "Must enter a name!")
        return

    if name in people:
        messagebox.showerror("Error", "%s already in list!" % name)
        return

    people.append(name)
    draw_people()
    save_settings()

def directory_changed():
    save_settings()

if __name__ == "__main__":
    global people_frame
    global directory_variable

    root = tk.Tk()
    n = ttk.Notebook(root)
    n.columnconfigure(0, weight=1)
    n.grid(sticky=[tk.N, tk.S, tk.W, tk.E])
    f1 = tk.Frame(n)
    ttk.Label(f1, text="Root Directory").grid(row=0,column=0, sticky=tk.W)
    f1.columnconfigure(0, weight=1)
    directory_variable = tk.StringVar()
    directory_variable.trace("u", directory_changed)
    root_directory = ttk.Entry(f1, textvariable=directory_variable)
    root_directory.grid(row=1, column=0, columnspan=2, sticky=[tk.E, tk.W])
    browse_button = ttk.Button(f1, text="Browse", command=browse_button_pressed)
    browse_button.grid(row=1, column=2, sticky=tk.E)
    n.add(f1, text="Settings")
    f2 = tk.Frame(n)
    n.add(f2, text="People")
    people_frame = tk.Frame(f2)
    people_frame.grid(row=0, column=0, sticky=[tk.N, tk.S, tk.W, tk.E])
    load_settings()
    draw_people()
    add_frame = ttk.Frame(f2)
    add_frame.grid(row=1, column=0, sticky=[tk.W, tk.N])
    add_people_button = ttk.Button(add_frame, text="Add", command=add_person_button_pressed)
    add_people_button.pack()

    f2.columnconfigure(0, weight=1)
    f3 = tk.Frame(n)
    n.add(f3, text="Images")
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    root.wm_minsize(400, 300)

    root.mainloop()
