from flask import Flask
import pandas as pd
import numpy as np
from scipy.stats import zscore

app = Flask(__name__)

# Constants for column names in the ECG data
WAVE_TYPE_QRS = "QRS"
RECORD_WAVE_TYPE = "wave_type"
RECORD_ONSET = "onset"
RECORD_OFFSET = "offset"
RECORD_TAGS = "tags"
RECORD_R_TIMESTAMP = "r_offset"
RECORD_R_R_INTERVAL = "r_r_interval"
RECORD_BPM = "bpm"

class ECGAnalysisService:
    """
    ECGAnalysisService class is responsible for processing ECG records and calculating
    heart rate statistics based on the QRS complex.

    Attributes:
        record: Path to the ECG record file (CSV format).
    """

    def __init__(self, record):
        """
        Initializes the ECGAnalysisService with a given ECG record file.
        
        Parameters:
            record (str): Path to the ECG record file.
        """
        self.record = record

    def analyze_ecg(self):
        """
        Analyzes the ECG data by calculating heart rate based on QRS complex intervals.

        This method:
        - Loads ECG data from a CSV file.
        - Filters data for QRS complexes.
        - Calculates the R-wave timestamp (approximated as the midpoint of the QRS complex).
        - Computes the R-R interval (the time between successive R-waves).
        - Calculates the BPM (beats per minute) based on the R-R interval.
        
        Returns:
            dict: A dictionary containing the mean, minimum, and maximum heart rate (BPM).
        """

        # Load ECG data from the provided CSV file, specifying column names
        df = pd.read_csv(self.record, names=[
            RECORD_WAVE_TYPE, 
            RECORD_ONSET, 
            RECORD_OFFSET,
            RECORD_TAGS
        ], on_bad_lines="skip", engine="python")
    
        # Filter data to only include rows where the wave type is 'QRS'
        df = df[df[RECORD_WAVE_TYPE] == WAVE_TYPE_QRS]
        
        # Calculate the R-wave timestamp (approximated as the midpoint of the QRS complex)
        df[RECORD_R_TIMESTAMP] = df[RECORD_ONSET] + (df[RECORD_OFFSET] - df[RECORD_ONSET]) / 2
        
        # Compute the R-R interval (the difference between successive R-wave timestamps)
        df[RECORD_R_R_INTERVAL] = df[RECORD_R_TIMESTAMP].diff()
        
        # Drop rows where R-R interval is NaN (i.e., missing values)
        df = df.dropna(subset=[RECORD_R_R_INTERVAL])

        df = self.filter_by_zscore(df, 2.5, -1.85)

        # Convert the R-R interval (in milliseconds) to heart rate (BPM) - f = 1/T
        df[RECORD_BPM] = 60000 / df[RECORD_R_R_INTERVAL]

        # Get min & max rows
        min_bpm_row = df.loc[df[RECORD_BPM].idxmin()]
        max_bpm_row = df.loc[df[RECORD_BPM].idxmax()]
        
        # Return the mean, minimum, and maximum BPM
        return {
            "mean_heart_rate": round(df[RECORD_BPM].mean(), 2),         # Mean heart rate
            "min_heart_rate": round(min_bpm_row[RECORD_BPM], 2),        # Minimum heart rate
            "min_heart_rate_timestamp": int(min_bpm_row[RECORD_ONSET]), # Minimum heart rate timestamp (QRS start)
            "max_heart_rate": round(max_bpm_row[RECORD_BPM], 2),        # Maximum heart rate
            "max_heart_rate_timestamp": int(max_bpm_row[RECORD_ONSET])  # Maximum heart rate timestamp (QRS start)
        }
    
    def filter_by_zscore(self, df, threshold_positive=2.5, threshold_negative=-1.85):
        # Calculate the Z-scores
        z_scores = zscore(df[RECORD_R_R_INTERVAL])
        
        # Remove rows where the Z-score exceeds the positive threshold or is below the negative threshold
        return df[(z_scores <= threshold_positive) & (z_scores >= threshold_negative)]
