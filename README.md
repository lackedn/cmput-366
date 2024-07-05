Assignment 4 for AI search course: sudoku solver (CSPs). <br /> 
<br />
Algorithm used to solve the partially filled board is called "arc consistency 3". Heuristics used for variable selection in backtracking are "minimum remaining value" and "first available value" (MRV is usually much faster) <br />
<br />
The text file "top95.txt" is used to input all boards to be solved. Each line represents a partially filled board, with 81 characters. The i-th character in each line represents the pre-filled cell on the board at position (i//9,i%9). If there is no number at that position, it instead contains ".", representing values that are to be solved for in the search.
