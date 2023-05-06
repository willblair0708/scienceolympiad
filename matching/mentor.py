import csv
import re
import numpy as np
import pandas as pd

input_file = 'data/mentor_data.csv'
output_file = 'data/mentor_availability.csv'

def read_mentor_csv(file_path):
    mentors = []
    df = pd.read_csv(file_path)

    for _, row in df.iterrows():
        mentor = Mentor(row['mentor_name'],
                        row['monday'],
                        row['tuesday'],
                        row['wednesday'],
                        row['thursday'],
                        row['friday'])
        mentors.append(mentor)

    return mentors

class Mentor:
    def __init__(self, name, monday, tuesday, wednesday, thursday, friday):
        self.name = name
        self.availability = {
            'monday': self.parse_availability(monday),
            'tuesday': self.parse_availability(tuesday),
            'wednesday': self.parse_availability(wednesday),
            'thursday': self.parse_availability(thursday),
            'friday': self.parse_availability(friday)
        }

    def parse_availability(self, avail_str):
        return avail_str.split() if isinstance(avail_str, str) else []

    def get_availability_for_school(self, day):
        return self.availability[day]

    def __repr__(self):
        return f'Mentor(name={self.name}, availability={self.availability})'
    
def remove_brackets(text):
    return re.sub(r'\(.*?\)', '', text).strip()

def time_to_timestamp(time_str):
    time_ranges = re.findall(r'(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})', time_str)
    time_timestamps = []
    for start, end in time_ranges:
        start_timestamp = pd.Timestamp(start).strftime('%H:%M')
        end_timestamp = pd.Timestamp(end).strftime('%H:%M')
        time_timestamps.append(f"{start_timestamp}-{end_timestamp}")
    return list(set(time_timestamps))

with open(input_file, 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    mentors = []

    for row in reader:
        mentor = {}
        mentor['mentor_name'] = row['full_name']
        mentor['head_mentor'] = row['head_mentor']
        mentor['school_supported'] = row['school_supported']
        mentor['monday'] = ' '.join(time_to_timestamp(remove_brackets(row['availability_monday'].replace("Monday ", ""))))
        mentor['tuesday'] = ' '.join(time_to_timestamp(remove_brackets(row['availability_tuesday'].replace("Tuesday ", ""))))
        mentor['wednesday'] = ' '.join(time_to_timestamp(remove_brackets(row['availability_wednesday'].replace("Wednesday ", ""))))
        mentor['thursday'] = ' '.join(time_to_timestamp(remove_brackets(row['availability_thursday'].replace("Thursday ", ""))))
        mentor['friday'] = ' '.join(time_to_timestamp(remove_brackets(row['availability_friday'].replace("Friday ", ""))))
        mentors.append(mentor)

with open(output_file, 'w', newline='') as csvfile:
    fieldnames = ['mentor_name','head_mentor', 'school_supported', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for mentor in mentors:
        writer.writerow(mentor)
