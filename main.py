import matplotlib.pyplot as plt
import numpy as np
import time

class Grid:
    def __init__(self):
        self._cells = []
        self._complete_domain = "123456789"
        self._width = 9

    def copy(self):
        copy_grid = Grid()
        copy_grid._cells = [row.copy() for row in self._cells]
        return copy_grid

    def get_cells(self):
        return self._cells

    def get_width(self):
        return self._width

    def read_file(self, string_puzzle):
        i = 0
        row = []
        for p in string_puzzle:
            if p == '.':
                row.append(self._complete_domain)
            else:
                row.append(p)
            i += 1
            if i % self._width == 0:
                self._cells.append(row)
                row = []
            
    def print(self):
        for _ in range(self._width + 4):
            print('-', end=" ")
        print()
        for i in range(self._width):
            print('|', end=" ")
            for j in range(self._width):
                if len(self._cells[i][j]) == 1:
                    print(self._cells[i][j], end=" ")
                elif len(self._cells[i][j]) > 1:
                    print('.', end=" ")
                else:
                    print(';', end=" ")
                if (j + 1) % 3 == 0:
                    print('|', end=" ")
            print()
            if (i + 1) % 3 == 0:
                for _ in range(self._width + 4):
                    print('-', end=" ")
                print()
        print()

    def print_domains(self):
        for row in self._cells:
            print(row)

    def is_solved(self):
        for i in range(self._width):
            for j in range(self._width):
                if len(self._cells[i][j]) > 1 or not self.is_value_consistent(self._cells[i][j], i, j):
                    return False
        return True
    
    def is_value_consistent(self, value, row, column):
        for i in range(self.get_width()):
            if i == column: continue
            if self.get_cells()[row][i] == value:
                return False
        for i in range(self.get_width()):
            if i == row: continue
            if self.get_cells()[i][column] == value:
                return False
        row_init = (row // 3) * 3
        column_init = (column // 3) * 3
        for i in range(row_init, row_init + 3):
            for j in range(column_init, column_init + 3):
                if i == row and j == column:
                    continue
                if self.get_cells()[i][j] == value:
                    return False
        return True

class VarSelector:
    def select_variable(self, grid):
        pass

class FirstAvailable(VarSelector):
    def select_variable(self, grid):
        for i in range(grid.get_width()):
            for j in range(grid.get_width()):
                if len(grid.get_cells()[i][j]) > 1:
                    return(i,j)

class MRV(VarSelector):
    def select_variable(self, grid):
        current_i = None
        current_j = None
        minimum = float('inf')
        for i in range(grid.get_width()):
            for j in range(grid.get_width()):
                if minimum >= len(grid.get_cells()[i][j]) and len(grid.get_cells()[i][j]) > 1:
                    minimum = len(grid.get_cells()[i][j])
                    current_i = i
                    current_j = j
        return(current_i, current_j)

class AC3:
    def remove_domain_row(self, grid, row, column):
        variables_assigned = []
        for j in range(grid.get_width()):
            if j != column:
                new_domain = grid.get_cells()[row][j].replace(grid.get_cells()[row][column], '')
                if len(new_domain) == 0:
                    return None, True
                if len(new_domain) == 1 and len(grid.get_cells()[row][j]) > 1:
                    variables_assigned.append((row, j))
                grid.get_cells()[row][j] = new_domain
        
        return variables_assigned, False

    def remove_domain_column(self, grid, row, column):
        variables_assigned = []
        for j in range(grid.get_width()):
            if j != row:
                new_domain = grid.get_cells()[j][column].replace(grid.get_cells()[row][column], '')
                if len(new_domain) == 0:
                    return None, True
                if len(new_domain) == 1 and len(grid.get_cells()[j][column]) > 1:
                    variables_assigned.append((j, column))
                grid.get_cells()[j][column] = new_domain

        return variables_assigned, False

    def remove_domain_unit(self, grid, row, column):
        variables_assigned = []
        row_init = (row // 3) * 3
        column_init = (column // 3) * 3

        for i in range(row_init, row_init + 3):
            for j in range(column_init, column_init + 3):
                if i == row and j == column:
                    continue
                new_domain = grid.get_cells()[i][j].replace(grid.get_cells()[row][column], '')
                if len(new_domain) == 0:
                    return None, True
                if len(new_domain) == 1 and len(grid.get_cells()[i][j]) > 1:
                    variables_assigned.append((i, j))
                grid.get_cells()[i][j] = new_domain
        return variables_assigned, False

    def pre_process_consistency(self, grid):
        Q = set()
        for i in range(grid.get_width()):
            for j in range(grid.get_width()):
                if len(grid.get_cells()[i][j]) == 1:
                    Q.add((i,j))
        return(self.consistency(grid,Q))
    
    def consistency(self, grid, Q):
        while len(Q) != 0:
            i,j = Q.pop()
            removed_rows, x = self.remove_domain_row(grid,i,j)
            removed_cols, y = self.remove_domain_column(grid,i,j)
            removed_units, z = self.remove_domain_unit(grid,i,j)
            if x or y or z:
                return False
            for assigned_index in removed_rows + removed_cols + removed_units:
                Q.add(assigned_index)
        return grid

class Backtracking:
    def search(self, grid, var_selector, already_preinitialized = None):
        ac3 = AC3()
        if already_preinitialized is None:
            #initialize partially filled sudoku board with AC3 to find possible candidates
            grid = ac3.pre_process_consistency(grid)
            already_preinitialized = True
        if grid.is_solved():
            return grid
        i,j = var_selector.select_variable(grid)
        #backtrack search all possible values for the sudoku board using "var_selector" heuristic (recursive)
        for d in grid.get_cells()[i][j]:
            if grid.is_value_consistent(d, i, j):
                copy_g = grid.copy()
                copy_g._cells[i][j] = str(d)
                current_set = set()
                current_set.add((i,j))
                if ac3.consistency(copy_g,current_set):
                    rb = self.search(copy_g,var_selector, already_preinitialized)
                    if rb:
                        return rb
        return False
    
def main():
    file = open('top95.txt', 'r')
    problems = file.readlines()
    #each line in the file is its' own partially filled Sudoku board
    for p in problems:
        g = Grid()
        g.read_file(p)
        bt = Backtracking()
        try:
            s = time.time()
            mrv_search = bt.search(g, MRV())
            e = time.time()
            print('Inputted board:')
            g.print()
            print(f'Time it took to solve using MRV heuristic: {e-s}')
        except:
            print('A solution does not exist for the following partially filled board:')
            g.print()
            continue
        s = time.time()
        fa_search = bt.search(g,FirstAvailable())
        e = time.time()
        print(f'Time it took to solve using FA heuristic: {e-s}\n')
        print('Solved board (MRV):')
        mrv_search.print()
        print('Solved board (FA):')
        fa_search.print()
    
if __name__ == '__main__':
    main()
