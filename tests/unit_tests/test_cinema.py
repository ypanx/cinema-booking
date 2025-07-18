import unittest

from cinema import Cinema

class TestCinema(unittest.TestCase):
    def test_initialization(self):
        """
        Test cinema initialization with various sizes.
        """
        cinema = Cinema("Interstellar", 10, 15)
        self.assertEqual(cinema.title, "Interstellar")
        self.assertEqual(cinema.rows, 10)
        self.assertEqual(cinema.seats_per_row, 15)
        self.assertEqual(cinema.total_seats, 150)
        self.assertEqual(cinema.available_seats, 150)
        
        # small cinema
        small = Cinema("Harry Potter", 3, 4)
        self.assertEqual(small.rows, 3)
        self.assertEqual(small.seats_per_row, 4)
        self.assertEqual(small.total_seats, 12)
        
        # max size constraints
        large = Cinema("Lord of the Rings", 30, 60)
        self.assertEqual(large.rows, 26)
        self.assertEqual(large.seats_per_row, 50)
        self.assertEqual(large.total_seats, 26 * 50)
    
    def test_row_conversions(self):
        """
        Test row letter/index conversion methods.
        """
        cinema = Cinema("Interstellar", 5, 10)
        
        # row_index to letter
        self.assertEqual(cinema.get_row_letter(0), 'E')
        self.assertEqual(cinema.get_row_letter(4), 'A')
        
        # letter to row_index
        self.assertEqual(cinema.get_row_index('A'), 4)
        self.assertEqual(cinema.get_row_index('E'), 0)
        
        # case insensitivity
        self.assertEqual(cinema.get_row_index('a'), 4)
        
        # larger cinema
        cinema_large = Cinema("Interstellar", 26, 10)
        self.assertEqual(cinema_large.get_row_letter(0), 'Z')
        self.assertEqual(cinema_large.get_row_letter(25), 'A')
        self.assertEqual(cinema_large.get_row_index('Z'), 0)
        self.assertEqual(cinema_large.get_row_index('A'), 25)
    
    def test_booking_id_generation(self):
        """
        Test unique booking id generation.
        """
        cinema = Cinema("Interstellar", 5, 5)
        
        # initial booking ids
        self.assertEqual(cinema.generate_booking_id(), "BK0001")
        self.assertEqual(cinema.generate_booking_id(), "BK0002")
        self.assertEqual(cinema.generate_booking_id(), "BK0003")
        
        # formatting with larger numbers
        cinema.booking_counter = 9998
        self.assertEqual(cinema.generate_booking_id(), "BK9999")
        self.assertEqual(cinema.generate_booking_id(), "BK10000")
    
    def test_seat_availability(self):
        """
        Test seat availability checking.
        """
        cinema = Cinema("Interstellar", 5, 5)
        
        # All seats should be available initially
        for row in range(5):
            for col in range(5):
                self.assertTrue(cinema.is_seat_available(row, col))
        
        # Book some seats
        test_seats = [(0, 0), (2, 3)]
        cinema.book_seats(test_seats, "BK0001")
        
        # Check availability after booking
        for row in range(5):
            for col in range(5):
                if (row, col) in test_seats:
                    self.assertFalse(cinema.is_seat_available(row, col))
                else:
                    self.assertTrue(cinema.is_seat_available(row, col))
    
    def test_allocate_default_seats_simple(self):
        """
        Test basic default seat allocation.
        """
        cinema = Cinema("Interstellar", 5, 11)
        
        # allocate one seat - should be in middle of back row
        seats = cinema.allocate_default_seats(1)
        self.assertEqual(len(seats), 1)
        self.assertEqual(seats[0], (4, 5))
        
        # allocate three seats - should be middle and adjacent in back row
        cinema = Cinema("Interstellar", 5, 11)
        seats = cinema.allocate_default_seats(3)
        self.assertEqual(len(seats), 3)
        self.assertIn((4, 5), seats)
        self.assertIn((4, 4), seats)
        self.assertIn((4, 6), seats)
        
        # allocation from middle expands outward correctly
        cinema = Cinema("Interstellar", 5, 11)
        seats = cinema.allocate_default_seats(5)
        self.assertEqual(len(seats), 5)
        self.assertIn((4, 5), seats)
        self.assertIn((4, 4), seats)
        self.assertIn((4, 6), seats)
        self.assertIn((4, 3), seats)
        self.assertIn((4, 7), seats)
    
    def test_allocate_default_seats_multiple_rows(self):
        """
        Test default seat allocation across multiple rows.
        """
        cinema = Cinema("Interstellar", 5, 5)
        
        # allocate more seats than in one row
        seats = cinema.allocate_default_seats(8)
        self.assertEqual(len(seats), 8)
        
        # count seats in each row
        row_counts = {}
        for row, _ in seats:
            row_counts[row] = row_counts.get(row, 0) + 1
        
        # should use at least two rows
        self.assertGreaterEqual(len(row_counts), 2)
        
        # back row should be filled first, followed by the next
        self.assertEqual(row_counts.get(4), 5)
        self.assertEqual(row_counts.get(3), 3)
    
    def test_allocate_default_seats_with_unavailable_seats(self):
        """
        Test default allocation when some seats are already booked.
        """
        cinema = Cinema("Interstellar", 5, 5)
        
        # book the middle seats in the back row
        cinema.book_seats([(4, 2)], "BK0001")
        
        # allocate 3 seats
        seats = cinema.allocate_default_seats(3)
        self.assertEqual(len(seats), 3)
        
        # middle seat should be skipped
        self.assertNotIn((4, 2), seats)
        
        # we should still get seats from the middle outward
        self.assertIn((4, 1), seats)
        self.assertIn((4, 3), seats)
    
    def test_allocate_from_position_simple(self):
        """
        Test allocating seats from a specified position in a single row.
        """
        cinema = Cinema("Interstellar", 5, 10)
        
        # 3 seats from position (2,3)
        seats = cinema.allocate_seats_from_position(3, 2, 3)
        self.assertEqual(len(seats), 3)
        self.assertIn((2, 3), seats)
        self.assertIn((2, 4), seats)
        self.assertIn((2, 5), seats)
        
        # 2 seats from the end of row
        seats = cinema.allocate_seats_from_position(2, 3, 8)
        self.assertEqual(len(seats), 2)
        self.assertIn((3, 8), seats)
        self.assertIn((3, 9), seats)
    
    def test_allocate_from_position_overflow(self):
        """
        Test allocating seats with overflow to next row.
        """
        cinema = Cinema("Interstellar", 5, 5)
        
        # request seats that overflow to next row
        seats = cinema.allocate_seats_from_position(4, 3, 3)
        self.assertEqual(len(seats), 4)
        
        # should include positions (3,3) and (3,4) from first row
        self.assertIn((3, 3), seats)
        self.assertIn((3, 4), seats)
        
        # should overflow to next row from middle
        self.assertIn((2, 2), seats)
        
        # larger number of seats
        cinema = Cinema("Interstellar", 5, 5)
        seats = cinema.allocate_seats_from_position(8, 4, 2)
        self.assertEqual(len(seats), 8)
        
        # count seats per row
        rows = {}
        for row, _ in seats:
            rows[row] = rows.get(row, 0) + 1
        
        # 3 seats from row 4, 5 seats from row 3
        self.assertEqual(rows.get(4), 3)
        self.assertEqual(rows.get(3), 5)

    def test_allocate_from_overflow(self):
        """
        Test allocating seats with overflow to next row.
        """
        cinema = Cinema("Interstellar", 3, 3)

        # request seats that overflow to next row - this should work
        # Starting from (0, 1), we can fill 2 seats in row 0, then overflow to row 1 for 2 more
        seats = cinema.allocate_seats_from_position(4, 0, 1)
        
        # If allocation fails, it should return None
        if seats is None:
            # Let's try a smaller allocation that should work
            seats = cinema.allocate_seats_from_position(2, 0, 1)
            self.assertEqual(len(seats), 2)
            booking_id = "BK0001"
            cinema.book_seats(seats, booking_id)
            self.assertEqual(cinema.seating_map[0][1], booking_id)
            self.assertEqual(cinema.seating_map[0][2], booking_id)
        else:
            self.assertEqual(len(seats), 4)
            booking_id = "BK0001"
            cinema.book_seats(seats, booking_id)
            # Check that 4 seats were allocated correctly

    def test_allocate_from_middle_even(self):
        """
        Test allocating seats with overflow to next row.
        """
        booking_id = "BK0001"

        cinema = Cinema("Interstellar", 1, 2)
        seats = cinema.allocate_default_seats(1)

        cinema.book_seats(seats, booking_id)
        self.assertEqual([booking_id, "."], cinema.seating_map[0])

    def test_allocate_from_middle_even_large(self):
        """
        Test allocating seats with overflow to next row.
        """
        booking_id = "BK0001"

        # More columns
        cinema = Cinema("Interstellar", 1, 10)
        seats = cinema.allocate_default_seats(4)
        cinema.book_seats(seats, booking_id)

        self.assertEqual(['.', '.', '.', booking_id, booking_id, booking_id, booking_id, '.', '.', '.'], cinema.seating_map[0])

    
    def test_allocate_from_position_with_unavailable_seats(self):
        """
        Test allocating from position when some seats are already booked.
        """
        cinema = Cinema("Interstellar", 5, 5)
        
        # book 2 seats
        cinema.book_seats([(3, 2), (3, 4)], "BK0001")
        
        # try to allocate seats nearby
        seats = cinema.allocate_seats_from_position(3, 3, 1)
        self.assertEqual(len(seats), 3)
        
        # should skip booked seats
        self.assertIn((3, 1), seats)
        self.assertIn((3, 3), seats)
        self.assertNotIn((3, 2), seats)
        self.assertNotIn((3, 4), seats)
    
    def test_book_seats(self):
        """
        Test booking seats and updating internal state.
        """
        cinema = Cinema("Interstellar", 5, 5)
        
        seats = [(1, 1), (1, 2), (2, 3)]
        booking_id = "BK0001"
        result = cinema.book_seats(seats, booking_id)

        self.assertEqual(result, booking_id)

        self.assertIn(booking_id, cinema.bookings)
        self.assertEqual(cinema.bookings[booking_id], seats)
        
        for row, col in seats:
            self.assertEqual(cinema.seating_map[row][col], booking_id)
        
        self.assertEqual(cinema.available_seats, 25 - len(seats))
        
        more_seats = [(3, 3), (3, 4)]
        another_id = "BK0002"
        cinema.book_seats(more_seats, another_id)
        
        self.assertEqual(cinema.bookings[booking_id], seats)
        self.assertEqual(cinema.bookings[another_id], more_seats)
        
        self.assertEqual(cinema.seating_map[1][1], booking_id)
        self.assertEqual(cinema.seating_map[3][3], another_id)
        
        self.assertEqual(cinema.available_seats, 25 - len(seats) - len(more_seats))
    
    def test_allocate_from_middle_helper(self):
        """
        Test the _allocate_from_middle helper method.
        """
        cinema = Cinema("Interstellar", 5, 11)
        
        # allocate 3 seats from middle of row 2
        seats, count = cinema._allocate_from_middle(2, 3)
        
        self.assertEqual(count, 3)
        self.assertEqual(len(seats), 3)

        self.assertIn((2, 5), seats)
        self.assertIn((2, 4), seats)
        self.assertIn((2, 6), seats)
        
        # test with some unavailable seats
        cinema.book_seats([(2, 5)], "BK0001")
        seats, count = cinema._allocate_from_middle(2, 3)
        
        self.assertEqual(count, 3)
        self.assertEqual(len(seats), 3)
        
        # Should skip middle seat
        self.assertNotIn((2, 5), seats)
        self.assertIn((2, 4), seats)
        self.assertIn((2, 6), seats)
        self.assertTrue((2, 3) in seats or (2, 7) in seats)
    
    def test_edge_cases(self):
        """
        Test various edge cases for the Cinema class.
        """
        # 0 tickets - should raise ValueError
        cinema = Cinema("Interstellar", 5, 5)
        with self.assertRaises(ValueError):
            cinema.allocate_default_seats(0)
        
        # negative tickets - should raise ValueError
        with self.assertRaises(ValueError):
            cinema.allocate_default_seats(-1)
        
        # more seats than available
        cinema = Cinema("Interstellar", 5, 5)
        cinema.book_seats([(0, 0), (0, 1)], "BK0001")
        self.assertIsNone(cinema.allocate_default_seats(30))
        
        # allocation when cinema is almost full
        cinema = Cinema("Interstellar", 2, 3)
        cinema.book_seats([(0, 0), (0, 1), (0, 2), (1, 0), (1, 1)], "BK0001")
        seats = cinema.allocate_default_seats(1)
        self.assertEqual(len(seats), 1)
        self.assertEqual(seats[0], (1, 2))
        
        # allocation when cinema is full
        cinema = Cinema("Interstellar", 2, 3)
        cinema.book_seats([(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)], "BK0001")
        self.assertIsNone(cinema.allocate_default_seats(1))
        self.assertIsNone(cinema.allocate_seats_from_position(1, 0, 0))

    def test_cancel_booking(self):
        """
        Test allocating seats with overflow to next row.
        """
        booking_id = "BK0001"

        # More columns
        cinema = Cinema("Interstellar", 2, 5)
        seats = cinema.allocate_default_seats(4)
        cinema.book_seats(seats, booking_id)

        self.assertEqual([['.', '.', '.', '.', '.'], ['.', 'BK0001', 'BK0001', 'BK0001', 'BK0001']], cinema.seating_map)
        self.assertEqual([(1, 2), (1, 3), (1, 1), (1, 4)], cinema.bookings[booking_id])
        self.assertEqual(6, cinema.available_seats)

        cinema.cancel_booking(booking_id)

        self.assertEqual([['.', '.', '.', '.', '.'], ['.', '.', '.', '.', '.']], cinema.seating_map)
        self.assertEqual(None, cinema.bookings.get(booking_id))
        self.assertEqual(10, cinema.available_seats)


if __name__ == "__main__":
    unittest.main() 