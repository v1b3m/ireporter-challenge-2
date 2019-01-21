import psycopg2
import psycopg2.extras
from pprint import pprint
import os

class DatabaseConnection:
    def __init__(self):
        if os.getenv('DB_NAME') == 'ireporter_db_test':
            self.db_name = 'ireporter_db_test'
        else:
            self.db_name = 'ireporter_db'

        try:
            self.connection = psycopg2.connect(
                dbname='ireporter_db_test', user='postgres', host='localhost', password='2SweijecIf', port=5432
            )
            self.connection.autocommit = True
            self.cursor = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

            print('Connected to database successfully.')
            print(self.db_name)

        except:
            pprint('Failed to connect to the database.')

    def create_user_table(self):
        try:
            query = """CREATE TABLE IF NOT EXISTS users (userId SERIAL PRIMARY KEY,
                        firstname varchar(32) NOT NULL,
                        lastname varchar(32) NOT NULL,
                        othernames varchar(64) NULL,
                        username varchar(32) NOT NULL,
                        email varchar(128) NOT NULL UNIQUE,
                        password varchar(128) NOT NULL,
                        phone_number varchar(15) NOT NULL,
                        registered TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        is_admin BIT NOT NULL DEFAULT '0');
                    """
            self.cursor.execute(query)
            print("Succesfully created users table.")
        except Exception as e:
            pprint(e)

    def create_incidents_table(self):
        try:
            query = """
                    CREATE TABLE IF NOT EXISTS incidents (
                        incident_id SERIAL PRIMARY KEY,
                        created_on TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        created_by int,
                        type varchar(16) NOT NULL,
                        location varchar(32) NOT NULL,
                        status varchar(16) NOT NULL DEFAULT 'Pending',
                        images varchar(256) NOT NULL,
                        videos varchar(256) NOT NULL,
                        comment varchar(256) NOT NULL,
                        FOREIGN KEY (created_by) REFERENCES users(userId)
                    )
                    """
            self.cursor.execute(query)
            print("Successfully created incidents table.")
        except Exception as e:
            pprint(e)

    def create_user(self, **kwargs):
        try:
            query = """
                    INSERT INTO users (firstname, lastname, othernames, username,
                    email, password, phone_number)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
            self.cursor.execute(query, (kwargs['firstname'], kwargs['lastname'],
                            kwargs['othernames'], kwargs['username'], kwargs['email'],
                            kwargs['password'], kwargs['phone_number']))
        except Exception as e:
            pprint(e)

    def create_incident(self, **kwargs):
        try:
            query = """
                    INSERT INTO incidents (created_by, type, location,
                    images, videos, comment) VALUES (%s, %s, %s, %s, %s, %s)
                    """
            self.cursor.execute(query, (kwargs['created_by'], kwargs['type'],
                            kwargs['location'], kwargs['images'],
                            kwargs['videos'], kwargs['comment']))
        except Exception as e:
            pprint(e)

    def delete_incident(self, id):
        try:
            query = "DELETE FROM incidents WHERE incident_id = %d" % id
            self.cursor.execute(query)
        except Exception as e:
            pprint(e)

    def get_incident(self, id):
        try:
            query = "SELECT * FROM incidents WHERE incident_id = %d" % id
            self.cursor.execute(query)
            incident = self.cursor.fetchone()
            return incident.type
        except Exception as e:
            pprint(e)

    def get_incidents(self):
        try:
            query = "SELECT * FROM incidents"
            self.cursor.execute(query)
            incidents = self.cursor.fetchall()
            return incidents
        except Exception as e:
            pprint(e)
    
    def edit_incident_location(self, id, location):
        try:
            query = """
                    UPDATE incidents
                    SET location = %s
                    WHERE incident_id = %s
                    """
            self.cursor.execute(query, (location, id))
        except Exception as e:
            pprint(e)

    def edit_incident_comment(self, id, comment):
        try:
            query = """
                    UPDATE incidents
                    SET comment = %s
                    WHERE incident_id = %s
                    """
            self.cursor.execute(query, (comment, id))
        except Exception as e:
            pprint(e)


if __name__ == '__main__':
    db_name = DatabaseConnection()
    
