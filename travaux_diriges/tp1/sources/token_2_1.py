import numpy as np
from mpi4py import MPI

globCom = MPI.COMM_WORLD.Dup()
nbp     = globCom.size
rank    = globCom.rank
name    = MPI.Get_processor_name()

if(rank==0):
    token = 1
    globCom.send(token, dest = 1)
    token = globCom.recv(source = nbp-1)
    print(f"token received by {nbp-1} is {token} (message from {rank})")
elif(rank > 0 and rank < nbp-1):
    token = globCom.recv(source = rank-1) + 1
    globCom.send(token, dest = rank+1)
else:
    token = globCom.recv(source = nbp-1-1) + 1
    globCom.send(token, dest = 0)
    
