import unittest
import sys

from unit_tests.test_cinema import TestCinema
from e2e_tests.test_booking_flow import TestBookingFlow

def run_all_tests():
    # Create test suite
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestCinema))
    suite.addTests(loader.loadTestsFromTestCase(TestBookingFlow))
    
    # Run tests
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(suite)

    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    sys.exit(run_all_tests()) 