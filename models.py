from pydantic import BaseModel

class Project(BaseModel):
    """ A data class to represent an Immune Cell Population Project """
    project_id: str

class Subject(BaseModel):
    """ A class representing a subject within a immune cell population project """
    subject_id: str
    condition: str
    age: int
    sex: str
    treatment: str
    response: bool
    project: Project

class Sample(BaseModel):
    """ A class representing an individual sample """   
    sample_id: str
    sample_type: str
    time_from_treatment_start: int
    b_cell: int
    cd8_t_cell: int
    cd4_t_cell: int
    nk_cell: int
    monocyte: int
    subject: Subject