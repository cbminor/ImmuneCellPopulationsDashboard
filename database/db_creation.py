import os
import sqlite3

class InitialDatabaseCreation:
    """ 
    A class with methods related to creating the initial database and inserting the first information
    """

    def initialize_database(self, schema_path: str, db_path: str) -> None:
        """ Initializes a sqlite database based on the given schema 
        
        Args:
            schema_path (str): The path to the sql file containing the db schema
            db_path (str): The path the database

        Raises:
            FileNotFoundError: If the schema file does not exist.
            FileExistsError: If the DB already exists
            RuntimeError: If a SQL or I/O error occurs during intialization.
        """

        if not os.path.exists(schema_path):
            raise FileNotFoundError(f"Schema file at {schema_path} does not exist.")
        
        try:
            with open(schema_path, "r") as f:
                schema = f.read()
            
            conn = sqlite3.connect(db_path)
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
