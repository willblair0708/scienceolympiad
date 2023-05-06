import pandas as pd
from matchmaking import match_mentors_to_sessions, read_mentor_csv, create_schedule_list, Mentor


def create_output_dataframe(schedules):
    data = []

    for schedule in schedules:
        for mentor in schedule.mentors:
            data.append({
                'Mentor Full Name': mentor.full_name,
                'Day': schedule.day.capitalize(),
                'Time': schedule.time,
                'School': schedule.school,
            })

    return pd.DataFrame(data)


def write_schedule_to_csv(df, output_file):
    df.to_csv(output_file, index=False)


if __name__ == '__main__':
    input_file = 'mentors.csv'
    output_file = 'matched_schedule.csv'

    df = read_mentor_csv(input_file)
    mentors = [Mentor.from_dataframe_row(row) for _, row in df.iterrows()]
    schedules = create_schedule_list(df)
    matched_schedules = match_mentors_to_sessions(mentors, schedules)

    output_df = create_output_dataframe(matched_schedules)
    write_schedule_to_csv(output_df, output_file)
