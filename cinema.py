class Cinema:
  """
  Represents a cinema session with booking functionality and seating management.
  """
  def __init__(self, title, rows, seats_per_row):
    self.title = title
    self.rows = min(rows, 26)
    self.seats_per_row = min(seats_per_row, 50)

    self.total_seats = self.rows * self.seats_per_row
    self.available_seats = self.total_seats

    self.seating_map = [['.' for _ in range(self.seats_per_row)] for _ in range(self.rows)]

    self.booking_counter = 0
    self.bookings = {}

  def generate_booking_id(self):
    """
    Generate a unique booking id.
    """
    self.booking_counter += 1
    return f"GIC{self.booking_counter:04d}"

  def get_row_letter(self, row_index):
    """
    Convert row index to letter with `A` being the front row.
    """
    return chr(65 + self.rows - row_index - 1)

  def get_row_index(self, row_letter):
    """
    Convert row letter to index (0-based).
    """
    letter_value = ord(row_letter.upper()) - 65
    return self.rows - letter_value - 1

  def is_seat_available(self, row_index, col_index):
    """
    Check if a seat is available.
    """
    return self.seating_map[row_index][col_index] == '.'

  def _allocate_from_middle(self, row_index, remaining_tickets):
    """
    Allocate seats from the middle of a row outwards.
    """
    allocated_seats = []
    mid_col = self.seats_per_row // 2
    left_offset = 0
    seats_allocated = 0

    # Expand from the middle
    while (mid_col - left_offset >= 0 or
           mid_col + left_offset < self.seats_per_row) and seats_allocated < remaining_tickets:

      # Try right side of middle first
      right_col = mid_col + left_offset
      if right_col < self.seats_per_row and self.is_seat_available(row_index, right_col):
        allocated_seats.append((row_index, right_col))
        seats_allocated += 1

      # If we still need seats and left side is valid, allocate seat on left
      left_col = mid_col - left_offset
      if seats_allocated < remaining_tickets and left_col >= 0 and left_col != right_col and self.is_seat_available(
          row_index, left_col):
        allocated_seats.append((row_index, left_col))
        seats_allocated += 1

      left_offset += 1

    return allocated_seats, seats_allocated

  def allocate_default_seats(self, num_tickets):
    """
    Suggest default seats based on these rules:
    1. Start from the furthest row from the screen.
    2. Start from the middle-most possible column.
    3. When a row is not enough to accommodate the number of tickets, it should overflow to the next row closer to the screen.

    Return None if there is not enough available seats left.
    """
    if num_tickets > self.available_seats:
      return None

    remaining_tickets = num_tickets
    allocated_seats = []

    # Start from the furthest row from screen
    for row_index in range(self.rows - 1, -1, -1):
      if remaining_tickets <= 0:
        break

      row_seats, seats_in_row = self._allocate_from_middle(row_index, remaining_tickets)
      allocated_seats.extend(row_seats)
      remaining_tickets -= seats_in_row

    # If we couldn't allocate all tickets, return None
    if remaining_tickets > 0:
      return None

    return allocated_seats

  def allocate_seats_from_position(self, num_tickets, start_row, start_col):
    """
    Allocate seats when user specifies a starting position:
    1. Starting from the specified position, fill up all empty seats in the same row all the way to the right.
    2. When there is not enough seats available, it should overflow to the next row closer to the screen.
    3. Seat allocation for overflow follows the rules for default seat selection (expand from middle).

    Return None if there is not enough available seats left.
    """
    if num_tickets > self.available_seats:
      return None

    allocated_seats = []
    remaining_tickets = num_tickets

    row_index = start_row
    col_index = start_col
    
    # Handle the starting row (fill from start_col to the right)
    while col_index < self.seats_per_row and remaining_tickets > 0:
      if self.is_seat_available(row_index, col_index):
        allocated_seats.append((row_index, col_index))
        remaining_tickets -= 1
      col_index += 1
    
    # Move to next row closer to screen
    row_index -= 1
    
    # For overflow rows, use the default seat selection logic (middle-out)
    while row_index >= 0 and remaining_tickets > 0:
      row_seats, seats_allocated = self._allocate_from_middle(row_index, remaining_tickets)
      allocated_seats.extend(row_seats)
      remaining_tickets -= seats_allocated
      
      row_index -= 1

    # If we couldn't allocate all tickets, return None
    if remaining_tickets > 0:
      return None

    return allocated_seats

  def book_seats(self, seats, booking_id):
    """
    Mark seats as booked with the given booking_id.
    """
    for row_index, col_index in seats:
      self.seating_map[row_index][col_index] = booking_id

    self.bookings[booking_id] = seats
    self.available_seats -= len(seats)
    return booking_id

  def display_seating_map(self, current_booking=None):
    """
    Display the seating map with current booking highlighted.
    """
    total_width = self.seats_per_row * 4

    screen_text = "S C R E E N"
    padding = (total_width - len(screen_text)) // 2
    separator_line = "-" * total_width

    print(f"\n{' ' * padding}{screen_text}")
    print(separator_line)

    for row_index in range(self.rows):
      row_letter = self.get_row_letter(row_index)
      print(f"{row_letter} ", end="")

      for col_index in range(self.seats_per_row):
        seat_status = self.seating_map[row_index][col_index]

        if seat_status == '.':
          print(".", end="   ")
        elif current_booking and seat_status == current_booking:
          print("o", end="   ")
        else:
          print("#", end="   ")
      print()

    print("  ", end="")
    for col in range(1, self.seats_per_row + 1):
      if col < 10:
        print(f"{col}  ", end=" ")
      else:
        print(f"{col} ", end=" ")
    print("\n")