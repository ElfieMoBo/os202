# Calcul de l'ensemble de Mandelbrot en python
import numpy as np
from dataclasses import dataclass
from PIL import Image
from math import log
from time import time
import matplotlib.cm
from mpi4py import MPI

global_com = MPI.COMM_WORLD.Dup()
rank       = global_com.rank
nbp        = global_com.size

@dataclass
class MandelbrotSet:
    max_iterations: int
    escape_radius : float = 2.0

    def __contains__(self, c: complex) -> bool:
        return self.stability(c) == 1

    def convergence(self, c:complex, smooth=False, clamp=True) -> float:
        value = self.count_iterations(c,smooth)/self.max_iterations
        return max(0.0, min(value, 1.0)) if clamp else value

    def count_iterations(self, c: complex,  smooth=False) -> int | float :
        z    : complex
        iter : int

        # On vérifie dans un premier temps si le complexe
        # n'appartient pas à une zone de convergence connue :
        #   1. Appartenance aux disques  C0{(0,0),1/4} et C1{(-1,0),1/4}
        if c.real*c.real+c.imag*c.imag < 0.0625 :
            return self.max_iterations
        if (c.real+1)*(c.real+1)+c.imag*c.imag < 0.0625:
            return self.max_iterations
        #  2.  Appartenance à la cardioïde {(1/4,0),1/2(1-cos(theta))}    
        if (c.real > -0.75) and (c.real < 0.5) :
            ct = c.real-0.25 + 1.j * c.imag
            ctnrm2 = abs(ct)
            if ctnrm2 < 0.5*(1-ct.real/max(ctnrm2,1.E-14)):
                return self.max_iterations
        # Sinon on itère 
        z=0
        for iter in range(self.max_iterations):
            z = z*z + c
            if abs(z) > self.escape_radius:
                if smooth:
                    return iter + 1 - log(log(abs(z)))/log(2)
                return iter
        return self.max_iterations

# On peut changer les paramètres des deux prochaines lignes
mandelbrot_set = MandelbrotSet(max_iterations=500,escape_radius=10)
width, height = 1024, 1024

scaleX = 3./width
scaleY = 2.25/height
if rank==0: # Primaire
    deb = time()
    convergence = np.empty((height, width),dtype=np.double)
    ligne = 0
    for iProc in range(1,nbp):
        global_com.ssend(ligne, iProc)
        ligne += 1
    new_ligne = np.empty(width, dtype=np.double)
    stat = MPI.Status()
    while ligne < height:
        global_com.Recv(new_ligne, status=stat)
        req = global_com.isend(ligne, stat.Get_source())
        convergence[stat.Get_tag(),:] = new_ligne[:]
        req.wait(None)
        ligne += 1
    task = -1 # Arrêt de la boucle et des programmes secondaires
    for iProc in range(1,nbp):
        global_com.Recv(new_ligne, status=stat)
        req = global_com.isend(task, stat.Get_source())
        convergence[stat.Get_tag(),:] = new_ligne[:]
        req.wait(None)
    fin = time()
    print(f"Temps du calcul de l'ensemble de Mandelbrot : {fin-deb} for ({rank})")   
    # Constitution de l'image résultante :
    deb=time()
    image = Image.fromarray(np.uint8(matplotlib.cm.plasma(convergence)*255))
    fin = time()
    print(f"Temps de constitution de l'image : {fin-deb}")
    image.show()
else: # Secondaire
    deb = time()
    ligne = 0
    new_ligne = np.empty(width, dtype=np.double)
    while ligne >= 0:
        ligne = global_com.recv(source=0)
        if ligne >= 0:
            for x in range(width):
                c = complex(-2. + scaleX*x, -1.125 + scaleY * ligne)
                new_ligne[x] = mandelbrot_set.convergence(c,smooth=True)
            global_com.Send(new_ligne, 0, ligne)
    fin = time()
    print(f"Temps du calcul de l'ensemble de Mandelbrot : {fin-deb} for ({rank})")   