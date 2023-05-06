import pandas as pd
from scipy.optimize import linear_sum_assignment

# Read CSV files
mentor_df = pd.read_csv("mentor_availability.csv")
school_df = pd.read_csv("modified_schools.csv")

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
    return overlap_count

# Create a cost matrix
cost_matrix = []

for _, mentor in mentor_df.iterrows():
    mentor_row = []
    for _, school in school_df.iterrows():
        mentor_row.append(-compare_availability(mentor, school))  # Negative values because we're maximizing overlap
    cost_matrix.append(mentor_row)

# Use Hungarian algorithm to find the best match
row_ind, col_ind = linear_sum_assignment(cost_matrix)

# Store matches in a DataFrame and write to a CSV file
matches = []

for mentor_idx, school_idx in zip(row_ind, col_ind):
    mentor_name = mentor_df.loc[mentor_idx, "mentor_name"]
    school_name = school_df.loc[school_idx, "school"]
    matches.append((mentor_name, school_name))

# Add mentors with no schools
for _, mentor in mentor_df.iterrows():
    if mentor["mentor_name"] not in [match[0] for match in matches]:
        matches.append((mentor["mentor_name"], ""))

match_df = pd.DataFrame(matches, columns=["Mentor Name", "School"])
match_df.to_csv("optimized_mentor_school_matches.csv", index=False)