# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import asyncio
import asyncpg
import json
import sys
from fastmcp import FastMCP
from typing import Annotated, List, Dict, Any, Optional
from pydantic import Field
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("PostgreSQLServer")

mcp = FastMCP("PostgreSQL Server")

class PostgresOperator:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.conn = None
        logger.info("PostgreSQL Operator initialized")
    
    async def connect(self):
        """Connect to the PostgreSQL database"""
        if not self.conn:
            logger.info("Connecting to PostgreSQL database")
            self.conn = await asyncpg.connect(self.connection_string)
        return self.conn
    
    async def close(self):
        """Close the database connection"""
        if self.conn:
            logger.info("Closing PostgreSQL connection")
            await self.conn.close()
            self.conn = None

# The PostgreSQL operator will be initialized when the server starts
postgres_operator = None

# Custom JSON encoder for PostgreSQL types
def _encoder(value):
    if isinstance(value, asyncpg.pgproto.pgproto.UUID):
        return str(value)
    if isinstance(value, asyncpg.pgproto.pgproto.Numeric):
        return float(value)
    if isinstance(value, asyncpg.pgproto.pgproto.Point):
        return {"x": float(value.x), "y": float(value.y)}
    raise TypeError(f"Cannot encode {type(value)}")

@mcp.tool()
async def list_tables() -> Dict[str, List[str]]:
    """List all tables in the connected database"""
    if not postgres_operator:
        return {"error": "Database connection not initialized"}
    
    try:
        conn = await postgres_operator.connect()
        query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        """
        rows = await conn.fetch(query)
        tables = [row['table_name'] for row in rows]
        
        logger.info(f"Listed {len(tables)} tables")
        return {"tables": tables}
    except Exception as e:
        logger.error(f"Error listing tables: {str(e)}")
        return {"error": str(e)}

@mcp.tool()
async def get_table_schema(
    table_name: Annotated[str, Field(description="Name of the table")]
) -> Dict[str, Any]:
    """Get the schema information for a specific table"""
    if not postgres_operator:
        return {"error": "Database connection not initialized"}
    
    try:
        conn = await postgres_operator.connect()
        query = """
        SELECT 
            column_name, 
            data_type,
            is_nullable,
            column_default
        FROM 
            information_schema.columns
        WHERE 
            table_schema = 'public' AND 
            table_name = $1
        ORDER BY 
            ordinal_position
        """
        rows = await conn.fetch(query, table_name)
        
        if not rows:
            return {"error": f"Table '{table_name}' not found"}
        
        columns = []
        for row in rows:
            columns.append({
                "name": row['column_name'],
                "type": row['data_type'],
                "nullable": row['is_nullable'] == 'YES',
                "default": row['column_default']
            })
        
        # Get primary key information
        pk_query = """
        SELECT 
            kcu.column_name
        FROM 
            information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
        WHERE 
            tc.constraint_type = 'PRIMARY KEY' AND
            tc.table_schema = 'public' AND
            tc.table_name = $1
        ORDER BY 
            kcu.ordinal_position
        """
        pk_rows = await conn.fetch(pk_query, table_name)
        primary_keys = [row['column_name'] for row in pk_rows]
        
        logger.info(f"Retrieved schema for table {table_name}")
        return {
            "table": table_name,
            "columns": columns,
            "primary_keys": primary_keys
        }
    except Exception as e:
        logger.error(f"Error getting schema for table {table_name}: {str(e)}")
        return {"error": str(e)}

@mcp.tool()
async def execute_query(
    query: Annotated[str, Field(description="SQL query to execute (read-only)")]
) -> Dict[str, Any]:
    """Execute a read-only SQL query"""
    if not postgres_operator:
        return {"error": "Database connection not initialized"}
    
    # For security, ensure this is a read-only query
    query_lower = query.lower().strip()
    if any(keyword in query_lower for keyword in ['insert', 'update', 'delete', 'drop', 'alter', 'create', 'truncate']):
        logger.warning(f"Rejected non-read-only query: {query}")
        return {"error": "Only read-only queries are allowed"}
    
    try:
        conn = await postgres_operator.connect()
        rows = await conn.fetch(query)
        
        # Convert rows to dictionaries and handle PostgreSQL-specific types
        result = []
        for row in rows:
            row_dict = dict(row)
            # Use json to handle PostgreSQL types
            row_json = json.loads(json.dumps(row_dict, default=_encoder))
            result.append(row_json)
        
        logger.info(f"Executed query successfully, returned {len(result)} rows")
        return {"rows": result}
    except Exception as e:
        logger.error(f"Error executing query: {str(e)}")
        return {"error": str(e)}

@mcp.tool()
async def count_rows(
    table_name: Annotated[str, Field(description="Name of the table")],
    condition: Annotated[str, Field(description="Optional WHERE condition")] = ""
) -> Dict[str, int]:
    """Count the number of rows in a table with an optional condition"""
    if not postgres_operator:
        return {"error": "Database connection not initialized"}
    
    try:
        conn = await postgres_operator.connect()
        
        query = f"SELECT COUNT(*) FROM {table_name}"
        if condition:
            query += f" WHERE {condition}"
        
        # For security, check if this is a read-only query
        query_lower = query.lower().strip()
        if any(keyword in query_lower for keyword in ['insert', 'update', 'delete', 'drop', 'alter', 'create', 'truncate']):
            logger.warning(f"Rejected non-read-only count query: {query}")
            return {"error": "Only read-only queries are allowed"}
        
        count = await conn.fetchval(query)
        
        logger.info(f"Counted {count} rows in table {table_name}")
        return {"count": count}
    except Exception as e:
        logger.error(f"Error counting rows in table {table_name}: {str(e)}")
        return {"error": str(e)}

# Server initialization with connection string
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python postgresql_server.py <connection_string>")
        sys.exit(1)
    
    connection_string = sys.argv[1]
    postgres_operator = PostgresOperator(connection_string)
    
    # Use asyncio to run the server
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(mcp.run_async())
    finally:
        if postgres_operator:
            loop.run_until_complete(postgres_operator.close())
