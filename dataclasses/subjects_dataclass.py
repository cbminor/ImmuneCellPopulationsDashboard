from dataclasses import dataclass
from project_dataclass import Project

@dataclass
class Subject:
    """ A class representing a subject within a immune cell population project """
    subject_id: str
    condition: str
    age: int
    sex: str
    treatment: str
    response: bool
    project: Project
