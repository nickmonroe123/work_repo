import cx_Oracle
from typing import List, Dict
import os

def connect_to_oracle(username: str, password: str, host: str, port: str, service_name: str) -> cx_Oracle.Connection:
    """
    Establishes connection to Oracle database
    
    Args:
        username (str): Database username
        password (str): Database password
        host (str): Database host address
        port (str): Database port number
        service_name (str): Oracle service name
    
    Returns:
        cx_Oracle.Connection: Database connection object
    """
    dsn = cx_Oracle.makedsn(host=host, port=port, service_name=service_name)
    connection = cx_Oracle.connect(user=username, password=password, dsn=dsn)
    return connection

def query_with_params(connection: cx_Oracle.Connection, 
                     sql_query: str,
                     params: Dict = None) -> List[Dict]:
    """
    Executes a parameterized query and returns results
    
    Args:
        connection (cx_Oracle.Connection): Database connection
        sql_query (str): SQL query with bind variables
        params (Dict): Dictionary of parameter names and values
    
    Returns:
        List[Dict]: List of dictionaries containing query results
    """
    try:
        # Create cursor
        cursor = connection.cursor()
        
        # Execute query with parameters
        cursor.execute(sql_query, params or {})
        
        # Get column names
        columns = [col[0] for col in cursor.description]
        
        # Fetch results and convert to list of dictionaries
        results = []
        for row in cursor:
            results.append(dict(zip(columns, row)))
            
        return results
        
    except cx_Oracle.Error as error:
        print(f"Database error: {error}")
        raise
        
    finally:
        if cursor:
            cursor.close()

def main():
    # Database connection parameters
    db_config = {
        "username": "your_username",
        "password": "your_password",
        "host": "your_host",
        "port": "1521",  # Default Oracle port
        "service_name": "your_service_name"
    }
    
    # Example query with parameters
    query = """
    SELECT * 
    FROM employees 
    WHERE department_id = :dept_id 
    AND salary >= :min_salary
    """
    
    # Parameter values
    params = {
        "dept_id": 10,
        "min_salary": 50000
    }
    
    try:
        # Establish connection
        connection = connect_to_oracle(**db_config)
        
        # Execute query
        results = query_with_params(connection, query, params)
        
        # Process results
        for row in results:
            print(row)
            
    except Exception as e:
        print(f"Error: {e}")
        
    finally:
        if connection:
            connection.close()

if __name__ == "__main__":
    main()
