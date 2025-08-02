import os
import sqlite3
from models import Project, Subject, Sample
from typing import List, Tuple

class Database:
    """ 
    A class containing methods related to database initialization and connection
    """

    def __init__(self, db_path: str):
        """ Initiizes the database class with the path to the database 
        
        Args:
            db_path: The path to the database 
        """
        self.db_path = db_path

    def _connect(self):
        """ Returns a connection to the sqlite database 
        
        Returns:
            Connection to a sqlite database
        """
        return sqlite3.connect(self.db_path)

    def initialize_database(self, schema_path: str) -> None:
        """ Initializes a sqlite database based on the given schema 
        
        Args:
            schema_path (str): The path to the sql file containing the db schema

        Raises:
            FileNotFoundError: If the schema file does not exist.
            FileExistsError: If the DB already exists
            RuntimeError: If a SQL or I/O error occurs during intialization.
        """

        if not os.path.exists(schema_path):
            raise FileNotFoundError(f"Schema file at {schema_path} does not exist.")
        
        if  os.path.exists(self.db_path):
            raise FileExistsError(f"Database {self.db_path} already exists.")
        
        try:
            with open(schema_path, "r") as f:
                schema = f.read()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.executescript(schema)
            conn.commit()
        except Exception as err:
            raise RuntimeError(f"Failed to initialize the database. Process failed with the following error: {err}")
        finally:
            try:
                conn.close() # type: ignore
            except:
                pass

    def _insert_many_db_query(self, query: str, items: List[Tuple]):
        """ A generic class for adding several items into the database 
        
        Args:
            query (str): The SQL query
            items (List[Tuple]): A list of tuples representing the items that should be inserted into the database 
        """
        connection = self._connect()
        try:
            cursor = connection.cursor()
            cursor.executemany(query, items)
            connection.commit()
        except sqlite3.IntegrityError as e:
            connection.rollback()
            raise RuntimeError(f"A data integrity error occurred: {e}")
        except sqlite3.Error as e:
            connection.rollback()
            raise RuntimeError(f"Failed to insert items: {e}")
        finally:
            connection.close()


    def add_projects(self, projects: List[Tuple]):
        """ Adds a list of projects to the database """
        query = "INSERT INTO projects (project_id) VALUES (?)"
        self._insert_many_db_query(query=query, items=projects)
    
    def add_subjects(self, subjects: List[Tuple]):
        """ Add a list of subjects to the database """
        query = "INSERT INTO subjects (subject_id, condition, age, sex, treatment, response, project) VALUES (?, ?, ?, ?, ?, ?, ?)"
        self._insert_many_db_query(query=query, items=subjects)
    
    def add_samples(self, samples: List[Tuple]):
        """ Adds a list of samples to the database """
        query = "INSERT INTO samples (sample_id, sample_type, time_from_treatment_start, b_cell, cd8_t_cell, cd4_t_cell, nk_cell, monocyte, subject) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
        self._insert_many_db_query(query=query, items=samples)





