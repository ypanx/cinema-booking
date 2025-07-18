import logging

# Constants
MAX_ROWS = 26
MAX_SEATS_PER_ROW = 50
ASCII_A = 65

class Cinema:
    """
    Represents a cinema session with booking functionality and seating management.
    """
    def __init__(self, title, rows, seats_per_row):
        self.title = title
        self.rows = min(rows, MAX_ROWS)
        self.seats_per_row = min(seats_per_row, MAX_SEATS_PER_ROW)

        self.total_seats = self.rows * self.seats_per_row
        self.available_seats = self.total_seats

        self.seating_map = [['.' for _ in range(self.seats_per_row)] for _ in range(self.rows)]

        self.booking_counter = 0
        self.bookings = {}

        # Configure logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def generate_booking_id(self):
        """
        Generate a unique booking id.
        """
        self.booking_counter += 1
        booking_id = f"GIC{self.booking_counter:04d}"
        self.logger.debug(f"Generated booking ID: {booking_id}")
        return booking_id

    def get_row_letter(self, row_index):
        """
        Convert row index to letter with `A` being the front row.
        """
        if not (0 <= row_index < self.rows):
            raise ValueError(f"Row index {row_index} is out of range")
        return chr(ASCII_A + self.rows - row_index - 1)

    def get_row_index(self, row_letter):
        """
        Convert row letter to index (0-based).
        """
        if not isinstance(row_letter, str) or len(row_letter) != 1:
            raise ValueError("Row letter must be a single character")
        
        letter_value = ord(row_letter.upper()) - ASCII_A
        row_index = self.rows - letter_value - 1
        
        if not (0 <= row_index < self.rows):
            raise ValueError(f"Row letter '{row_letter}' is out of range")
        
        return row_index

    def is_seat_available(self, row_index, col_index):
        """
        Check if a seat is available.
        """
        if not (0 <= row_index < self.rows and 0 <= col_index < self.seats_per_row):
            return False
        return self.seating_map[row_index][col_index] == '.'

    def _allocate_from_middle(self, row_index, remaining_tickets):
        """
        Allocate seats from the middle of a row outwards.
        """
        allocated_seats = []
        mid_col = (self.seats_per_row // 2)
        if self.seats_per_row % 2 == 0:
            mid_col -= 1

        left_offset = 0
        seats_allocated = 0

        # Expand from the middle
        while (mid_col - left_offset >= 0 or mid_col + left_offset < self.seats_per_row) and seats_allocated < remaining_tickets:
            # Try right side of middle first
            right_col = mid_col + left_offset
            if right_col < self.seats_per_row and self.is_seat_available(row_index, right_col):
                allocated_seats.append((row_index, right_col))
                seats_allocated += 1

            # If we still need seats and left side is valid, allocate seat on left
            left_col = mid_col - left_offset
            if (seats_allocated < remaining_tickets and left_col >= 0 and 
                left_col != right_col and self.is_seat_available(row_index, left_col)):
                allocated_seats.append((row_index, left_col))
                seats_allocated += 1

            left_offset += 1

        return allocated_seats, seats_allocated

    def allocate_default_seats(self, num_tickets):
        """
        Suggest default seats based on these rules:
        1. Start from the furthest row from the screen.
        2. Start from the middle-most possible column.
        3. When a row is not enough to accommodate the number of tickets, 
           it should overflow to the next row closer to the screen.

        Return None if there is not enough available seats left.
        """
        if num_tickets <= 0:
            raise ValueError("Number of tickets must be positive")
            
        if num_tickets > self.available_seats:
            self.logger.warning(f"Cannot allocate {num_tickets} tickets - only {self.available_seats} available")
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
            self.logger.error(f"Could not allocate all {num_tickets} tickets")
            return None

        self.logger.info(f"Successfully allocated {num_tickets} seats")
        return allocated_seats

    def allocate_seats_from_position(self, num_tickets, start_row, start_col):
        """
        Allocate seats when user specifies a starting position:
        1. Starting from the specified position, fill up all empty seats in the same row all the way to the right.
        2. When there is not enough seats available, it should overflow to the next row closer to the screen.
        3. Seat allocation for overflow follows the rules for default seat selection (expand from middle).

        Return None if there is not enough available seats left.
        """
        if num_tickets <= 0:
            raise ValueError("Number of tickets must be positive")
            
        if not (0 <= start_row < self.rows and 0 <= start_col < self.seats_per_row):
            raise ValueError("Starting position is out of bounds")
            
        if num_tickets > self.available_seats:
            self.logger.warning(f"Cannot allocate {num_tickets} tickets - only {self.available_seats} available")
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
        while remaining_tickets > 0 and row_index >= 0:
            row_seats, seats_allocated = self._allocate_from_middle(row_index, remaining_tickets)
            allocated_seats.extend(row_seats)
            remaining_tickets -= seats_allocated
            row_index -= 1

        # If we couldn't allocate all tickets, return None
        if remaining_tickets > 0:
            self.logger.error(f"Could not allocate all {num_tickets} tickets from specified position")
            return None

        self.logger.info(f"Successfully allocated {num_tickets} seats from position ({start_row}, {start_col})")
        return allocated_seats

    def book_seats(self, seats, booking_id):
        """
        Mark seats as booked with the given booking_id.
        """
        if not seats:
            raise ValueError("No seats provided for booking")
            
        for row_index, col_index in seats:
            if not self.is_seat_available(row_index, col_index):
                raise ValueError(f"Seat ({row_index}, {col_index}) is not available")
            self.seating_map[row_index][col_index] = booking_id

        self.bookings[booking_id] = seats
        self.available_seats -= len(seats)
        self.logger.info(f"Booked {len(seats)} seats with booking ID: {booking_id}")
        return booking_id

    def cancel_booking(self, booking_id):
        """
        Cancel a booking and free up the seats.
        """
        if booking_id not in self.bookings:
            self.logger.warning(f"Booking ID {booking_id} not found")
            return False

        seats_count = len(self.bookings[booking_id])
        for seat_row, seat_col in self.bookings[booking_id]:
            self.seating_map[seat_row][seat_col] = "."
            self.available_seats += 1

        del self.bookings[booking_id]
        self.logger.info(f"Cancelled booking {booking_id} and freed {seats_count} seats")
        return True

    def _format_screen_header(self):
        """Format the screen header section."""
        total_width = self.seats_per_row * 4
        screen_text = "S C R E E N"
        padding = (total_width - len(screen_text)) // 2
        separator_line = "-" * total_width
        
        return f"\n{' ' * padding}{screen_text}\n{separator_line}"

    def _format_seating_grid(self, current_booking=None):
        """Format the main seating grid."""
        grid_lines = []
        
        for row_index in range(self.rows):
            row_letter = self.get_row_letter(row_index)
            line = f"{row_letter} "

            for col_index in range(self.seats_per_row):
                seat_status = self.seating_map[row_index][col_index]

                if seat_status == '.':
                    line += "."
                elif current_booking and seat_status == current_booking:
                    line += "o"
                else:
                    line += "#"
                line += "   "
            
            grid_lines.append(line)
        
        return "\n".join(grid_lines)

    def _format_column_numbers(self):
        """Format the column number footer."""
        line = "  "
        for col in range(1, self.seats_per_row + 1):
            if col < 10:
                line += f"{col}   "
            else:
                line += f"{col}  "
        return line

    def display_seating_map(self, current_booking=None):
        """
        Display the seating map with current booking highlighted.
        """
        self.logger.info(f"Displaying seating map for '{self.title}'")
        
        # Build the complete seating map display
        display_parts = [
            self._format_screen_header(),
            self._format_seating_grid(current_booking),
            self._format_column_numbers(),
            ""  # Empty line at the end
        ]
        
        seating_display = "\n".join(display_parts)
        self.logger.info(f"Cinema seating map:\n{seating_display}")
        
        # Also print to console for user visibility
        print(seating_display)