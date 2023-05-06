import pandas as pd
import re

# Read the CSV file
df = pd.read_csv('data/schools.csv')

# Change column titles to lowercase
df.columns = [col.lower() for col in df.columns]

# Define a function to convert time to timestamp form
def time_to_timestamp(time_str):
    time_ranges = re.findall(r'(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})', time_str)
    time_timestamps = []
    for start, end in time_ranges:
        start_timestamp = pd.Timestamp(start).strftime('%H:%M')
        end_timestamp = pd.Timestamp(end).strftime('%H:%M')
        time_timestamps.append(f"{start_timestamp}-{end_timestamp}")
    return ','.join(list(set(time_timestamps)))

# Apply the conversion to each time column
time_columns = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
for col in time_columns:
    df[col] = df[col].apply(lambda x: time_to_timestamp(x.strip('[]')) if isinstance(x, str) else x)

# Save the modified CSV file
df.to_csv('data/modified_schools.csv', index=False)
