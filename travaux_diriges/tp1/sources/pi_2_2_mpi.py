# With MPI:
import numpy as np
import random as rd
import time

from mpi4py import MPI

globCom = MPI.COMM_WORLD.Dup()
nbp     = globCom.size
rank    = globCom.rank
name    = MPI.Get_processor_name()

total_dot = 10000000

rd.seed(rank)
start = time.time()
def random_dot():
    return[rd.uniform(-1.0,1.0), rd.uniform(-1.0,1.0)]

def is_in_cercle(x, y):
    if(x**2 + y**2 <=1):
        return True
    else:
        return False

if(rank==0):
    cercle_dot = 0
    for i in range(total_dot//nbp + total_dot%nbp):
        x, y = random_dot()
        if is_in_cercle(x,y):
            cercle_dot += 1
    for i in range(1,nbp):
        cercle_dot += globCom.recv(source = i)
    r = cercle_dot/total_dot
    pi = 4*r
    print(f"having : pi ~ {pi}")
elif(rank > 0 and rank < nbp):
    cercle_dot = 0
    for i in range(total_dot//nbp):
        x, y = random_dot()
        if is_in_cercle(x,y):
            cercle_dot += 1
    print(f"{rank} sending...")
    globCom.send(cercle_dot, dest = 0)

end = time.time()
print(f"in {end-start:04f}s with {nbp} MPI")