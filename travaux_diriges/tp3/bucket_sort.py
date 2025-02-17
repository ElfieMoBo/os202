import numpy as np
import random as rd
import statistics as stat
from time import time


# For using MPI
from mpi4py import MPI
globCom = MPI.COMM_WORLD.Dup()
nbp     = globCom.size
rank    = globCom.rank
name    = MPI.Get_processor_name()

# Choosing a size as a multiple of (3x3)x(4x4) = 144
size = 144*100
bound = 1

SENDRECV = 0
GATHER = 1
ALLTOALL = 0

# Random init
rd.seed(time()+rank)

def random_init(array, bound):
    for i in range(len(array)):
        array[i] = rd.random()
    return array

def is_ascending(array):
    for i in range(len(array)-1):
        if array[i] > array[i+1] :
            return False
    return True

# Clock
begin = time()

# Create a buffer for the part array
array_to_sort = None
local_array = np.empty(int(size/nbp), dtype='d')
global_array_sorted = np.empty(size, dtype='d')
temp_array_sorted = np.empty(size, dtype='d')

if(rank==0):
    # Init array with random array
    array_to_sort = np.empty(size, dtype='d')
    array_to_sort = random_init(array_to_sort, bound)

# Sending parts of array
globCom.Scatter(array_to_sort, [local_array, MPI.INT], root=0)

# First sort to calculate upper and lower bound
local_array.sort()
assert is_ascending(local_array)
local_size = len(local_array)
local_bound = stat.quantiles(local_array,n=nbp)
local_bound = np.append(local_bound, bound+1)

# Sending upper and lower bound to everyone
global_bound = np.empty(nbp)
globCom.Allreduce(local_bound, global_bound, MPI.SUM)
global_bound /= nbp
# print(f"bound: {global_bound}")

# Creating buckets with bounded walues 
local_bucket = []
local_array_bounded = []
local_bucket.append(tuple(local_array[local_array <= global_bound[0]]))
local_array_bounded.append(0)
for k in range(1,nbp): # passing from 1 to 0
    local_bucket.append(tuple(local_array[np.logical_and(local_array <= global_bound[k], local_array > global_bound[k-1])]))
    local_array_bounded.append(0)

if SENDRECV :
    # Sending message with send/recv functions (could be long and blocking)
    print(f"sendrecv")
    global_bound = np.insert(global_bound, 0, -1)
    begin_loop = time()
    local_array_rank = np.empty(0)
    for i_ranks in range(nbp):
        if(i_ranks==rank) :
            local_array_rank = np.append(local_array_rank, local_bucket[i_ranks])
        else :
            globCom.send(local_bucket[i_ranks], i_ranks)
            local_array_rank = np.append(local_array_rank, globCom.recv(source = i_ranks))
    local_array_rank.sort()
    end_loop = time()
    temp_array_sorted = globCom.gather(local_array_rank)

if GATHER :
    # Sending buckets with gather to the good root
    print(f"gather")
    begin_loop = time()
    local_array_rank = np.empty(0)
    for i_ranks in range(nbp):
        if(i_ranks==rank) :
            local_array_rank = globCom.gather(local_bucket[i_ranks], root = i_ranks)
        else :
            globCom.gather(local_bucket[i_ranks], root = i_ranks)
    local_array_rank = np.concatenate(local_array_rank, axis=None)
    local_array_rank.sort()
    end_loop = time()
    temp_array_sorted = globCom.gather(local_array_rank)

if ALLTOALL :
    # Sending buckets with Alltoall (that scatter and gather) but issue with scattering np.array (not hashable)
    print(f"{rank}: bou{local_array_bounded}")
    globCom.Alltoall(local_bucket, local_array_bounded)
    local_array_bounded.sort()
    temp_array_sorted = globCom.gather(local_array_bounded)

# Clock
end = time()

# Creating the last array sorted
if rank == 0:
    global_array_sorted = np.concatenate(temp_array_sorted, axis=None)
    assert is_ascending(global_array_sorted)
    print(f"passing from {array_to_sort} to {global_array_sorted} in {(end-begin)*1000}ms")
    print(f"time in loop : {(end_loop-begin_loop)*1000}")

    simple_begin = time()
    array_sorted = array_to_sort.sort()
    simple_end = time()
    print(f"simple sort in {(simple_end-simple_begin)*1000}ms")

