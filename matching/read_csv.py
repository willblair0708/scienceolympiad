import pandas as pd

def read_mentor_csv(file_path):
    """
    Read and parse the CSV file containing mentor information.

    Args:
    file_path (str): Path to the CSV file containing mentor information.

    Returns:
    pd.DataFrame: A dataframe containing the mentor data.
    """
    mentor_data = pd.read_csv(file_path)

    # Renaming columns to make them more readable and easier to work with
    # Define the columns dictionary with the new column names
    columns = {
        'Full Name:': 'full_name',
        'What was your status in the Fall?': 'status',
        'If you mentored in Fall 2022, select which school you supported:': 'school_supported',
        'Are you interested in being a Head Mentor?': 'head_mentor',
        'Select any and all sessions you would be available to mentor at:': 'availability_monday',
        "If you aren\'t available for any of the sessions above, but have other availability on Mondays, please describe below:": 'availability_monday_other',
        "Select any and all sessions you would be available to mentor at:.1": 'availability_tuesday',
        "If you aren\'t available for any of the sessions above, but have other availability on Tuesdays, please describe below:": 'availability_tuesday_other',
        "Select any and all sessions you would be available to mentor at:.2": 'availability_wednesday',
        "If you aren\'t available for any of the sessions above, but have other availability on Wednesdays, please describe below:": 'availability_wednesday_other',
        "Select any and all sessions you would be available to mentor at:.3": 'availability_thursday',
        "If you aren\'t available for any of the sessions above, but have other availability on Thursdays, please describe below:": 'availability_thursday_other',
        "Select any and all sessions you would be available to mentor at:.4": 'availability_friday',
        "If you aren\'t available for any of the sessions above, but have other availability on Fridays, please describe below:": 'availability_friday_other',
        'Are you interested in mentoring during Intersession?': 'intersession_interest',
        'Select when you are available Jan. 3rd - 20th:': 'intersession_availability',
        'How many sessions are you interested in supporting each week?': 'intersession_sessions',
        'Anything else you want to share?': 'additional_info'
    }

    # remove leading/trailing whitespace from column names
    columns = {col.strip(): val for col, val in columns.items()}
    mentor_data.rename(columns=columns, inplace=True)

    return mentor_data

if __name__ == '__main__':
    file_path = 'data/availability.csv'
    mentor_data = read_mentor_csv(file_path)
    mentor_data.to_csv('data/mentor_data.csv', index=False)

