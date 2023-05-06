import csv
import datetime
import pandas as pd

from mentor import Mentor, read_mentor_csv

def read_school_csv(file_path):
    schools = []
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
    df = pd.read_csv(file_path)

    # Convert column names to lowercase
    df.columns = df.columns.str.lower()

    for _, row in df.iterrows():
        school_name = row['school']
        for day in days:
            time_str = row[day]
            if not pd.isna(time_str):
                start_time, end_time = time_str.split(' - ')
                start_timestamp = pd.Timestamp(start_time).strftime('%H:%M')
                end_timestamp = pd.Timestamp(end_time).strftime('%H:%M')
                time_range = f"{start_timestamp}-{end_timestamp}"
                schools.append((school_name, day, time_range))

    return schools

class Schedule:
    def __init__(self, day, time, school, school_name, mentors=None):
        self.day = day
        self.time = time
        self.school = school
        self.school_name = school_name
        self.mentors = mentors if mentors is not None else []

    def add_mentor(self, mentor):
        self.mentors.append(mentor)

    def is_mentor_available(self, mentor):
        return self.time in mentor.get_availability_for_school(self.day)

    def assign_mentors(self, mentors):
        for mentor in mentors:
            if self.is_mentor_available(mentor):
                self.add_mentor(mentor)

    def __repr__(self):
        return f'day={self.day}, time={self.time}, school={self.school}, school_name={self.school_name}, mentors={self.mentors})'

if __name__ == '__main__':
    mentor_file_path = 'mentor_availability.csv'
    mentors = read_mentor_csv(mentor_file_path)

    school_file_path = 'schools.csv'
    schools = read_school_csv(school_file_path)

    sessions = []
    for school_name, day, time in schools:
        session = Schedule(day, time, school_name.split()[-1], school_name)
        session.assign_mentors(mentors)
        sessions.append(session)

    for session in sessions:
        print(session)
