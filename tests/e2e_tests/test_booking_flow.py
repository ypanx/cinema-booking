import unittest
from unittest.mock import patch
from io import StringIO
import sys

from main import Cinema, main, book_tickets

class TestBookingFlow(unittest.TestCase):
    def setUp(self):
        # Redirect stdout to capture output
        self.held_output = StringIO()
        self.old_stdout = sys.stdout
        sys.stdout = self.held_output
    
    def tearDown(self):
        # Restore stdout
        sys.stdout = self.old_stdout
    
    @patch('builtins.input')
    def test_cinema_creation_small(self, mock_input):
        mock_input.side_effect = ["Interstellar 5 5", "3"]

        main()

        output = self.held_output.getvalue()
        self.assertIn("Interstellar", output)
    
    @patch('builtins.input')
    def test_cinema_creation_large(self, mock_input):
        mock_input.side_effect = ["Inception 20 30", "3"]
        
        main()

        output = self.held_output.getvalue()
        self.assertIn("Inception", output)

    @patch('builtins.input')
    def test_cinema_creation_max(self, mock_input):
        mock_input.side_effect = ["Tenet 30 50"]

        try:
            main()
        except StopIteration:
            pass

        output = self.held_output.getvalue()
        self.assertNotIn("Tenet", output)
        self.assertIn("Maximum number of rows is 26", output)
    
    @patch('builtins.input')
    def test_basic_booking_flow(self, mock_input):
        mock_input.side_effect = ["The Dark Knight 5 10", "1", "2", "", "3"]
        
        main()

        output = self.held_output.getvalue()
        self.assertIn("Successfully reserved 2 The Dark Knight tickets", output)
        self.assertIn("Booking id: BK0001", output)
    
    @patch('builtins.input')
    def test_change_seats_once(self, mock_input):
        mock_input.side_effect = ["Oppenheimer 5 10", "1", "2", "B5", "", "3"]
        
        main()

        output = self.held_output.getvalue()
        self.assertIn("Successfully reserved 2 Oppenheimer tickets", output)
        self.assertIn("Booking id: BK0001", output)
        
        # Map should be shown twice, if there's a seat change
        self.assertGreaterEqual(output.count("S C R E E N"), 2)
    
    @patch('builtins.input')
    def test_change_seats_multiple_times(self, mock_input):
        mock_input.side_effect = [
            "Dunkirk 8 12",
            "1",
            "3",
            "C6",
            "A2",
            "D10",
            "",
            "3"
        ]
        
        main()

        output = self.held_output.getvalue()
        self.assertIn("Successfully reserved 3 Dunkirk tickets", output)
        self.assertIn("Booking id: BK0001", output)
        
        # Map should be shown 4 times, for the seat changes.
        seating_maps = output.count("S C R E E N")
        self.assertGreaterEqual(seating_maps, 4)
    
    @patch('builtins.input')
    def test_check_bookings(self, mock_input):
        mock_input.side_effect = [
            "Insomnia 6 8",
            "1",
            "2",
            "",
            "2"
            "0001",
            "",
            "3"
        ]
        
        main()

        output = self.held_output.getvalue()
        self.assertIn("Booking id: BK0001", output)
        self.assertIn("Selected seats:", output)
        
        # Check for booking confirmation
        booking_confirms = output.count("Booking id: BK0001")
        self.assertGreaterEqual(booking_confirms, 2)
    
    @patch('builtins.input')
    def test_invalid_seating_position(self, mock_input):
        mock_input.side_effect = [
            "Insomnia 5 8",
            "1",
            "2",
            "Z9",
            "A20",
            "invalid",
            "B3",
            "",
            "3"
        ]
        
        main()

        output = self.held_output.getvalue()
        self.assertIn("Invalid seating position", output)
        self.assertIn("Booking id: BK0001", output)
    
    @patch('builtins.input')
    def test_handling_fully_booked_cinema(self, mock_input):
        cinema = Cinema("Memento", 2, 3)

        # Pre-book all seats
        seats = [(0,0), (0,1), (0,2), (1,0), (1,1), (1,2)]
        cinema.book_seats(seats, "BK0001")
        
        # Try to book more seats
        mock_inputs = ["2", ""]
        
        with patch('builtins.input', side_effect=mock_inputs):
            book_tickets(cinema)
        
        output = self.held_output.getvalue()
        self.assertIn("Sorry, there are only 0 seats available", output)
    
    @patch('builtins.input')
    def test_wide_cinema_booking(self, mock_input):
        # Test ability to display double digits column number
        mock_input.side_effect = [
            "Insomnia 5 30",
            "1",
            "4",
            "C20",
            "",
            "2",
            "BK0001",
            "",
            "3"
        ]
        
        main()

        output = self.held_output.getvalue()
        self.assertIn("Booking id: BK0001", output)

        self.assertIn("S C R E E N", output)
        self.assertIn("10", output)
        self.assertIn("19", output)
        self.assertIn("20", output)

    @patch('builtins.input')
    def test_invalid_cinema_creation(self, mock_input):
        mock_input.side_effect = [
            "Batman Begins",
            "30 10",
            "Test -5 10",
            "Test 10 -5",
            "Test 30 50",
            "Test 20 60",
            "Test 5 10",
            "3"
        ]

        main()

        output = self.held_output.getvalue()
        self.assertIn("Invalid format", output)
        self.assertIn("Maximum number of rows", output)
        self.assertIn("Maximum number of seats per row", output)
    
    @patch('builtins.input')
    def test_booking_zero_or_negative_tickets(self, mock_input):
        mock_input.side_effect = [
            "The Prestige 10 10",
            "1",
            "0",
            "-5",
            "abc",
            "",
            "3"
        ]
        
        main()

        output = self.held_output.getvalue()
        self.assertIn("Number of tickets must be positive", output)
        self.assertIn("Invalid number", output)
    
    @patch('builtins.input')
    def test_check_nonexistent_booking(self, mock_input):
        mock_input.side_effect = [
            "Following 10 10",
            "2",
            "BK9999",
            "",
            "3"
        ]
        
        try:
            main()
        except (SystemExit, StopIteration):
            pass
        
        output = self.held_output.getvalue()
        self.assertIn("Booking id BK9999 not found", output)
    
    @patch('builtins.input')
    def test_invalid_menu_option(self, mock_input):
        mock_input.side_effect = [
            "Following 10 10",
            "5",
            "abc",
            "3"
        ]
        
        main()

        output = self.held_output.getvalue()
        self.assertIn("Invalid selection", output)
    
    @patch('builtins.input')
    def test_book_more_tickets_than_available(self, mock_input):
        mock_input.side_effect = [
            "The Dark Knight Rises 3 3",
            "1",
            "10",
            "",
            "3"
        ]
        
        main()

        output = self.held_output.getvalue()
        self.assertIn("Sorry, there are only 9 seats available", output)
    
    @patch('builtins.input')
    def test_multiple_bookings(self, mock_input):
        mock_input.side_effect = [
            "The Hustle 10 10",
            "1",
            "2",
            "",
            "1",
            "3",
            "",
            "2",
            "BK0001",
            "",
            "2",
            "BK0002",
            "",
            "3"
        ]

        try:
            main()
        except (SystemExit, StopIteration):
            pass

        output = self.held_output.getvalue()
        
        # Verify 2 bookings were made
        self.assertIn("Booking id: BK0001 confirmed", output)
        self.assertIn("Booking id: BK0002 confirmed", output)
        
        # Check available seats were updated correctly, after 5 tickets are booked
        self.assertIn("(95 seats available)", output)
    
    @patch('builtins.input')
    def test_allocation_with_unavailable_seats(self, mock_input):
        # cinema with some pre-booked seats
        cinema = Cinema("The Hustle", 5, 11)
        
        # book the middle seats in the back row
        booking_id = cinema.generate_booking_id()
        cinema.book_seats([(4, 5)], booking_id)
        
        # Try to book seats that would include the middle seat
        mock_inputs = ["3", "B6", ""]
        
        with patch('builtins.input', side_effect=mock_inputs):
            book_tickets(cinema)
        
        output = self.held_output.getvalue()
        
        # Should skip the booked middle seat and allocate adjacent seats
        self.assertIn("Successfully reserved 3", output)
        self.assertIn("Booking id: BK0002 confirmed", output)

if __name__ == '__main__':
    unittest.main() 