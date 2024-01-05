from os.path import exists
import re

# Helper function that mimics ".find" but continuously.
# Returns a list of indices, empty if none found
def find_all(text, keyword):
    return [m.start() for m in re.finditer(keyword, text.lower())]

# Helper function to determine whether quoted words are near enough to each other
# Assume arrays is a 2D array of sorted indices
# Returns lowest index upon success and None otherwise
def find_numbers_within_range(arrays, proximity_score):
  if not arrays or not arrays[0]:
      return None  # Handle empty input

  # Number of subarrays and their lengths
  num_subarrays = len(arrays)
  subarray_lengths = [len(subarray) for subarray in arrays]

  # Initialize pointers for each subarray
  pointers = [0] * num_subarrays

  while True:
      # Get the current set of numbers
      current_set = [arrays[i][pointers[i]] for i in range(num_subarrays)]

      # Find the minimum and maximum values in the current set
      min_val, max_val = min(current_set), max(current_set)

      # Check if the condition is met
      if max_val - min_val <= proximity_score:
          return min_val  # Return the smallest number from the set

      # Move the pointer of the subarray with the smallest element in the current set
      min_pointer = current_set.index(min_val)
      pointers[min_pointer] += 1

      # Check if any subarray is exhausted
      if pointers[min_pointer] == subarray_lengths[min_pointer]:
          return None  # No set meeting the conditions

# Helper function to search through a tournament
# Returns next 20 characters
def ctrlf(keywords, path):
    # Handle empty keywords
    if not keywords:
        return False
    # Return false if file doesn't exist
    if exists(path):
        f = open(path, "r")
    else:
        return False
    # Read file
    current_text = f.read()
    f.close()
    current_text_lower = current_text.lower()

    # Separate quoted and unquoted words
    quote_flag_flag = False
    quote_flag = False
    quoted_words = []
    current_quoted_words = []
    unquoted_words = []
    for word in keywords:
        # Check for quote and turn on corresponding flags
        if not quote_flag and word[0] == "\"":
            quote_flag = True
            word = word[1:]
        elif quote_flag and word[-1] == "\"":
            quote_flag_flag = True
            word = word[:-1]
        # Remember by quoted or unquoted
        if quote_flag:
            current_quoted_words.append(word)
        else:
            unquoted_words.append(word)
        # Turn off quote mode if necessary
        if quote_flag_flag:
            quote_flag = False
            quoted_words.append(current_quoted_words)
            current_quoted_words = []
        quote_flag_flag = False
    
    # Account for unclosed quotation
    if quote_flag:
        for word in current_quoted_words:
            unquoted_words.append(word)
    
    # Check unquoted words first
    preview_index = 0
    index_flag = True
    for word in unquoted_words:
        if path.find(word) != -1:
            result = [0]
        else:
            result = find_all(current_text_lower, word)
        if not result:
            return False
        if index_flag:
            preview_index = result[0]
            index_flag = False
    
    # Then, check quoted words
    proximity_score = 100
    for current_words in quoted_words:
        quoted_results = []
        for word in current_words:
            result = find_all(current_text_lower, word)
            if not result:
                return False
            quoted_results.append(result)

        preview_index = find_numbers_within_range(quoted_results, proximity_score)
        if preview_index is None:
            return False

    preview_size = 75 # 75 characters of preview

    # Clean up and return preview
    preview = current_text[preview_index:preview_index+preview_size]
    clean_preview = ""
    for char in preview:
        if char != "\n":
            clean_preview += char
        else:
            clean_preview += " "
    return clean_preview
        

# Returns path to pdf file
def get_path(tournament, level, year):
    return f"./static/rounds/{tournament}/{tournament}_{level}_{year}.txt"

# Returns corresponding color to a level
def get_color(level):
    if level == "novice":
        return "table-success"
    elif level == "intermediate":
        return "table-warning"
    elif level == "advanced":
        return "table-danger"
    elif level == "elite":
        return "table-secondary"
    else:
        return ""

# Helper function for row sorting by level
def sort_level(row):
    if row["level"] == "advanced":
        return 0
    elif row["level"] == "intermediate":
        return 1
    elif row["level"] == "novice":
        return 2
    elif row["level"] == "elite":
        return 3
    else:
        return 4