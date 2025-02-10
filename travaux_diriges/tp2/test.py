import numpy as np

# # # With MPI:
# from mpi4py import MPI

# globCom = MPI.COMM_WORLD.Dup()
# nbp     = globCom.size
# rank    = globCom.rank

# N = 12
# data = None
# if rank==0 :
#     data = [x for x in range(N)]
#     print(f"scattering : {data}")

# partial_data = np.empty(int(N/nbp), dtype='d')
# globCom.Scatter(data, partial_data, root=0)

# print(f"received {partial_data} ({rank})")

# import libraries
from mpi4py import MPI
import numpy as np

# set up MPI world
comm = MPI.COMM_WORLD
size = comm.Get_size() # new: gives number of ranks in comm
rank = comm.Get_rank()

# generate a large array of data on RANK_0
numData = 12
data = None
if rank == 0:
    data = np.array([(x+1)/2 for x in range(numData)])
    print(data)

# initialize empty arrays to receive the partial data
partial = np.empty(int(numData/(2*size)), dtype='d')
print(f"begin with {partial}")
# send data to the other workers
comm.Scatter(data, [partial, MPI.DOUBLE], root=0)

print(f"end with {partial}")
# prepare the reduced array to receive the processed data
# reduced = None
# if rank == 0:
#     reduced = np.empty(size, dtype='d')

# # Average the partial arrays, and then gather them to RANK_0
# comm.Reduce(np.average(partial), reduced, root=0)

# if rank == 0:
#     print('Full Average:',np.average(reduced))