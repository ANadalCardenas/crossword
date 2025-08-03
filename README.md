Crossword Solver

A Constraint Satisfaction Problem (CSP) solver for automatically generating and solving crossword puzzles. The program fills a crossword grid using a set of words and enforces consistency between intersecting clues.

Features

Solves crossword puzzles using:

Node consistency (unary constraints)

Arc consistency (AC-3 algorithm)

Backtracking search with heuristics:

Minimum Remaining Values (MRV)

Degree heuristic

Least Constraining Value (LCV)

Graphical output (renders the filled crossword as an image)

Text-based printing of the solution in terminal

Requirements

Python 3.8+

Pillow (for saving the crossword as an image)

To install dependencies:

bash
Copy
Edit
pip install -r requirements.txt
Note: The crossword module and data files (structure and word list) must be present.

Usage

bash
Copy
Edit
python generate.py structure.txt words.txt [output.png]
Arguments:

structure.txt: ASCII file describing the crossword grid (use “#” for blocked cells).

words.txt: Text file containing the list of words (one per line).

output.png (optional): If provided, saves the solved crossword as an image.

Example:

bash
Copy
Edit
python generate.py data/structure1.txt data/words.txt solution.png
File Structure
generate.py — Main script to run the crossword generator and solver.

crossword.py — Contains the crossword structure and variable definitions.

words.txt — Word list.

structure.txt — Grid layout for the crossword.

assets/fonts/ — Font used to render letters in the output image.

Limitations

Solving time may increase significantly for large or highly constrained grids.

The solver does not currently handle clues or definitions — only structure and letter matching.

Status

In progress. Most core logic is implemented, but some issues may remain with variable ordering or consistency. Contributions and suggestions are welcome.

These are the structures of each file of this project:

requirements.txt

Minimal dependencies needed to run the project:

Pillow

If you're planning to manage fonts or environment configuration:

python-dotenv # optional

Save this as requirements.txt.

Example structure.txt:

This file defines the layout of the crossword grid. Use # for blocked (black) cells, and space or any other character for open cells.

Example (5x5 grid):

Each line should have the same number of characters.

Make sure there are enough open spaces to allow word placement.

Save this file as structure.txt.

Example words.txt:

This file contains the list of words used to fill the crossword. One word per line.

Example:

apple
lemon
grape
melon
orange
banana
berry

🟡 Tip: Make sure your word list has a wide variety of word lengths and letter combinations to increase the chances of solving the puzzle.

License
This project is open source and licensed under the MIT License.
