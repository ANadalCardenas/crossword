import sys
from pprint import pprint
from itertools import product
from collections import defaultdict

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
        
        print(self.backtrack(dict()))
        return None


    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.domains.keys():
            updated_domains = set()
            for word in self.domains[var]:
                if var.length == len(word):
                    updated_domains.add(word)
            self.domains[var] = updated_domains
        

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        overlap_cells = self.crossword.overlaps[x,y]
        if overlap_cells != None:
            letters_overlaped_x = { word[overlap_cells[0]] for word in self.domains[x] }
            letters_overlaped_y = { word[overlap_cells[1]] for word in self.domains[y] }
            intersection = letters_overlaped_x & letters_overlaped_y

            if  intersection is None:
                return False
            else:
                new_domains = set()
                for word in self.domains[x]:
                    if word[overlap_cells[0]] in intersection:
                        new_domains.add(word)
                self.domains[x] = new_domains
                return True
        return False
        

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """

        if arcs is None:
            arcs = set()
            arcs = { (x, y) for x in self.domains for y in self.domains if x != y }

        for arc in arcs:
            if not arc[0].__eq__(arc[1]):
                self.revise(arc[0], arc[1])
            for set_domains in self.domains.values():
                if not set_domains:
                    return False
        return True
                
            
    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for words in assignment.values():
            if len(words) != 1:
                return False
        return True


    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # Checks if all values are different (there are not the same word in more than one space)
        values = set()
        for var_x, words_x in assignment.items():
            for word_x in words_x:
                # Calculates the intersection between the words already inserted and the current word.
                # Checks if the length of "word" is equal than the "length" parameter of current Variable
                if len(word_x) != var_x.length or (values & word_x):
                    return False
                else:
                    values.add(word_x)
            # Checks if the overlap cells have at least one valid option of words for both Variables
            for var_y, words_y in assignment.items():
                if not var_x.__eq__(var_y):
                    overlap_cells = self.crossword.overlaps[var_x,var_y]
                    if overlap_cells:
                        matching_overlap = False
                        for word_x, word_y in product(words_x, words_y):
                            if word_x[overlap_cells[0]] == word_y[overlap_cells[1]]:
                                matching_overlap = True
                                break
                        if not matching_overlap:
                            return False
            return True
        


    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # Checks if current var has already an assignment value
        print("var :",var)
        print("assignment :", assignment)
        if var in assignment.keys():
            return [0]
        # Created de dictionary where the function will order the words of the domain of "var". At first, all values have a 0 value. 
        # All of them haven't eliminated any possible value of their neighboring cells yet
        result = defaultdict(int)
        # Gets all vars in domain
        for var_y in self.domains.keys():
            # Checks that the current var_y is different that the current variable var
            # Checks if ther are any overlap cells between two variables
            if var.__eq__(var_y) or var_y in assignment:
                continue
            overlap_cells = self.crossword.overlaps[var,var_y]
            # Checks if ther are any overlap cells between two variables
            if not overlap_cells:
                continue
            # Checks the possibles values of var_y for each value in the domain of "var"
            for word in self.domains[var]:
                overlap_char = word[overlap_cells[0]]
                # For every possible valur or var_y, checks if the overlap cell matches with the current value of var
                # Adds a unit at the corresponding value if it doesn't match
                deleted = sum(1 for word_y in self.domains[var_y] if word_y[overlap_cells[1]] != overlap_char)
                result[word] += deleted

        return sorted(result, key=result.get)
                        
                    

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # Gets the variables that are not yet in assignment.
        sub_domains = {k: v for k, v in self.domains.items() if k not in assignment}
        # Calcs the ordered list of domain's values with the above function
        ###
        print("sub_domains :",sub_domains)
        for k in sub_domains.items():
            print("k :",k[0])
        ###
        #remaining_values = {k: {self.order_domain_values(k, assignment)[0]} for k in sub_domains.keys()}
        # Orders the last dictionary to find the variable with the lowest degree
        ordered_remaining_values = dict(sorted(remaining_values.items(), key=lambda item: item[1]))
        # Gets the lowest value
        lowest_value = next(iter(ordered_remaining_values.values()), None)
        tie_variables = {k: v for k , v in ordered_remaining_values.items() if ordered_remaining_values[k] == lowest_value}
        # If there is not a tie, return the unique variable in tie_variables
        if len(tie_variables) == 1:
            return tie_variables
        for var in list(tie_variables).items():
            degree_variables = {k : sum(self.crossword.overlaps[var,k]) for k in self.domains.keys() if self.crossword.overlaps[var,k] and not var.__eq__(k)}
        
        
        return dict(sorted(degree_variables.items(), key=lambda item: item[1], reverse = True))[0]

        

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        
        # If all the domain's variables are in current assignment, resturn this assignment as solution
        if self.assignment_complete(assignment):
            return assignment
        
        # Else, selects an unasignment value with the function above (the variable with the lowets remaining values in this domain and highest degree)
        val = self.select_unassigned_variable(assignment)
        # Adds a new element at the current assignment with the pair {val: selected word}
        new_assignment = assignment.copy()
        new_assignment.update(val)

        self.backtrack(new_assignment)

        return None
        """
    def backtrack(self, assignment):
        """
        Using Backtracking Search, return a complete assignment if possible to do so.
        If no solution is possible, return None.
        """
        # Si l'assignació és completa, retornem el resultat
        if len(assignment) == len(self.crossword.variables):
            return assignment

        # Seleccionem una variable no assignada
        var = self.select_unassigned_variable(assignment)

        # Provem els valors del seu domini (ordenats per mínimes restriccions)
        for value in self.order_domain_values(var, assignment):
            # Assignem provisionalment el valor
            new_assignment = assignment.copy()
            new_assignment[var] = value

            # Comprovem si és consistent
            if self.consistent(new_assignment):
                # Opcional: inference amb AC-3
                # domains_backup = deepcopy(self.domains)
                # self.domains[var] = {value}
                # if self.ac3({(neighbor, var) for neighbor in self.crossword.neighbors(var)}):
                result = self.backtrack(new_assignment)
                if result is not None:
                    return result
                # self.domains = domains_backup

        # Si cap valor condueix a una solució, retrocedim
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
