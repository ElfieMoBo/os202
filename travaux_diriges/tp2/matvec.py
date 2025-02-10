# Produit matrice-vecteur v = A.u
import numpy as np
import time

# With MPI:
from mpi4py import MPI
globCom = MPI.COMM_WORLD.Dup()
nbp     = globCom.size
rank    = globCom.rank
name    = MPI.Get_processor_name()

# Dimension du problème (divisible par 2, 3 et 4)
dim = 120

# Méthode utilisée pour le problème
methode = "ligne"

if methode == "colonne" :
    begin = time.time()
    # Initialisation de la matrice et du vecteur u
    A = None
    u = None
    if rank == 0: 
        A = np.array([[(i+j) % dim+1. for i in range(dim)] for j in range(dim)])
        print(f"A = {A}")
        u = np.array([i+1. for i in range(dim)])
        print(f"u = {u}")

    partial_A = np.empty((int(dim),int(dim/nbp)), dtype='d')
    partial_u = np.empty(int(dim/nbp), dtype='d')

    # Envoie des colonnes de la matrice
    globCom.Scatter(A, [partial_A, MPI.DOUBLE], root=0)
    globCom.Scatter(u, [partial_u, MPI.DOUBLE], root=0)
    partial_v = partial_A.dot(partial_u)
    # Preparation du vecteur v (en eniter)
    v = np.empty(dim, dtype='d')

    # Création du vecteur v en sommant tous les petits vecteurs v
    globCom.Allreduce(partial_v, v, MPI.SUM)
    end = time.time()

elif methode == "ligne":
    begin = time.time()
    # Initialisation de la matrice et du vecteur u
    A = None
    u = np.empty(int(dim), dtype='d')
    if rank == 0: 
        A = np.array([[(i+j) % dim+1. for i in range(dim)] for j in range(dim)])
        print(f"A = {A}")
        u = np.array([i+1. for i in range(dim)])
        print(f"u = {u}")

    partial_A = np.empty((int(dim/nbp),int(dim)), dtype='d')

    # Envoie des colonnes de la matrice
    globCom.Scatter(A, [partial_A, MPI.DOUBLE], root=0)
    globCom.Bcast(u, root=0)
    partial_v = partial_A.dot(u)

    # Preparation du vecteur v (en eniter)
    v = np.empty(dim, dtype='d')

    # Création du vecteur v en concatenant tous les petits vecteurs v
    globCom.Allgather(partial_v, v)
    end = time.time()

if rank == 0:
    print(f"v = {v}")
    print(f"time : {(end-begin)*1000}s")