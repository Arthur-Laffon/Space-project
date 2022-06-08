#!/usr/bin/python3
#----Projet NSI de Arthur, Noé et Léa : Simulateur Orbital 

from importlib import import_module
import tkinter as tk
from math import sqrt, asin, acos, sin, cos, pi
import os
import argparse
from PIL import Image

parser = argparse.ArgumentParser()
parser.add_argument("dt", type = float, help = "temps entre deux executions du prg, le diminuer ralenti la simulation, mais la rend plus précise")
parser.add_argument("r", type = int, help = "rayon des planetes sur le canvass")
parser.add_argument("plns", nargs = '+', type = float, help = "liste de coordonnées des planetes, écrire en forme ae+b")


args = parser.parse_args()
if args.dt : 
    dt = args.dt
if args.plns : 
    p = args.plns
print(p)
plns = []
for i in range (round(len(p)/8)) : 
    print(i)
    plns.append([])
    plns[i].append(float(p[i*8]))
    plns[i].append(tuple((int(p[i*8+1]), int(p[i*8+2]), int(p[i*8+3]))))
    plns[i].append(tuple((int(p[i*8+4]), int(p[i*8+5]), int(p[i*8+6]))))
    plns[i].append(int(p[i*8+7]))
print(plns)



#constante gravitationelle
G = 6.6743/10**6

def _create_circle(self, x, y, r, **kwargs):
    """fonction cercle pour les chemins des planetes"""
    return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)
tk.Canvas.create_circle = _create_circle
# On ouvre une fenêtre 800x800
window = tk.Tk()
window.title("astro.py")
window.geometry("800x800")

# On ajoute à la fenètre un canvas (toile) de dessin.
canvas = tk.Canvas(window, width=8000, height=8000, borderwidth=0,
                   highlightthickness=0, bg="black")
canvas.grid()

def read_images(folder, radius):
    """convertit le dossier dans folder en une liste d'images de côté radius"""
    imgs = []
    for file in os.listdir(folder):
        print(file)
        img = tk.PhotoImage(file=folder+'/'+file)
        print(img)
        imgb = img.subsample(round(400/radius))
        imgs.append(imgb)
    return(imgs)

class planet() : 
    """masse en kg, vitesse : vecteur de n dimensions en km/h, position : vecteur de n dimensions en km"""
    def __init__(self, masse, vitesse, position, img):
        self.masse = masse/10**20
        self.vitesse = (vitesse[0]/3.6/10**4, vitesse[1]/3.6/10**4, vitesse[2]/3.6/10**4)
        self.position = (position[0]/10**6, position[1]/10**6, position[2]/10**6)
        self.energy = 0
        self.img = canvas.create_image(position[0], position[1], anchor = tk.NW, image=img)

def distance (pln1, pln2) : 
    """renvoie la distance entre les planètes pln1 et pln2, et sa décomposition sur les 3 axes"""
    dx = pln1.position[0]-pln2.position[0]
    dy = pln1.position[1]-pln2.position[1]
    dz = pln1.position[-1]-pln2.position[-1]
    d = sqrt(dx**2+dy**2+dz**2)
    return (d, dx, dy, dz)

def rect2sphr (vecteur) : 
    """convertit vecteur rectangulaire en coordonnées sphériques"""
    r = sqrt(vecteur[0]**2+vecteur[1]**2+vecteur[2]**2)
    if r==0 : return [0, 0, 0]
    phi = acos(vecteur[2]/r)
    print(sin(phi))
    theta = acos(vecteur[0]/r/sin(phi))
    return [r, phi, theta]
def sphr2rect (vecteur) : 
    """convertit un vecteur sphérique en coordonnées rectangulaires"""
    x = vecteur[0]*sin(vecteur[1])*cos(vecteur[2])
    y = vecteur[0]*sin(vecteur[1])*sin(vecteur[2])
    z = vecteur[0]*cos(vecteur[1])
    if vecteur[1]==pi/2 : 
        return (x, y, 0)
    else : 
        return (x, y, z)

def Energie_potentielle (planet, planets) : 
    """fait la somme des forces gravitationelles exercées sur planet 
    pour renvoyer son energie potentielle totale"""
    E_poxyz = []
    E_po = [0, 0, 0]
    for pln in planets : 
        if pln.position == planet.position : continue
        E_x = pln.masse*planet.masse*G/distance(planet, pln)[1] if distance(planet, pln)[1]!=0 else 0
        E_y = pln.masse*planet.masse*G/distance(planet, pln)[2] if distance(planet, pln)[2]!=0 else 0
        E_z = pln.masse*planet.masse*G/distance(planet, pln)[3] if distance(planet, pln)[3]!=0 else 0
        E_poxyz.append((E_x, E_y, E_z))
    for i in range(3) : 
        E_po[i] = sum(F[i] for F in E_poxyz)
    E_po = sqrt(E_po[0]**2+E_po[1]**2+E_po[2]**2)
    return E_po

def Energie_cinetique (planet) : 
    """Energie cinétique de la planete"""
    print(planet.vitesse)
    return (planet.vitesse[0]**2+planet.vitesse[1]**2+planet.vitesse[2]**2)*planet.masse/2

def force (planet, force, dt):
    """met à jour la position et la vitesse de la planete après une intervale de temps dt"""
    planet.vitesse = (planet.vitesse[0]+force[0]*dt/planet.masse, planet.vitesse[1]+force[1]*dt/planet.masse, planet.vitesse[2]+force[2]*dt/planet.masse)
    planet.position = (planet.position[0]+planet.vitesse[0]*dt, planet.position[1]+planet.vitesse[1]*dt, planet.position[2]+planet.vitesse[2]*dt)
    #--code pour la gérer l'énergie, incomplet--
    # E_diff = planet.energy-(Energie_potentielle(planet, planets)+Energie_cinetique(planet))
    # v = rect2sphr(planet.vitesse)
    # v[0] = sqrt(2*planet.energy/planet.masse)
    # if E_diff>0 : 
    #     v[0] = sqrt(v[0]**2+E_diff)
    # else : 
    #     v[0] = 2*v[0]-sqrt(v[0]**2+abs(E_diff))
    # v = sphr2rect(v)
    # planet.vitesse = v


def force_totale (planet, planets) : 
    """prend les valeurs d'une planete, et additione la force que les autres exercent sur elle pour 
    renvoyer un seul vecteur"""
    force = (0, 0, 0)
    for pln in planets : 
        if pln.position == planet.position : continue
        d = distance(pln, planet)
        F = G*(planet.masse*pln.masse)/d[0]**2
        #Avec Thalès, on a dx/Fx = dy/Fy = d/F  
        force = (force[0]+F*d[1]/d[0], force[1]+F*d[2]/d[0], force[2]+F*d[3]/d[0])
    return force


#lit les images et les met au rayon 10p
imgs = read_images("img_NSI", r)

#implante les 
for (masse, vitesse, position, nbr_image) in plns : 
    planets.append(planet(masse, vitesse, position, imgs[nbr_image]))

for pln in planets : 
    pln.energy+=Energie_potentielle(pln, planets)

def deplace (pln) : 
    """met à jour la position et la vitesse de la planete pln après une certaine intervalle dt"""
    global dt
    force(pln, force_totale(pln, planets), dt)
    canvas.moveto(pln.img, pln.position[0], pln.position[1])
    #laisse un chemin pour observer l'orbite des planètes
    canvas.create_circle(pln.position[0]+10, pln.position[1]+10, 1, fill = 'white')

def launch (planets) : 
    """boucle applicant la fonction deplace à toutes les planetes"""
    for pln in planets : 
        deplace(pln)
    window.after(1, launch, planets)
window.after(1, launch,planets)
window.mainloop()