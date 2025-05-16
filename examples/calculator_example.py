# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import asyncio
from fastmcp import Client

async def main():
    # Create a client that points to the calculator server
    client = Client("../src/calculator_server.py")
    
    async with client:
        # Get server info
        info = await client.get_info()
        print(f"Connected to: {info.name}")
        
        # Call the sum tool
        result = await client.call_tool("sum", {"a": 5, "b": 3})
        print(f"5 + 3 = {result}")
        
        # Call the sub tool
        result = await client.call_tool("sub", {"a": 10, "b": 4})
        print(f"10 - 4 = {result}")
        
        # Call the multiply tool
        result = await client.call_tool("multiply", {"a": 6, "b": 7})
        print(f"6 * 7 = {result}")
        
        # Call the divide tool
        result = await client.call_tool("divide", {"a": 20, "b": 4})
        print(f"20 / 4 = {result}")
        
        # Try division by zero (should raise an error)
        try:
            result = await client.call_tool("divide", {"a": 10, "b": 0})
            print(f"10 / 0 = {result}")  # This should not execute
        except Exception as e:
            print(f"Error (expected): {e}")

if __name__ == "__main__":
    asyncio.run(main())
