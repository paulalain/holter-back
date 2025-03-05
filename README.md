# Holter Record Summary App

A normal heartbeat produces three entities on the ECG — a P wave, a QRS complex, a T wave.
[See Electrocardiography theory here.](https://en.wikipedia.org/wiki/Electrocardiography#Theory)

Identifying those entities in a signal is called delineation.
[Here are CSV of an algorithm output for a 24h ECG](https://cardiologs-public.s3.amazonaws.com/python-interview/record.csv)

Rows have the following fields:
   - Wave type: P, QRS, T or INV (invalid)
   - Wave onset: Start of the wave in ms
   - Wave offset: End of the wave in ms
    - Optionally, a list of wave tags

Write a simple application, including a web interface and an HTTP server with the following
functionalities:
- Providing the following measurements to a physician when a delineation file is uploaded on the app with a POST /delineation request:
    - The mean heart rate of the recording (Frequency at which QRS complexes appear).
    - The minimum and maximum heart rate, each with the time at which they happened.
- [BONUS QUESTION] Providing a possibility to set up the date and the time of the recording, as they are not included in the file. This should impact the date and the time seen in the measurements.

Cardiologs should be able to recover your work, understand it, trust it easily, maintain it, make changes to it, etc

---

## Solution

It can be tested here (free plan, it could take 60s to be launched) : 

`https://holter-back.onrender.com/delineation POST`

I chose Flask as the REST framework for this project due to its simplicity and ease of use, especially when building lightweight web applications. Having worked with dataframes and pandas in the past, I found it to be a great fit for processing and analyzing the ECG data.

To start, I implemented the necessary routes in Flask and added some basic validation for the uploaded file to ensure it's in the correct format.

For the ECG analysis, I focused on isolating the QRS complexes, which are key to calculating heart rate. I created a new column in the dataframe to represent the R timestamp, assuming that the R-wave occurs at the midpoint of the QRS complex (though this is an approximation, as the exact position can vary).

Next, I created another column to calculate the R-R interval, which is the time difference between two successive R waves. Using these R-R intervals, I calculated the heart rate (BPM) for each interval with the formula 𝑓 = 1/𝑇 where 𝑇 is the R-R interval in milliseconds.

Finally, I leveraged pandas to compute the mean, minimum, and maximum heart rates based on the BPM values, providing a summary of the ECG data.

---

## Results with the given file

Here are the results from the API based on the provided file:

```
{
    "max_heart_rate": 606.06,
    "max_heart_rate_timestamp": 76862748,
    "mean_heart_rate": 79.04,
    "min_heart_rate": 17.64,
    "min_heart_rate_timestamp": 1836313
}
```

The mean heart rate appears to be reasonable, but both the maximum heart rate and minimum heart rate seem unusual. The maximum heart rate (606.06 bpm) is too high, and the minimum heart rate (17.64 bpm) is too low.

Upon inspecting the file at the timestamps for the maximum and minimum heart rates, it seems that the time intervals between the QRS signals are abnormally small for the maximum heart rate, and too large for the minimum heart rate. This discrepancy may indicate that the data is not accurate or that the file contains errors.

Next steps:

- Verify with the team if the file is valid for a human ECG recording.
- Check if we have to remove QRS values where INV data are present in between QRS.
- Consider adding features to handle these anomalies, such as applying statistical methods (e.g., percentiles) to identify and correct outliers in the timestamp data.

  With the 0.5/99.5 percentile, we can have better results:

  ```
   df = self.filter_by_percentile(df, RECORD_R_R_INTERVAL, 0.1, 99.9)

   def filter_by_percentile(self, df, column, lower=0, upper=100):
     lower_bound = df[column].quantile(lower / 100)
     upper_bound = df[column].quantile(upper / 100)
     
     return df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
  ```

  The results look more accurate, but on correct files we could miss some data.

   ```
     {
       "max_heart_rate": 203.74,
       "max_heart_rate_timestamp": 25087882,
       "mean_heart_rate": 78.95,
       "min_heart_rate": 35.75,
       "min_heart_rate_timestamp": 50086370
      }
   ```

- Another solution could be to use zscore and remove RECORD_R_R_INTERVAL values with a zscore higher than the threshold.

  ```
    def filter_by_zscore(self, df, threshold_positive=2.5, threshold_negative=-1.85):
        # Calculate the Z-scores
        z_scores = zscore(df[RECORD_R_R_INTERVAL])
        
        # Remove rows where the Z-score exceeds the positive threshold or is below the negative threshold
        return df[(z_scores <= threshold_positive) & (z_scores >= threshold_negative)]
  ```

  The results look more accurate:

   ```
    {
        "max_heart_rate": 209.79,
        "max_heart_rate_timestamp": 25447444,
        "mean_heart_rate": 79.01,
        "min_heart_rate": 33.79,
        "min_heart_rate_timestamp": 73088109
    }
   ```

Using Jupyter, we could also find a good threshold. Here are the values for R-R intervals and BPM without the filter. We can see some outliers values.

<img width="925" alt="Capture d’écran 2025-03-05 à 16 25 25" src="https://github.com/user-attachments/assets/a4b5986b-bbed-4a0d-92bc-533d9b6daeb6" />

Using -1.85 as a negative threshold and 2.5 as a positive threshold, it looks like we don't miss data, and we can remove outliers.

<img width="910" alt="Capture d’écran 2025-03-05 à 16 48 00" src="https://github.com/user-attachments/assets/95b86fa0-8ba9-4615-af90-b04c5ae500f0" />

---

## 📌 Requirements
- **Python 3.10+**
- **Docker (optional, for containerized deployment)**

---

## 🔧 Installation & Running Locally

1️⃣ **Clone the repository**
```sh
git clone git@github.com:paulalain/holter-back.git
cd holter-back
```

2️⃣ **Create a virtual environment (optional but recommended)**
```sh
python -m venv venv
source venv/bin/activate
```

3️⃣ **Install dependencies**
```sh
pip install -r requirements.txt
```

4️⃣ **Run the application**
```sh
python wsgi.py
```

The API will be available at **http://127.0.0.1:5000/delineation**.

---

## 🚀 Deployment with Docker

1️⃣ **Build the Docker image**
```sh
docker build -t holter-back .
```

2️⃣ **Run the Docker container**
```sh
docker run -p 5000:5000 holter-back
```

The API will be available at **http://localhost:5000/delineation**.

---

## 📤 Usage

### **POST /delineation**
- **Request:** Upload a CSV file using `multipart/form-data`.
    - A file named 'record' must be included in the POST request.
    - The file must be in CSV format.
- **Response:** 
        - 200 OK: Returns heart rate statistics in the following JSON format:
```json
  {
            "mean_heart_rate": <float>,   # Average heart rate (bpm)
            "min_heart_rate": <float>,    # Minimum heart rate (bpm)
            "min_heart_rate_timestamp": <int>,  # Timestamp of the minimum heart rate
            "max_heart_rate": <float>,    # Maximum heart rate (bpm)
            "max_heart_rate_timestamp": <int>   # Timestamp of the maximum heart rate
        }
```
    - 400 Bad Request: If no file is provided, the file is empty, or the file format is invalid.
    - 500 Internal Server Error: If there is an issue processing the file or performing the analysis.

#### **Example Request (cURL)**
```sh
curl -X POST http://localhost:5000/delineation \
     -F "record=@sample.csv"
```

#### **Example Response**
```json
{
    "mean_heart_rate": 72.5,
    "min_heart_rate": 60.0,
    "min_heart_rate_timestamp": 12345,
    "max_heart_rate": 95.0,
    "max_heart_rate_timestamp": 56789
}
```

---

## 📜 License
This project is licensed under the MIT License.
