import sys
import time
import math
import random
import copy
import itertools

from mpi4py import MPI
comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()
stat = MPI.Status()

try:
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib import cm
    from matplotlib import animation as animation
    visual = True
except:
    visual = False

n_row_total = 200
n_col = 200
generation = 50

R = 2  # at least burning tree number
p = 0.5  # susceptible tree prob
f = 0.01  # lightning strike prob
q = 1-p

n_row = n_row_total // size + 2

if visual:
    fig = plt.figure()



# Initial resistant tree(R-0) and susceptible tree(S-1)
subGrid = np.random.binomial(1,p,size=n_row*n_col)
subGrid = np.reshape(subGrid,(n_row,n_col))

# Initial lightning strike burning tree(B-2)
aa = np.random.binomial(1,f,size=(n_row-2)*(n_col-2))
aa = np.reshape(aa,(n_row-2,n_col-2))
for i in range(n_row-2):
    for j in range(n_col-2):
        if aa[i][j] == 1:
            subGrid[i+1][j+1] = 2


# Parallel
def msg_up(sub_grid):
    # Sends and Receives rows with Rank+1
    comm.send(sub_grid[n_row-2], dest=rank+1)
    sub_grid[n_row-1] = comm.recv(source=rank+1)
    return 0


def msg_down(sub_grid):
    # Sends and Receives rows with Rank-1
    comm.send(sub_grid[1], dest=rank-1)
    sub_grid[0] = comm.recv(source=rank-1)
    return 0


def print_forest(title,forest):
    print (title)
    for i in range(len(forest)):
        for j in range(n_col):
            if not isinstance(title, int):
                sys.stdout.write(str(forest[i][j]))
            elif forest[i][j] == 0:
                sys.stdout.write("\033[1;34;40m 0\033[0m")  # blue for resistant tree (R)
            elif forest[i][j] == 1:
                sys.stdout.write("\033[1;32;40m 1\033[0m")  # green for susceptible tree (S)
            elif forest[i][j] == 2:
                sys.stdout.write("\033[1;31;40m 2\033[0m")  # red for burning tree (B)
            else:
                sys.stdout.write("\033[1;30;40m 3\033[0m")  # black for empty cell (E)
        sys.stdout.write("\n")
    print ()


def calculate_forest(old_forest):
    result_forest=[[3 for i in range(n_col)] for j in range(n_row)]
    result_forest = np.reshape(result_forest,(n_row,n_col))
    for row in range(1, n_row-1):
        for col in range(1, n_col-1):
            if old_forest[row][col] == 1:
                result_forest[row][col] = 1
                counts=0
                for a in (-1,0,1):
                    for b in (-1,0,1):
                        if old_forest[row+a][col+b] == 2:
                            counts+=1
                if counts > 0:
                    result_forest[row][col] = 2

            elif old_forest[row][col] == 0:
                result_forest[row][col] = 0
                count=0
                for a in (-1,0,1):
                    for b in (-1,0,1):
                        if old_forest[row+a][col+b] == 2:
                            count+=1
                if count >= R:
                    result_forest[row][col] = 2

            elif old_forest[row][col] == 3:
                result_forest[row][col] = 3

            elif old_forest[row][col] == 2:
                result_forest[row][col] = 2
                neighbour=0
                for a in (-1,0,1):
                    for b in (-1,0,1):
                        neighbour = neighbour+old_forest[row+a][col+b]
                if (neighbour > 18) or (neighbour==18):
                    result_forest[row][col] = 3
    return result_forest


# Assign sub-forest
sub_forest = subGrid

ims = []
for i in range(generation):
    sub_forest = copy.deepcopy(calculate_forest(sub_forest))
    if rank == 0:
        msg_up(sub_forest)
    elif rank == size - 1:
        msg_down(sub_forest)
    else:
        msg_up(sub_forest)
        msg_down(sub_forest)

    temp_grid = comm.gather(sub_forest[1:n_row - 1], root=0)

    if rank == 0:
        list_forest = list(itertools.chain.from_iterable(temp_grid))
        if visual:
            print(i, "/", generation)
            new_forest = np.vstack(list_forest)
            im = plt.imshow(new_forest, animated=True, interpolation="none", cmap=cm.plasma)
            ims.append([im])
        else:
            time.sleep(1)
            print("Generation: ", i)
            print_forest(i,list_forest)
