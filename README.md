# crossword
This is a project part of the CS50AI course. I have only written the main algothrim that solves the puzzle which consisits of the functions: enforce_node_consistency(), revise(), ac3(), assignment_complete(), consistent(), order_domain_values(), select_unassigned_variable() and backtrack(). 

The crosssword is a problem that is catagorized under the Constraint Satisfaction problems. These are a class of problems where variables need to be assigned values while satisfying some conditions. The program solves the problem using the following algorgirm: 1- Enforce node consistency 2- Enforce arc consistency 3- assign values to the variables using the Backtrack Search algorithm.

## Usage: 
python generate.py structure words [output]
To use the program you need to provide a structure for the puzzle, and a list of words which there are examples of under the data directory. And optionally, a file to save an image representaion of the solved puzzle.
