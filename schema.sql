CREATE TABLE IF NOT EXISTS projects (
    project_id VARCHAR PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS subjects (
    subject_id VARCHAR PRIMARY KEY,
    condition VARCHAR(15),
    age INT,
    sex CHAR(1),
    treatment VARCHAR(15),
    response BOOLEAN,
	project VARCHAR,
	FOREIGN KEY (project) REFERENCES projects(project_id)
);

CREATE TABLE IF NOT EXISTS samples (
    sample_id VARCHAR PRIMARY KEY,
    sample_type VARCHAR,
    time_from_treatment_start INT,
    b_cell INT,
    cd8_t_cell INT,
    cd4_t_cell INT,
    nk_cell INT,
    monocyte INT,
	subject VARCHAR,
	FOREIGN KEY (subject) REFERENCES subjects(subject_id)
);