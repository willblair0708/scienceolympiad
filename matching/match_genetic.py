import pandas as pd
import numpy as np
from geneticalgorithm2 import geneticalgorithm2 as ga2

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

# Sort mentors by head_mentor status
mentor_df['head_mentor_rank'] = mentor_df['head_mentor'].map({'Yes': 1, 'Maybe': 2, 'No': 3})
mentor_df.sort_values(by=['head_mentor_rank'], inplace=True)

# Create a cost matrix
cost_matrix = []

max_mentors_per_school = 3  # Set the maximum number of mentors per school

for _, mentor in mentor_df.iterrows():
    mentor_row = []
    for _, school in school_df.iterrows():
        availability_score = compare_availability(mentor, school)
        mentor_row.extend([-availability_score] * max_mentors_per_school)  # Duplicate schools
    cost_matrix.append(mentor_row)

# Define the fitness function
def fitness_function(individual):
    individual = np.array(individual, dtype=int)
    score = 0
    school_counts = np.zeros(len(school_df), dtype=int)
    head_mentor_counts = np.zeros(len(school_df), dtype=int)

    for mentor_idx, school_idx in enumerate(individual):
        mentor = mentor_df.iloc[mentor_idx]
        school = school_df.iloc[school_idx // max_mentors_per_school]

        score += cost_matrix[mentor_idx][school_idx]

        school_counts[school_idx // max_mentors_per_school] += 1

        if mentor["head_mentor"].lower() in ["yes", "maybe"]:
            head_mentor_counts[school_idx // max_mentors_per_school] += 1

    # Penalize if more than max_mentors_per_school mentors are assigned to a school
    score += 1000 * np.sum((school_counts - max_mentors_per_school)[school_counts > max_mentors_per_school])

    # Penalize if a school does not have a head_mentor
    score += 1000 * np.sum(head_mentor_counts == 0)

    return score

# Set the Genetic Algorithm parameters
algorithm_param = {'max_num_iteration': 100,
                   'population_size': 200,
                   'mutation_probability': 0.2,
                   'elit_ratio': 0.01,
                   'crossover_probability': 0.8,
                   'parents_portion': 0.3,
                   'crossover_type': 'uniform',
                   'max_iteration_without_improv': None}

# Initialize the Genetic Algorithm
model = ga2(function=fitness_function, dimension=len(cost_matrix), variable_type='int', variable_boundaries=np.array([[0, len(cost_matrix) - 1]] * len(cost_matrix)), algorithm_parameters=algorithm_param)

# Run the Genetic Algorithm
model.run()

# Get the best individual
best_individual = model.result['variable']

# Store matches in a DataFrame
matches = []

for mentor_idx, school_idx in zip(best_individual, np.argmin(cost_matrix, axis=1)):
    mentor_name = mentor_df.loc[mentor_idx, "mentor_name"]
    school_name = school_df.loc[school_idx // max_mentors_per_school, "school"]
    head_mentor = mentor_df.loc[mentor_idx, "head_mentor"]
    matches.append((mentor_name, school_name, head_mentor))

match_df = pd.DataFrame(matches, columns=["Mentor Name", "School", "Head Mentor"])
# Sort the DataFrame alphabetically by school
match_df.sort_values(by=['School'], inplace=True)

# Write the sorted DataFrame to a CSV file
match_df.to_csv("data/optimized_mentor_school_matches.csv", index=False)