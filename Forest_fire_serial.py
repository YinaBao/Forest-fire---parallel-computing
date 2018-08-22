import sys
import math
import random
import copy
from tqdm import tqdm
import matplotlib.pyplot as plt
import numpy as np

# initialize environment

# number of rows and columns of grid
n_row = 200
n_col = 200
generation = 30
R = 2
p = 0.5
f = 0.01
q = 1-p


# Initial R(0) and S(1)
subGrid = np.random.binomial(1,p,size=n_row*n_col)
subGrid = np.reshape(subGrid,(n_row,n_col))

# Initial B(2)
aa = np.random.binomial(1,f,size=(n_row-2)*(n_col-2))
aa = np.reshape(aa,(n_row-2,n_col-2))
for i in range(n_row-2):
    for j in range(n_col-2):
        if aa[i][j] == 1:
            subGrid[i+1][j+1] = 2


def print_forest(forest):
    for i in range(len(forest)):
        for j in range(len(forest)):
            if forest[i][j] == 0:
                sys.stdout.write("\033[1;34;40m 0\033[0m")  # blue for (R)
            elif forest[i][j] == 1:
                sys.stdout.write("\033[1;32;40m 1\033[0m")  # green for (S)
            elif forest[i][j] == 2:
                sys.stdout.write("\033[1;31;40m 2\033[0m")  # red for burning (B)
            else:
                sys.stdout.write("\033[1;30;40m 3\033[0m")  # black for empty (E)
        sys.stdout.write("\n")


def update_forest(old_forest):
    result_forest=[[1 for i in range(n_col)] for j in range(n_row)]
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
                if (row==1 and col==1) or (row==1 and col==n_col-2) or (row==n_row-2 and col==1) or (row==n_row-2 and col==n_col-2):
                    if neighbour==16:
                        result_forest[row][col] = 3

    return result_forest


# start simulation
new_forest = subGrid

print('Initial')
print_forest(new_forest[1:n_row-1,1:n_col-1])
print()

for i in tqdm(range(generation)):
    new_forest = copy.deepcopy(update_forest(new_forest))
    forest_array = np.array(new_forest)
    print('Generation ',i+1)
    print_forest(forest_array[1:n_row-1,1:n_col-1])
    print()
