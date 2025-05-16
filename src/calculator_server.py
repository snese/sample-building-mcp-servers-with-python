# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
from fastmcp import FastMCP
from typing import Annotated
from pydantic import Field

mcp = FastMCP("Calculator Server")

@mcp.tool()
def sum(
    a: Annotated[int, Field(description="The first number")],
    b: Annotated[int, Field(description="The second number")]
) -> int:
    """Calculate the sum of two numbers"""
    return a + b

@mcp.tool()
def sub(
    a: Annotated[int, Field(description="The first number")],
    b: Annotated[int, Field(description="The second number")]
) -> int:
    """Calculate the difference between two numbers"""
    return a - b

@mcp.tool()
def multiply(
    a: Annotated[int, Field(description="The first number")],
    b: Annotated[int, Field(description="The second number")]
) -> int:
    """Calculate the product of two numbers"""
    return a * b

@mcp.tool()
def divide(
    a: Annotated[float, Field(description="The dividend")],
    b: Annotated[float, Field(description="The divisor")]
) -> float:
    """Calculate the quotient of two numbers"""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

if __name__ == "__main__":
    mcp.run()
