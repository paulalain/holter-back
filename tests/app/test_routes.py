import unittest
from io import BytesIO
from flask import Flask, jsonify
from app.routes import bp  # Assuming you have your routes defined in app.routes
from unittest.mock import patch

# Create a Flask app instance for testing
class TestRoutes(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up the Flask app and client for testing"""
        cls.app = Flask(__name__)
        cls.app.register_blueprint(bp)
        cls.client = cls.app.test_client()

    # Mock ECGAnalysisService to simulate the analysis without actual processing
    class MockECGAnalysisService:
        def __init__(self, file):
            pass

        def analyze_ecg(self):
            # Return a mock response as if the analysis was successful
            return {
                "mean_heart_rate": 72.5,
                "min_heart_rate": 60.0,
                "min_heart_rate_timestamp": 12345,
                "max_heart_rate": 95.0,
                "max_heart_rate_timestamp": 56789
            }

    # Test case for a valid CSV file upload
    def test_valid_file_upload(self):
        # Prepare a mock CSV file
        csv_data = "timestamp,heart_rate\n1617219234,72\n1617219235,75\n1617219236,70\n"
        data = {
            'record': (BytesIO(csv_data.encode('utf-8')), 'ecg_data.csv')
        }

        with patch('app.routes.ECGAnalysisService', self.MockECGAnalysisService):
            response = self.client.post('/delineation', data=data)

        self.assertEqual(response.status_code, 200)
        response_json = response.get_json()
        self.assertEqual(response_json['mean_heart_rate'], 72.5)
        self.assertEqual(response_json['min_heart_rate'], 60.0)
        self.assertEqual(response_json['max_heart_rate'], 95.0)

    # Test case for missing file in the request
    def test_missing_file(self):
        response = self.client.post('/delineation')
        self.assertEqual(response.status_code, 400)
        response_json = response.get_json()
        self.assertEqual(response_json['error'], "No file provided. Please upload a CSV file.")

    # Test case for an empty file
    def test_empty_file(self):
        data = {'record': (BytesIO(b''), 'empty.csv')}

        with patch('app.routes.ECGAnalysisService', self.MockECGAnalysisService):
            response = self.client.post('/delineation', data=data)

        self.assertEqual(response.status_code, 400)
        response_json = response.get_json()
        self.assertEqual(response_json['error'], "The file is empty. Please upload a valid CSV file.")

    # Test case for invalid file format (not CSV)
    def test_invalid_file_format(self):
        data = {'record': (BytesIO(b'not csv data'), 'invalid.txt')}

        with patch('app.routes.ECGAnalysisService', self.MockECGAnalysisService):
            response = self.client.post('/delineation', data=data)

        self.assertEqual(response.status_code, 400)
        response_json = response.get_json()
        self.assertEqual(response_json['error'], "Invalid file format. Only CSV files are supported.")

    # Test case for an exception during the ECG analysis (simulating server-side error)
    def test_internal_server_error(self):
        # Mock the ECGAnalysisService to raise an exception
        class FaultyECGAnalysisService:
            def __init__(self, file):
                pass

            def analyze_ecg(self):
                raise Exception("Simulated server error")

        data = {'record': (BytesIO(b'1,2\n'), 'data.csv')}

        with patch('app.routes.ECGAnalysisService', FaultyECGAnalysisService):
            response = self.client.post('/delineation', data=data)

        self.assertEqual(response.status_code, 500)
        response_json = response.get_json()
        self.assertEqual(response_json['error'], "An unexpected error occurred: Simulated server error")

# Run the tests
if __name__ == '__main__':
    unittest.main()

