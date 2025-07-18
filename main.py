from cinema import Cinema


def initialize_cinema():
    """
    Initialize a Cinema object based on user input.
    """
    print("Please define movie title and seating map in [Title] [Row] [SeatsPerRow] format:")

    while True:
        try:
            input_str = input("> ")
            parts = input_str.strip().split()

            if len(parts) < 3:
                print("Invalid format. Please use [Title] [Row] [SeatsPerRow] format.")
                continue

            title = " ".join(parts[:-2])
            rows = int(parts[-2])
            seats_per_row = int(parts[-1])

            if rows <= 0 or seats_per_row <= 0:
                print("Rows and seats per row must be positive numbers.")
                continue

            if rows > 26:
                print("Maximum number of rows is 26.")
                continue

            if seats_per_row > 50:
                print("Maximum number of seats per row is 50.")
                continue

            return Cinema(title, rows, seats_per_row)

        except ValueError:
            print("Invalid format. Please use [Title] [Row] [SeatsPerRow] format with numeric values for rows and seats.")


def book_tickets(cinema):
    """
    Handle the ticket booking process including seat selection.
    """
    while True:
        print("\nEnter number of tickets to book, or enter blank to go back to main menu:")
        num_tickets_str = input("> ")

        if not num_tickets_str:
            return

        try:
            num_tickets = int(num_tickets_str)
            if num_tickets <= 0:
                print("Number of tickets must be positive.")
                continue

            if num_tickets > cinema.available_seats:
                print(f"Sorry, there are only {cinema.available_seats} seats available.")
                continue

            # Generate booking id
            booking_id = cinema.generate_booking_id()

            # Allocate default seats
            allocated_seats = cinema.allocate_default_seats(num_tickets)

            if not allocated_seats:
                print("Could not allocate seats. Please try again with a different number of tickets.")
                continue

            is_selecting_seats = True

            while is_selecting_seats:
                # Create a temporary booking to display seats
                temp_booking_id = "TEMP_BOOKING_ID"
                for row_index, col_index in allocated_seats:
                    cinema.seating_map[row_index][col_index] = temp_booking_id

                print(f"\nSuccessfully reserved {num_tickets} {cinema.title} tickets.")
                print(f"Booking id: {booking_id}")
                print("Selected seats:")
                cinema.display_seating_map(temp_booking_id)

                # Prompt for seat selection change
                print("Enter blank to accept seat selection, or enter new seating position")
                seating_position = input("> ")

                # Reset temporary booking
                for row_index, col_index in allocated_seats:
                    cinema.seating_map[row_index][col_index] = '.'

                if not seating_position:
                    # User accepted the current selection
                    is_selecting_seats = False
                    continue

                try:
                    row_letter = seating_position[0].upper()
                    col_number = int(seating_position[1:])

                    if not ('A' <= row_letter <= chr(64 + cinema.rows)) or not (
                        1 <= col_number <= cinema.seats_per_row):
                        print("Invalid seating position. Please try again.")
                        continue

                    row_index = cinema.get_row_index(row_letter)
                    col_index = col_number - 1

                    new_seats = cinema.allocate_seats_from_position(num_tickets, row_index, col_index)

                    if not new_seats:
                        print("Could not allocate seats from that position. Please try another position.")
                        continue

                    # Update allocated seats with the new selection
                    allocated_seats = new_seats

                except (ValueError, IndexError):
                    print("Invalid seating position format. Please use format like 'A1', 'B5', etc.")

            # Book the final seat selection
            cinema.book_seats(allocated_seats, booking_id)
            print(f"\nBooking id: {booking_id} confirmed.")
            break

        except ValueError:
            print("Invalid number. Please enter a valid number of tickets.")


def check_bookings(cinema):
    """
    Display seats for a specific booking id.
    """
    while True:
        print("\nEnter booking id, or enter blank to go back to main menu:")
        booking_id = input("> ")

        if not booking_id:
            return

        if booking_id not in cinema.bookings:
            print(f"Booking id {booking_id} not found.")
            return

        print(f"\nBooking id: {booking_id}"
              f"\nSelected seats:")

        cinema.display_seating_map(booking_id)

        print("\nPress C to cancel this booking or enter blank to proceed:")
        is_cancel = input("> ")

        if not is_cancel:
            return

        if is_cancel.lower() == "c":
            cinema.cancel_booking(booking_id)
            print("\nBooking cancelled:")
            return

        print(f"\nInvalid selection")


def main():
    """
    Main application entry point.
    """
    # Initialize the cinema
    cinema = initialize_cinema()
    
    # Main menu loop
    while True:
        print(f"\nWelcome to Cinemas"
              f"\n[1] Book tickets for {cinema.title} ({cinema.available_seats} seats available)"
              f"\n[2] Check bookings"
              f"\n[3] Exit"
              f"\nPlease enter your selection:")
        
        selection = input("> ")
        
        if selection == "1":
            book_tickets(cinema)

        elif selection == "2":
            check_bookings(cinema)

        elif selection == "3":
            print("\nThank you for using Cinemas system. Bye.")
            break

        else:
            print("Invalid selection. Please try again.")


if __name__ == "__main__":
    # cinema = Cinema("Friends", 8, 10)
    # seats = cinema.allocate_default_seats(4)
    # cinema.book_seats(seats, "0001")
    # print(cinema.seating_map[-1])
    main()


