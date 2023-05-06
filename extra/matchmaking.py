import pandas as pd
from read_csv import read_mentor_csv
from mentor import Mentor
from schedule import Schedule


def create_schedule_list(df):
    unique_sessions = set()

    for index, row in df.iterrows():
        for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']:
            sessions = row[f'availability_{day}'].split(', ')
            unique_sessions.update(sessions)

    schedules = []
    for session in unique_sessions:
        if session == 'Unavailable':
            continue
        day, time_and_school = session.split(' ', 1)
        time, school = time_and_school.rsplit(' (', 1)
        school = school.rstrip(')')
        schedules.append(Schedule(day.lower(), time, school))

    return schedules


def match_mentors_to_sessions(mentors, schedules):
    for mentor in mentors:
        for schedule in schedules:
            if schedule.is_available():
                schedule.add_mentor(mentor)

    return schedules


if __name__ == '__main__':
    df = read_mentor_csv('mentor_data.csv')

    mentors = [Mentor.from_dataframe_row(row) for _, row in df.iterrows()]
    print(mentors)
    """
    schedules = create_schedule_list(df)

    matched_schedules = match_mentors_to_sessions(mentors, schedules)

    # Print the matched schedules
    for schedule in matched_schedules:
        print(schedule)
"""