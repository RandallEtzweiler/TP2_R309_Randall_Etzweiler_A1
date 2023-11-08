import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog

root = tk.Tk()
root.title("Réseau Dessin")
root.geometry("800x600")

canvas = tk.Canvas(root, bg='white', width=800, height=600)
canvas.pack(fill=tk.BOTH, expand=True)

# Dictionnaire pour stocker les éléments et leurs ports
network_elements = {}
port_size = 5  # Taille des ports

current_item = None
start_x = 0
start_y = 0
ctrl_held = False  # Variable pour suivre si la touche CTRL est appuyée

def on_key_press(event):
    global ctrl_held
    if event.keysym == 'Control_L':
        ctrl_held = True

def on_key_release(event):
    global ctrl_held
    if event.keysym == 'Control_L':
        ctrl_held = False

def on_drag_start(event):
    global current_item, start_x, start_y
    # Enregistre l'élément en cours et sa position de départ
    current_item = canvas.find_closest(event.x, event.y)[0]
    start_x = event.x
    start_y = event.y

def on_drag_motion(event):
    global current_item, start_x, start_y
    # Calcule le déplacement
    dx = event.x - start_x
    dy = event.y - start_y
    # Déplace l'élément en cours
    canvas.move(current_item, dx, dy)
    # Mise à jour de la position de départ
    start_x = event.x
    start_y = event.y

def delete_item(event, item):
    canvas.delete(item)

def edit_item_properties(event, item):
    new_name = simpledialog.askstring("Edit Name", "Enter new name:", parent=root)
    if new_name:
        # Mise à jour du nom de l'élément
        print(f"Item {item} renamed to: {new_name}")

    # Pour l'icône, on demande à l'utilisateur de choisir un fichier image
    new_icon_path = filedialog.askopenfilename(title="Select Icon",
                                               filetypes=(("PNG files", "*.png"), ("All files", "*.*")))
    if new_icon_path:
        # Mise à jour de l'icône de l'élément
        print(f"Item {item} icon changed to: {new_icon_path}")


def right_click(event, item):
    menu = tk.Menu(root, tearoff=0)
    menu.add_command(label="Modifier les propriétés", command=lambda: edit_item_properties(event, item))
    menu.tk_popup(event.x_root, event.y_root)

def create_network_element(event, element_type):
    item = None
    ports = []

    # Création de l'élément et définition du nombre de ports
    if element_type == 'client':
        item = canvas.create_rectangle(event.x-25, event.y-25, event.x+25, event.y+25, fill='blue')
        ports.append((event.x, event.y))  # Un seul port pour le client
    elif element_type == 'switch':
        item = canvas.create_oval(event.x-25, event.y-25, event.x+25, event.y+25, fill='green')
        # On peut changer le nombre de ports ici pour un switch
        num_ports = 4
    elif element_type == 'router':
        item = canvas.create_polygon(event.x, event.y-30, event.x+30, event.y+20, event.x-30, event.y+20, fill='red')
        # On peut changer le nombre de ports ici pour un routeur
        num_ports = 4

    if element_type in ['switch', 'router']:
        for i in range(num_ports):
            offset = (i - (num_ports - 1) / 2) * 20  # Espacement des ports
            port_x = event.x + offset
            port_y = event.y + (25 if element_type == 'switch' else 20)
            ports.append((port_x, port_y))

    # On dessine les ports sur le canevas
    for port_x, port_y in ports:
        canvas.create_oval(port_x - port_size, port_y - port_size, port_x + port_size, port_y + port_size, fill='black')

    # On ajoute l'élément et ses ports au dictionnaire
    network_elements[item] = ports

    # On attache les fonctions d'événement pour la suppression, etc.
    canvas.tag_bind(item, '<Button-1>', on_drag_start)
    canvas.tag_bind(item, '<B1-Motion>', on_drag_motion)
    canvas.tag_bind(item, '<Double-Button-1>', lambda e, i=item: delete_item(e, i))
    canvas.tag_bind(item, '<Button-3>', lambda e, i=item: right_click(e, i))

def find_closest_port(x, y):
    closest_port = None
    min_distance = float('inf')
    for item_ports in network_elements.values():
        for port_x, port_y in item_ports:
            distance = ((port_x - x) ** 2 + (port_y - y) ** 2) ** 0.5
            if distance < min_distance:
                min_distance = distance
                closest_port = (port_x, port_y)
    return closest_port

# Modification de la fonction draw_link pour utiliser les ports
def draw_link(event):
    global ctrl_held
    x, y = event.x, event.y
    if not hasattr(draw_link, "start"):
        # On trouve le port le plus proche du clic initial
        closest_port = find_closest_port(x, y)
        draw_link.start = closest_port if closest_port else (x, y)
    else:
        # Lorsque la ligne est terminée, on l'a lie au port le plus proche
        closest_port = find_closest_port(x, y)
        end_coords = closest_port if closest_port else (x, y)
        canvas.create_line(draw_link.start, end_coords, fill="black")
        delattr(draw_link, "start")

canvas.bind('<ButtonPress-1>', draw_link)
root.bind('<KeyPress-Control_L>', on_key_press)
root.bind('<KeyRelease-Control_L>', on_key_release)

def create_client(event):
    create_network_element(event, 'client')

def create_switch(event):
    create_network_element(event, 'switch')

def create_router(event):
    create_network_element(event, 'router')

root.bind('c', create_client)
root.bind('s', create_switch)
root.bind('r', create_router)

root.mainloop()