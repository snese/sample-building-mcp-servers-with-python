# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import asyncio
import sys
from fastmcp import Client
import json

async def main():
    if len(sys.argv) < 2:
        print("Usage: python postgresql_example.py <connection_string>")
        return
    
    connection_string = sys.argv[1]
    
    # Create a client that points to the PostgreSQL server with the connection string
    client = Client(["../src/postgresql_server.py", connection_string])
    
    async with client:
        # Get server info
        info = await client.get_info()
        print(f"Connected to: {info.name}")
        
        # List tables
        print("\nListing tables:")
        result = await client.call_tool("list_tables")
        print(json.dumps(result, indent=2))
        
        # If there are tables, get schema for the first one
        if result.get("tables") and len(result["tables"]) > 0:
            table_name = result["tables"][0]
            
            # Get table schema
            print(f"\nGetting schema for table: {table_name}")
            schema = await client.call_tool("get_table_schema", {"table_name": table_name})
            print(json.dumps(schema, indent=2))
            
            # Count rows in the table
            print(f"\nCounting rows in table: {table_name}")
            count = await client.call_tool("count_rows", {"table_name": table_name})
            print(json.dumps(count, indent=2))
            
            # Execute a simple query
            print(f"\nExecuting query on table: {table_name}")
            query = f"SELECT * FROM {table_name} LIMIT 5"
            query_result = await client.call_tool("execute_query", {"query": query})
            print(json.dumps(query_result, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
