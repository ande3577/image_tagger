import tkinter as tk
from tkinter import simpledialog, messagebox
import tkinter.filedialog as filedialog
import tkinter.ttk as ttk
import os as os
import json
from PIL import Image, ImageTk
import shutil

PEOPLE_FILENAME = "settings.json"


def load_settings():
    global people
    global directory_variable
    global tagged_members

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
            try:
                tagged_members = settings['tagged_members']
            except Exception:
                tagged_members = dict()
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
            ttk.Button(people_frame, text="Export", command=lambda p=p: export_pressed(p)).grid(row=i, column=2, sticky=[tk.E])
            ttk.Button(people_frame, text="Edit", command=lambda p=p, name=name: edit_person_pressed(p)).grid(row=i, column=3, sticky=[tk.E])
            ttk.Button(people_frame, text="Delete", command=lambda p=p: delete_person_pressed(p)).grid(row=i, column=4, sticky=[tk.E])

        people_frame.columnconfigure(0, weight=1)


def save_settings():
    global people
    global directory_variable
    global tagged_members

    try:
        with open(PEOPLE_FILENAME, mode="w") as f:
            settings = dict()
            settings['people'] = people
            settings['directory'] = directory_variable.get()
            settings['tagged_members'] = tagged_members
            json.dump(settings, f)
    except Exception as ex:
        messagebox.showerror("Error", ex)

def export_pressed(p):
    global tagged_members
    global directory_variable

    output_directory = filedialog.askdirectory()
    if not output_directory or len(output_directory) == 0:
        messagebox.showerror("Error.", "Must enter a directory")
        return

    for image in tagged_members.keys():
        if p in tagged_members[image]:
            input_file = os.path.join(directory_variable.get(), image)
            output_file = os.path.join(output_directory, image)
            print("Copy %s\n\t to %s\n" % (input_file, output_file))
            shutil.copyfile(input_file, output_file)

def edit_person_pressed(p):
    global people
    global tagged_members

    new_name = simpledialog.askstring("Name", "Enter new name", initialvalue=p)
    if new_name == None:
        return

    new_name = new_name.strip()
    if len(new_name) == 0:
        messagebox.showerror("Error", "Must enter a name!")
        return

    try:
        people[people.index(p)] = new_name
        for k in tagged_members.keys():
            tagged_members[k] = [new_name if x == p else x for x in tagged_members[k]]
        draw_people()
        draw_image()
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
        directory_changed()


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
    global tagged_members
    tagged_members = dict()
    save_settings()
    build_image_list()


def build_image_list():
    global directory_variable
    global image_list_box

    image_list_box.delete(0, tk.END)

    image_list = []
    directory = directory_variable.get()
    for root, dir, files in os.walk(directory):
        relative_path = root.replace(directory, "")
        print(relative_path)
        for file in files:
            if file.endswith( ('.png', '.jpg') ):
                relative_filepath = os.path.join(relative_path, file)
                image_list_box.insert(tk.END, relative_filepath)
                image_list.append(relative_filepath)

def draw_image():
    global image_frame
    global photo_image
    global image_list_box
    global directory_variable
    global people
    global tagged_members
    global check_variable

    for child in image_frame.winfo_children():
        child.destroy()

    button_frame = ttk.Frame(image_frame)
    ttk.Button(button_frame, text="Previous", command=previous_button_pressed).grid(row=0,column=0)
    ttk.Button(button_frame, text="Next", command=next_button_pressed).grid(row=0,column=1)
    button_frame.grid(row=0,column=0,sticky=[tk.N])

    directory = directory_variable.get()
    selected_image = image_list_box.get(tk.ACTIVE)
    if directory_variable.get() and len(directory) > 0 and selected_image and len(selected_image) > 0:
        path = os.path.join(directory, selected_image)
        path = path.replace("\\", "/")
        print(path)
        image = Image.open(path)
        image.thumbnail((400, 300), Image.ANTIALIAS)
        photo_image = ImageTk.PhotoImage(image)
        photo_label = tk.Label(image_frame, text="Hello World!", image=photo_image)
        photo_label.grid(row=1,column=0)

        row = 2
        check_variable = dict()
        for p in people:
            try:
                tagged = p in tagged_members[selected_image]
            except:
                tagged = False
            check_variable[p] = tk.BooleanVar()
            check_variable[p].set(tagged)
            check_button = ttk.Checkbutton(image_frame, text=p, variable=check_variable[p], onvalue=True, offvalue=False, command= lambda image=selected_image, person=p: tagged_members_changed(image, person))
            check_button.grid(row=row, column=0, sticky=[tk.W])
            row += 1

def tagged_members_changed(image, person):
    global tagged_members
    global check_variable

    print(image)
    print(person)
    print(check_variable[person].get())

    try:
        tagged_members[image]
    except KeyError:
        tagged_members[image] = []

    if check_variable[person].get() == True:
        if not person in tagged_members[image]:
            tagged_members[image].append(person)
    else:
        try:
            tagged_members[image].remove(person)
        except ValueError:
            pass

    save_settings()


def previous_button_pressed():
    global image_list_box

    i = image_list_box.index(tk.ACTIVE)
    if i > 0:
        i -= 1
    image_list_box.selection_set(i, None)
    draw_image()


def next_button_pressed():
    global image_list_box

    i = image_list_box.index(tk.ACTIVE)
    if i < image_list_box.index(tk.END):
        i += 1
    image_list_box.selection_set(i, None)
    draw_image()



def on_image_select(evt):
    draw_image()


if __name__ == "__main__":
    global people_frame
    global directory_variable
    global image_list_box
    global image_frame
    global tagged_members

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

    image_list_box = tk.Listbox(f3, width=35)
    image_list_box.grid(row=0, column=0, sticky=[tk.W, tk.N, tk.S])
    image_list_box.bind('<<ListboxSelect>>', on_image_select)

    scrollbar = tk.Scrollbar(f3, orient=tk.VERTICAL)
    scrollbar.config(command=image_list_box.yview)
    scrollbar.grid(row=0, column=1, sticky=[tk.W, tk.N, tk.S])
    f3.rowconfigure(0, weight=1)
    build_image_list()

    image_frame = ttk.Frame(f3)
    image_frame.grid(row=0, column=2)
    draw_image()
    f3.columnconfigure(2, weight=1)

    n.add(f3, text="Images")
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    root.wm_minsize(800, 600)

    root.mainloop()
