# Without MPI:
import numpy as np
import random as rd
import time

total_dot = total_dot = 1000000000000
cercle_dot = 0

rd.seed()
start = time.time()
def random_dot():
    return[rd.randint(-1,1), rd.randint(-1,1)]

def is_in_cercle(x, y):
    if(x**2 + y**2 <=1):
        return True
    else:
        return False

for i in range(total_dot):
    x, y = random_dot()
    if is_in_cercle(x,y):
        cercle_dot = cercle_dot + 1
r = cercle_dot/total_dot
pi = 4*r
print(f"having : pi ~ {pi}")
end = time.time()
print(f"in {end-start}s without MPI")