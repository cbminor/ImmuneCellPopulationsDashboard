from dataclasses import dataclass
from subjects_dataclass import Subject

@dataclass
class Sample:
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