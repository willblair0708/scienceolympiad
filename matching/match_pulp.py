import pandas as pd
import numpy as np
from scipy.optimize import linear_sum_assignment

# Read CSV files
mentor_df = pd.read_csv("data/mentor_availability.csv")
school_df = pd.read_csv("data/modified_schools.csv")

# Preprocess data
mentor_df.fillna("", inplace=True)
school_df.fillna("", inplace=True)

def check_overlap(mentor_range, school_range):
    mentor_start, mentor_end = [pd.to_datetime(t) for t in mentor_range.split('-')]
    school_start, school_end = [pd.to_datetime(t) for t in school_range.split('-')]

    return (mentor_start <= school_end) and (school_start <= mentor_end)

def compare_availability(mentor, school):
    overlap_count = 0
    for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']:
        mentor_slots = mentor[day].split()
        school_slots = school[day].split()

        for mentor_slot in mentor_slots:
            for school_slot in school_slots:
                if check_overlap(mentor_slot, school_slot):
                    overlap_count += 1

    # Add bonus points for supported schools
    if mentor["school_supported"] == school["school"]:
        overlap_count += 5

    return overlap_count

# Remove mentors with no availability
mentor_df['total_availability'] = mentor_df[['monday', 'tuesday', 'wednesday', 'thursday', 'friday']].apply(lambda x: ''.join(x), axis=1)
mentor_df = mentor_df[mentor_df['total_availability'] != ""]

# Reset index of mentor_df
mentor_df.reset_index(drop=True, inplace=True)

# Create a cost matrix
cost_matrix = []

for _, mentor in mentor_df.iterrows():
    mentor_row = []
    for _, school in school_df.iterrows():
        availability_score = compare_availability(mentor, school)
        
        # Penalize mentors who are not suitable as head mentors
        if mentor["head_mentor"].lower() not in ["yes", "maybe"]:
            availability_score -= 1000

        # Penalize mentors who have no overlapping availability with the school
        if availability_score == 0:
            availability_score -= 1000

        mentor_row.append(-availability_score)
    cost_matrix.append(mentor_row)
# Apply the Hungarian Algorithm
row_ind, col_ind = linear_sum_assignment(cost_matrix)

# Create a DataFrame with the matched mentors and schools
matches = []
school_mentor_counts = {school: 0 for _, school in school_df["school"].items()}
for mentor_idx, school_idx in zip(row_ind, col_ind):
    mentor = mentor_df.iloc[mentor_idx]
    school = school_df.iloc[school_idx]
    
    # Check if the school already has 3 mentors
    if school_mentor_counts[school["school"]] < 3:
        matches.append([mentor["mentor_name"], school["school"], mentor["head_mentor"]])
        school_mentor_counts[school["school"]] += 1
print(matches)

# Add mentors with "no" as head_mentor
no_head_mentor_df = mentor_df[mentor_df["head_mentor"].str.lower() == "no"]
for _, mentor in no_head_mentor_df.iterrows():
    school_idx = np.argmin([compare_availability(mentor, school) for _, school in school_df.iterrows()])
    school = school_df.iloc[school_idx]
    
    # Check if the school already has 3 mentors
    if school_mentor_counts[school["school"]] < 3:
        matches.append([mentor["mentor_name"], school["school"], mentor["head_mentor"]])
        school_mentor_counts[school["school"]] += 1

match_df = pd.DataFrame(matches, columns=["Mentor Name", "School", "Head Mentor"])

# Sort the DataFrame alphabetically by school
match_df.sort_values(by=['School'], inplace=True)

# Write the sorted DataFrame to a CSV file
match_df.to_csv("data/optimized_mentor_school_matches.csv", index=False)