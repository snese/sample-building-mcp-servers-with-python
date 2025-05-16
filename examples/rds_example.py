# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import asyncio
from fastmcp import Client
import json

async def main():
    # Create a client that points to the RDS server
    client = Client("../src/rds_server.py")
    
    async with client:
        # Get server info
        info = await client.get_info()
        print(f"Connected to: {info.name}")
        
        # List RDS instances
        print("\nListing RDS instances:")
        result = await client.call_tool("list_db_instances")
        print(json.dumps(result, indent=2))
        
        # If there are instances, get details for the first one
        if result.get("instances") and len(result["instances"]) > 0:
            instance_id = result["instances"][0]["identifier"]
            
            # Get detailed information about the instance
            print(f"\nGetting details for RDS instance: {instance_id}")
            details = await client.call_tool("describe_db_instance", {"instance_id": instance_id})
            print(json.dumps(details, indent=2))
        
        # List engine versions for MySQL
        print("\nListing MySQL engine versions:")
        versions = await client.call_tool("list_db_engine_versions", {"engine": "mysql"})
        print(json.dumps(versions, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
