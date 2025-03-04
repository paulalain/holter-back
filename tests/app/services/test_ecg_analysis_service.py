import unittest
from io import StringIO
from app.services.ecg_analysis_service import ECGAnalysisService

class TestECGAnalysisService(unittest.TestCase):
    """
    Unit tests for the ECGAnalysisService class.
    """

    def setUp(self):
        """
        Set up a mock CSV record for testing purposes.
        """
        # Sample ECG data (QRS waves, onset, offset, tags)
        self.mock_csv_data = """QRS,800,900,normal
T,1000,1100
QRS,1900,2100
QRS,3200,3250,premature
P,3300, 3400,
QRS,4000,4020
QRS,8000,8100"""
        
        # Use StringIO to simulate a file object from the string data
        self.mock_file = StringIO(self.mock_csv_data)
        
        # Create an instance of ECGAnalysisService with the mock file
        self.service = ECGAnalysisService(self.mock_file)

    def test_analyze_ecg(self):
        """
        Test the `analyze_ecg` method of ECGAnalysisService.
        """
        
        # Call the analyze_ecg method
        result = self.service.analyze_ecg()

        # Assert that the result is a dictionary
        self.assertIsInstance(result, dict)
        
        # Assert that the keys in the result dictionary are as expected
        self.assertIn("mean_heart_rate", result)
        self.assertIn("min_heart_rate", result)
        self.assertIn("min_heart_rate_timestamp", result)
        self.assertIn("max_heart_rate", result)
        self.assertIn("max_heart_rate_timestamp", result)

        # Assert the values returned are correct
        self.assertEqual(result["mean_heart_rate"], 48.11)
        self.assertEqual(result["min_heart_rate"], 14.85)
        self.assertEqual(result["max_heart_rate"], 76.43)
        self.assertEqual(result["min_heart_rate_timestamp"], 8000)
        self.assertEqual(result["max_heart_rate_timestamp"], 4000)

if __name__ == "__main__":
    unittest.main()
