# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import asyncio
from fastmcp import Client
import json

async def main():
    # Create a client that points to the S3 server
    client = Client("../src/s3_server.py")
    
    async with client:
        # Get server info
        info = await client.get_info()
        print(f"Connected to: {info.name}")
        
        # List buckets
        print("\nListing S3 buckets:")
        result = await client.call_tool("list_buckets")
        print(json.dumps(result, indent=2))
        
        # If there are buckets, get details for the first one
        if result.get("buckets") and len(result["buckets"]) > 0:
            bucket_name = result["buckets"][0]
            
            # Get bucket location
            print(f"\nGetting location for bucket: {bucket_name}")
            location = await client.call_tool("get_bucket_location", {"bucket": bucket_name})
            print(json.dumps(location, indent=2))
            
            # List objects in the bucket
            print(f"\nListing objects in bucket: {bucket_name}")
            objects = await client.call_tool("list_objects", {"bucket": bucket_name})
            print(json.dumps(objects, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
