from typing import List, Any
import itertools
import copy

class PatternGenerator:
    @staticmethod
    def initialize_pattern(clue_list: List, span: int) -> List[int]:
        """
        Initializes a base pattern for a clue list.

        Example: Clue ['3R', '2B'] → [R, R, R, B, B, 0, ...] based on span.

        Args:
            clue_list: List of clues (e.g., ['3R', '2B']).
            span: Total length of the pattern.

        Returns:
            List[int]: Initialized pattern.
        """
        empty_line = [0] * span
        pointer = 0

        for i, clue in enumerate(clue_list):
            clue_num = int(clue[0])
            if i != 0 and clue[1] == clue_list[i - 1][1]:
                pointer += 1  # Add a separator for same-color clues

            end = pointer + clue_num
            empty_line[pointer:end] = clue[1] * clue_num
            pointer = end

        return empty_line

    @staticmethod
    def generate_clue_sequence(clue_list: List, is_line: bool = False) -> str:
        """
        Generates a sequence representation of the clue list.

        Args:
            clue_list: List of clues.
            is_line: If True, returns a sequence for a line (e.g., 'RRRBB').

        Returns:
            str: Sequence representation.
        """
        if is_line:
            return ''.join([c for c in clue_list if c != 0])
        else:
            return ''.join([int(c[0]) * c[1] for c in clue_list])

    @staticmethod
    def map_non_zero_positions(line: List) -> List[int]:
        """
        Maps positions of non-zero elements in a line.

        Args:
            line: List representing a line.

        Returns:
            List[int]: Positions of non-zero elements.
        """
        positions = [0]
        memory = line[0]

        for i in range(1, len(line)):
            if line[i] != 0 and line[i] != memory:
                positions.append(i)
                memory = line[i]
            elif line[i] != 0 and line[i - 1] == 0 and line[i] == memory:
                positions.append(i)
                memory = line[i]

        return positions

    @staticmethod
    def validate_pattern(line: List, clue: List) -> bool:
        """
        Validates if a line matches the given clue.

        Args:
            line: List representing a line.
            clue: List of clues.

        Returns:
            bool: True if the line matches the clue, False otherwise.
        """
        clue_pointer = 0
        line_pointer = 0

        while line_pointer < len(line) and clue_pointer < len(clue):
            if line[line_pointer] == 0:
                line_pointer += 1
            else:
                if line[line_pointer] != clue[clue_pointer][-1]:
                    return False

                if clue[clue_pointer][:-1] == '1':
                    temp_line_pointer = line_pointer + 1
                    temp_clue_pointer = clue_pointer + 1

                    if (temp_clue_pointer < len(clue) and clue[temp_clue_pointer][-1] == clue[clue_pointer][-1]):
                        if temp_line_pointer < len(line) and line[temp_line_pointer] != 0:
                            return False
                        else:
                            clue_pointer = temp_clue_pointer
                            line_pointer = temp_line_pointer + 1
                    else:
                        clue_pointer = temp_clue_pointer
                        line_pointer = temp_line_pointer
                else:
                    counter = line_pointer + int(clue[clue_pointer][:-1])
                    if counter > len(line):
                        return False

                    while line_pointer < counter:
                        if line[line_pointer] != clue[clue_pointer][-1]:
                            return False
                        line_pointer += 1

                    clue_pointer += 1

        return True

    @staticmethod
    def generate_all_permutations(clue_list: List, span: int) -> List[List]:
        """
        Generates all valid permutations for a clue list.

        Args:
            clue_list: List of clues.
            span: Total length of the pattern.

        Returns:
            List[List]: Valid permutations.
        """
        if len(clue_list) == 0:
            return [[0] * span]

        first_line = PatternGenerator.initialize_pattern(clue_list, span)
        permutations = list(itertools.permutations(first_line))
        validator = set()
        result = []

        for perm in permutations:
            line_str = ''.join([str(e) for e in perm])
            if PatternGenerator.validate_pattern(perm, clue_list) and line_str not in validator:
                validator.add(line_str)
                result.append(list(perm))

        return result

def generate_permutations(clue: List, length: int) -> List[List]:
    """
    Generates all valid permutations for a clue.

    Args:
        clue: List of clues.
        length: Length of the pattern.

    Returns:
        List[List]: Valid permutations.
    """
    if len(clue) == 0:
        return [[0] * length]

    empty_array = [0] * length
    return generate_helper(clue, 0, 0, empty_array)

def generate_helper(clue: List, number: int, start: int, array: List) -> List[List]:
    """
    Recursively generates permutations for a clue segment.

    Args:
        clue: Current clue segment.
        number: Index of the current clue being processed.
        start: Starting position in the array.
        array: Working array to fill permutations into.

    Returns:
        List[List]: Valid permutations for the current clue segment.
    """
    num, color = int(clue[number][:-1]), clue[number][-1]
    permutations = []
    working_array = copy.deepcopy(array)

    for index in range(len(array)):
        if index >= start:
            for s in range(start, len(array)):
                working_array[s] = 0

            working_array[index] = color
            new_start = index + num

            for offset in range(num):
                if index - offset - 1 > 0 and index - offset - 1 >= start:
                    working_array[index - offset - 1] = 0
                if index + offset < len(array):
                    working_array[index + offset] = color

            if number + 1 < len(clue):
                next_num, next_color = int(clue[number + 1][:-1]), clue[number + 1][-1]
                if next_color == color:
                    new_perms = generate_helper(clue, number + 1, new_start + 1, working_array)
                else:
                    new_perms = generate_helper(clue, number + 1, new_start, working_array)

                for perm in new_perms:
                    if PatternGenerator.validate_pattern(perm, clue):
                        permutations.append(perm)
            else:
                if PatternGenerator.validate_pattern(working_array, clue):
                    permutations.append(copy.deepcopy(working_array))

    return permutations