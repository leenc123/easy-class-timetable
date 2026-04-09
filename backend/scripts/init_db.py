"""
MySQL database initialization script.
Uses pymysql to create database and import schema.
"""

import pymysql
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings

def init_database():
    """Initialize the database."""

    # Parse DATABASE_URL
    # Format: mysql+pymysql://user:password@host:port/database
    db_url = settings.DATABASE_URL
    print(f"Database URL: {db_url}")

    # Extract connection parameters
    # Simple parsing for mysql+pymysql://user:password@host:port/database
    if db_url.startswith("mysql+pymysql://"):
        url_part = db_url.replace("mysql+pymysql://", "")
        # Split by @ to get user:password and host:port/database
        auth_part, server_part = url_part.split("@")
        user, password = auth_part.split(":")

        # Split server_part by / to get host:port and database
        if "/" in server_part:
            host_port, database = server_part.split("/", 1)
            if ":" in host_port:
                host, port = host_port.split(":")
                port = int(port)
            else:
                host = host_port
                port = 3306
        else:
            host = server_part
            port = 3306
            database = ""
    else:
        raise ValueError(f"Unsupported DATABASE_URL format: {db_url}")

    print(f"Connecting to MySQL at {host}:{port} with user {user}")

    # First, connect without database to create it
    try:
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            charset='utf8mb4'
        )
        print("Connected to MySQL server successfully!")

        with connection.cursor() as cursor:
            # Create database if not exists
            cursor.execute(
                "CREATE DATABASE IF NOT EXISTS `timetable` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
            print("Database 'timetable' created or already exists.")

            # Show databases
            cursor.execute("SHOW DATABASES LIKE 'timetable'")
            result = cursor.fetchone()
            print(f"Database check result: {result}")

        connection.close()

        # Now connect to the specific database
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database='timetable',
            charset='utf8mb4'
        )
        print("Connected to timetable database!")

        # Read and execute SQL schema
        schema_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'migrations', 'init.sql'
        )

        if os.path.exists(schema_path):
            print(f"Reading schema from: {schema_path}")
            with open(schema_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()

            # Execute SQL statements
            # Split by semicolon and execute each statement
            statements = sql_content.split(';')

            with connection.cursor() as cursor:
                for statement in statements:
                    statement = statement.strip()
                    if statement and not statement.startswith('--'):
                        try:
                            cursor.execute(statement)
                        except Exception as e:
                            # Skip comments and empty statements
                            if not statement.startswith('--') and statement:
                                print(f"Error executing statement: {e}")
                                print(f"Statement: {statement[:100]}...")

            connection.commit()
            print("Schema imported successfully!")

            # Verify tables
            with connection.cursor() as cursor:
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                print(f"Tables created: {[t[0] for t in tables]}")
        else:
            print(f"Schema file not found at: {schema_path}")

        connection.close()
        print("\nDatabase initialization complete!")
        print("\nDefault users created:")
        print("  - admin (super_admin, password: admin123)")
        print("  - org_admin (org_admin, password: org123)")

    except pymysql.Error as e:
        print(f"MySQL error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    init_database()