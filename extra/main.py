from read_csv import read_mentor_csv
from mentor import Mentor
from matchmaking import create_schedule_list, match_mentors_to_sessions
from output import create_output_dataframe, write_schedule_to_csv

def main(input_file, output_file):
    # Read mentor data from the CSV file
    df = read_mentor_csv(input_file)

    # Create mentor and schedule objects
    mentors = [Mentor.from_dataframe_row(row) for _, row in df.iterrows()]
    schedules = create_schedule_list(df)

    # Match mentors to schedules
    matched_schedules = match_mentors_to_sessions(mentors, schedules)

    # Create output dataframe and write to a CSV file
    output_df = create_output_dataframe(matched_schedules)
    write_schedule_to_csv(output_df, output_file)


if __name__ == '__main__':
    input_file = 'availability.csv'
    output_file = 'matched_schedule.csv'

    main(input_file, output_file)
