import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if self.count == len(self.cells):
            return self.cells.copy()
        else:
            return False

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells.copy()
        else:
            return False

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        cells = self.cells.copy()
        for sentence_cell in cells:
            if sentence_cell == cell:
                self.cells.remove(cell)
                self.count -= 1


    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        cells = self.cells.copy()
        for sentence_cell in cells:
            if sentence_cell == cell:
                self.cells.remove(cell)

class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # Mark cell as a move thats been made
        self.moves_made.add(cell)

        # Mark cell as safe
        if cell not in self.safes:
            self.mark_safe(cell)

        # If no mines adjacent to the cell flipped
        if count == 0:
            for i in range(cell[0] - 1, cell[0] + 2):
                for j in range(cell[1] - 1, cell[1] + 2):
                    # Ignore cell itself
                    if (i, j) == cell:
                        continue
                    # If between bounds
                    elif 0 <= i < self.height and 0 <= j < self.width:
                        # If not already marked
                        if (i, j) not in self.safes and (i, j) not in self.mines: # Add moves_made?
                            # Mark as a safe cell
                            self.mark_safe((i, j))
        else:
            new_knowledge_cells = set()
            for i in range(cell[0] - 1, cell[0] + 2):
                for j in range(cell[1] - 1, cell[1] + 2):
                    # Ignore cell itself
                    if (i, j) == cell:
                        continue
                    # Ignore if already marked as safe
                    if (i, j) in self.safes:
                        continue
                    # Ignore and discount one mine if already marked as a mine
                    if (i, j) in self.mines:
                        count = count - 1
                        continue
                    # If between bounds
                    if 0 <= i < self.height and 0 <= j < self.width:
                        # Add cell to new list of cells
                        new_knowledge_cells.add((i, j))
            # Create a new sentence and add it to self.knowledge
            print(f'Adding new knowledge: {Sentence(new_knowledge_cells, count)}')
            self.knowledge.append(Sentence(new_knowledge_cells, count))

        self.check_knowledge()
        # Check subsets
        for i in range(len(self.knowledge)):
            for j in range(len(self.knowledge)):
                # Skip equal sentences
                if self.knowledge[i] == self.knowledge[j]:
                    continue
                else:
                    # If one is subset of another
                    if self.knowledge[j].cells < self.knowledge[i].cells: 
                        # Create new sentence
                        new_cells = self.knowledge[i].cells - self.knowledge[j].cells
                        new_count = self.knowledge[i].count - self.knowledge[j].count
                        new_sentence = Sentence(new_cells, new_count)
                        # If the new sentence is not already in the knowledge
                        if new_sentence not in self.knowledge:
                            # Add it to the knowledge
                            print(f'Adding new inferred subset {new_sentence} made from {self.knowledge[i]} and {self.knowledge[j]}')
                            self.knowledge.append(new_sentence)
        # Check knowledge
        self.check_knowledge()

        print(f'Move made is {cell} = {count}')
        print(f'This is self.knowledge:')
        for sentence in self.knowledge:
            print(sentence)
        print(f'This is self.mines: {self.mines}')
        print(f'This is self.safes: {self.safes}')
        print(f'This is self.moves_made: {self.moves_made}')
        print('-----------------------------------------------------------')

    def check_knowledge(self):
        """
        Checks the knowledge to see if any safes or mines can be inferred and simplified from
        existing sentences. If found any, the loop re-starts
        """
      
        # Make a copy to loop over and make changes
        knowledge = self.knowledge.copy()
        for sentence in knowledge:
            # Delete empty sentences
            if len(sentence.cells) == 0:
                self.knowledge.remove(sentence)
                return self.check_knowledge()
            # If sentence has only mines
            if sentence.known_mines():
                # Mark every cell as a mine
                for sentence_cell in sentence.known_mines():
                    self.mark_mine(sentence_cell)
                return self.check_knowledge()
            # If sentence has only safes
            if sentence.known_safes():
                # Mark every cell as safe
                for sentence_cell in sentence.known_safes():
                    self.mark_safe(sentence_cell)
                return self.check_knowledge()
        
    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for cell in self.safes:
            if cell not in self.moves_made and cell not in self.mines:
                return cell
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        possibilities = []
        for i in range(self.height):
            for j in range(self.width):
                if (i, j) not in self.moves_made and (i, j) not in self.safes and (i, j) not in self.mines:
                    possibilities.append((i, j))
        if len(possibilities) == 0:
            return None
        else:
            return random.choice(possibilities)
