import sys
import copy
from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        domain = copy.deepcopy(self.domains) #because this dict would have some it's items removed and python doesnt allow it
        for var in domain:
            for word in domain[var]:
                if(var.length != len(word)):
                    self.domains[var].remove(word)
                    
    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """

        overlap = self.crossword.overlaps[x,y]
        if(overlap != None):
            xDomain = copy.deepcopy(self.domains[x])
            xIndex = overlap[0]
            yIndex = overlap[1]
            revised = False

            for xWord in xDomain:
                matchFound = False
                for yWord in self.domains[y]:
                    if(xWord == yWord): #the game doesnt allow duplicate words, it will be removed later
                        continue
                    if(xWord[xIndex] == yWord[yIndex]):
                        matchFound = True
                        break

                if(matchFound == False):
                    self.domains[x].remove(xWord)
                    revised = True

            return revised
        
        #if there is no overlaps then no changes need to made for x 
        else:
            return False

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        
        listOfArcs = list()

        if(arcs == None):
            for var in self.crossword.variables:
                neighbors = self.crossword.neighbors(var)
                for neighbor in neighbors:
                    listOfArcs.append((var,neighbor))
        else:
            listOfArcs = arcs

        while listOfArcs:
            currArc = listOfArcs.pop()

            #if a change was made to currArc[0] then add all neighbors of it to the list of arcs besides currArc[1]
            if(self.revise(currArc[0],currArc[1])):
                if(len(self.domains[currArc[0]]) == 0):
                    return False
                neighbors = self.crossword.neighbors(currArc[0]) #if .remove(currArc[1]) is added it doesnt work for some reason
                #if it is none, then currArc[1] was the only neighbor for currArc[0]
                if(neighbors != None):
                    for neighbor in neighbors:
                        listOfArcs.append((neighbor,currArc[0]))

        #if a revise was done to all arcs and no domain is 0 for any variable
        return True   

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        if(len(assignment) != len(self.crossword.variables)): 
            return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """      
        #check unary constraints (lengths matching)
        for var in assignment:
            if var.length != len(assignment[var]):
                return False

        #check for binary constraints (conflicting neighbors) or duplicate values
        for i, val1 in enumerate(assignment):
            # Iterate over the second dictionary starting from the next index
            for val2 in list(assignment.keys())[i + 1:]:
                nodeConsistent = True
                overlap = self.crossword.overlaps[val1,val2]
                if(overlap):
                    val1Index = overlap[0]
                    val2Index = overlap[1]
                    if(assignment[val1][val1Index] != assignment[val2][val2Index]):
                        nodeConsistent = False
                if(not nodeConsistent or assignment[val1] == assignment[val2]): 
                    return False

        return True   
            

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        #give new name to not get confused with the loop
        targetVar = var

        #assign value to a number(initilly 0) that represent how many neighbors choices are affected by assigning that value to the target var
        domainValues = {}
        for value in self.domains[targetVar]:
            domainValues[value] = 0
        neighbors = self.crossword.neighbors(targetVar)

        #take variables that are not in yet assigned and are neighbors of the target value since not neighboring values are not effected directly
        unAssignedNeighboringVars = []
        for var in self.crossword.variables:
            if(var not in assignment and var in neighbors):
                unAssignedNeighboringVars.append(var)

        for value in domainValues:

            #change the domain of targetVar to the value only, then check if a neighbor changes it's domain
            #by saving how many it had before and after the change using the revise function 
            for neighbor in unAssignedNeighboringVars:
                prevDomains = copy.deepcopy(self.domains) #save the current domain of values to return to it later since the revise function changes the original domain
                prevNbOfValues = len(self.domains[neighbor])
                self.domains[targetVar] = {value}

                self.revise(neighbor, targetVar)
                domainValues[value] = domainValues[value] + (prevNbOfValues - len(self.domains[neighbor])) 

                #revert back to the original domain
                self.domains = copy.deepcopy(prevDomains)

            #sort the dict by the it's items (how many neighbors choices are affected by the value)
            domainValues = dict(sorted(domainValues.items(), key=lambda item: item[1]))

            #return the values only without the number
            domainValues = list(domainValues.keys())
            return domainValues

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        minVar = None
        minNbOfValues = float('inf')

        for var in self.crossword.variables:
            if(var not in assignment):
                nbOfValues = len(self.domains[var])
                if(nbOfValues <= minNbOfValues):
                    if(nbOfValues == minNbOfValues):
                        #if they have same number of values, compare their degeree. if min already had higher degree, change nothing
                        if( len(self.crossword.neighbors(var)) > len(self.crossword.neighbors(minVar))) :
                            minVar = var
                            minNbOfValues = nbOfValues
                            
                    else:
                        minVar = var
                        minNbOfValues = nbOfValues

        return minVar
    
    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """

        if(self.assignment_complete(assignment)):
            return assignment
        
        currVar = self.select_unassigned_variable(assignment)
        listOfValues = self.order_domain_values(currVar,assignment)
        if(listOfValues == None):
            return None

        #test all possible values for the variable
        for val in listOfValues:
            assignmentWithAddedValue = copy.deepcopy(assignment)
            assignmentWithAddedValue[currVar] = val
 
            if(self.consistent(assignmentWithAddedValue)):
                result = self.backtrack(assignmentWithAddedValue)
                if(result != None):
                    return result
                
            #if the value doesnt work with the current assignment remove it and try a new one
            del assignmentWithAddedValue[currVar]
        
        #if none of the values work, then return None
        return None

def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
    
