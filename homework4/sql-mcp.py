import pyodbc
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("SQL-Server-Manager")
CONN_STR = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=localhost;"
    "Database=Database;"
    "Trusted_Connection=yes;"
)

@mcp.tool()
def query_employees(sql: str) -> str:
    """
    Query the Employees table in the for_mcp database.
    Example: 'SELECT * FROM Employees WHERE Salary > 70000'
    """
    try:
        with pyodbc.connect(CONN_STR) as conn:
            cursor = conn.cursor()
            cursor.execute(sql)
            if cursor.description:
                columns = [column[0] for column in cursor.description]
                rows = cursor.fetchall()
                results = []
                for row in rows:
                    results.append(dict(zip(columns, row)))
                
                if not results:
                    return "No results found."
                return str(results)
            else:
                conn.commit()
                return "Command executed successfully."
    except Exception as e:
        return f"Database Error: {str(e)}"

if __name__ == "__main__":
    mcp.run()