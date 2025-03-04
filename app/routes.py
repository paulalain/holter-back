from flask import Blueprint, request, jsonify
from app.services.ecg_analysis_service import ECGAnalysisService

bp = Blueprint("api", __name__)

@bp.route("/delineation", methods=["POST"])
def delineation():
    """
    Handles the ECG file upload and returns heart rate statistics.

    This route expects a POST request containing a CSV file with ECG data. It processes the data, 
    performs heart rate analysis, and returns a JSON response with the following heart rate statistics:
        - mean_heart_rate: The average heart rate (bpm)
        - min_heart_rate: The minimum heart rate (bpm)
        - min_heart_rate_timestamp: The timestamp of the minimum heart rate
        - max_heart_rate: The maximum heart rate (bpm)
        - max_heart_rate_timestamp: The timestamp of the maximum heart rate

    If the file is not provided or is in an invalid format, an appropriate error message is returned.

    Request:
        - A file named 'record' must be included in the POST request.
        - The file must be in CSV format.

    Responses:
        - 200 OK: Returns heart rate statistics in the following JSON format:
            {
                "mean_heart_rate": <float>,   # Average heart rate (bpm)
                "min_heart_rate": <float>,    # Minimum heart rate (bpm)
                "min_heart_rate_timestamp": <int>,  # Timestamp of the minimum heart rate
                "max_heart_rate": <float>,    # Maximum heart rate (bpm)
                "max_heart_rate_timestamp": <int>   # Timestamp of the maximum heart rate
            }
        - 400 Bad Request: If no file is provided, the file is empty, or the file format is invalid.
        - 500 Internal Server Error: If there is an issue processing the file or performing the analysis.
    """

    # Check if a file is sent with the request (with the key 'record')
    if "record" not in request.files:
        return jsonify({"error": "No file provided. Please upload a CSV file."}), 400

    # Retrieve the file sent in the request
    record = request.files["record"]

    # Check if the file is empty
    if not record.filename or record.filename == "":
        return jsonify({"error": "The file is empty. Please upload a valid CSV file."}), 400

    # Check if the file has a CSV extension
    if not record.filename.endswith(".csv"):
        return jsonify({"error": "Invalid file format. Only CSV files are supported."}), 400

    try:
        # Analyze the ECG and return the results as a dictionary
        ecg_analysis_service = ECGAnalysisService(record)

        return jsonify(ecg_analysis_service.analyze_ecg()), 200

    except FileNotFoundError:
        return jsonify({"error": "The ECG file could not be found or read. Please check the file format."}), 500

    except ValueError as ve:
        return jsonify({"error": f"Data issue: {str(ve)}"}), 400

    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
