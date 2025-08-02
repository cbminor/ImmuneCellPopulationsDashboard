import pandas as pd
from db import Database

# TODO: Update code to be a reusable script
# TODO: Add data validation (Currently verifying manually in Excel)


def parse_cell_counts_row(row):
    project = tuple([row.project])
    subject = (row.subject, row.condition, row.age, row.sex, row.treatment, row.response, row.project)
    sample = (row["sample"], row.sample_type, row.time_from_treatment_start, row.b_cell, row.cd8_t_cell, 
              row.cd4_t_cell, row.nk_cell, row.monocyte, row.subject)
    return pd.Series([project, subject, sample], index=["project_tuple", "subject_tuple", "sample_tuple"])

file = pd.read_csv("cell-count.csv")
results = file.apply(parse_cell_counts_row, axis=1)
print("Projects Before: ", results.project_tuple.unique())
projects = results.project_tuple.unique().tolist()
subjects = results.subject_tuple.unique().tolist()
samples = results.sample_tuple.unique().tolist()
print("Projects: ", projects)


db = Database(db_path="cell_counts_db.db")
db.initialize_database(schema_path="schema.sql")
db.add_projects(projects=projects)
db.add_subjects(subjects=subjects)
db.add_samples(samples=samples)



    
    

                    
            


