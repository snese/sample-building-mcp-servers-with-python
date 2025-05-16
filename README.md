# MCP Sample

A Python implementation of Model Context Protocol (MCP) servers for extending AI assistant capabilities.

## Overview

This project provides sample MCP servers that can be used with Amazon Q or other MCP-compatible AI assistants. The servers implement various functionalities:

- **Calculator Server**: Performs basic arithmetic operations
- **RDS Server**: Interacts with Amazon RDS instances
- **S3 Server**: Manages Amazon S3 buckets and objects
- **PostgreSQL Server**: Connects to PostgreSQL databases and executes queries

These servers demonstrate how to build MCP servers in Python using the FastMCP framework, which provides a high-level, Pythonic interface for implementing the Model Context Protocol.

## Prerequisites

- Python 3.12+
- FastMCP library
- uv (recommended Python package manager for FastMCP)
- AWS credentials configured for RDS and S3 operations (for the respective servers)
- An MCP-compatible AI assistant (like Amazon Q)

## Installation

Clone the repository and install the dependencies:

```bash
git clone <repository-url>
cd sample-building-mcp-servers-with-python
```

We recommend using [uv](https://github.com/astral-sh/uv) to install dependencies as it's faster and more reliable than pip:

```bash
# Install uv if you don't have it
curl -sSf https://install.python-poetry.org | python3 -

# Install dependencies with uv
uv pip install -r requirements.txt
```

Alternatively, you can use pip:

```bash
pip install -r requirements.txt
```

## Usage

Run each server independently:

```bash
# Run the calculator server
python src/calculator_server.py

# Run the RDS server
python src/rds_server.py

# Run the S3 server
python src/s3_server.py

# Run the PostgreSQL server (requires a connection string)
python src/postgresql_server.py "postgresql://username:password@hostname:port/database"
```

### Integration with Amazon Q CLI

To integrate these MCP servers with Amazon Q CLI or other MCP-compatible clients, add a configuration like this to your `.amazon-q.json` file:

```json
{
  "mcpServers": {
    "calculator": {
      "command": "python /path/to/sample-building-mcp-servers-with-python/src/calculator_server.py",
      "args": []
    },
    "s3": {
      "command": "python /path/to/sample-building-mcp-servers-with-python/src/s3_server.py",
      "args": []
    },
    "rds": {
      "command": "python /path/to/sample-building-mcp-servers-with-python/src/rds_server.py",
      "args": []
    },
    "postgres": {
      "command": "python /path/to/sample-building-mcp-servers-with-python/src/postgresql_server.py",
      "args": ["postgresql://username:password@hostname:port/database"]
    }
  }
}
```

Replace `/path/to/sample-building-mcp-servers-with-python/` with the actual path to your project. Once configured, Amazon Q will be able to use these servers to extend its capabilities.

## Server Descriptions

### Calculator Server

Provides basic arithmetic operations like addition, subtraction, multiplication, and division.

### RDS Server

Lists and manages Amazon RDS instances in specified regions.

### S3 Server

Manages S3 buckets and objects, including listing buckets by region.

### PostgreSQL Server

Connects to PostgreSQL databases and executes read-only queries, lists tables, and provides schema information.

## Understanding the Code

Each server follows a similar pattern:

1. Create a FastMCP instance
2. Define tools using the `@mcp.tool()` decorator
3. Run the server with `mcp.run()`

For example, the Calculator Server looks like this:

```python
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

if __name__ == "__main__":
    mcp.run()
```

## Dependencies

- FastMCP: Python implementation of the Model Context Protocol
- boto3: AWS SDK for Python (for S3 and RDS servers)
- asyncpg: PostgreSQL client library (for PostgreSQL server)
- pydantic: Data validation and settings management

## Learning More

To learn more about the Model Context Protocol and FastMCP:

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [FastMCP Documentation](https://gofastmcp.com/)
- [Amazon Q Documentation](https://docs.aws.amazon.com/amazonq/)
- [uv Documentation](https://github.com/astral-sh/uv) - Recommended Python package manager for FastMCP

## Acknowledgments

This project was inspired by [sample-building-mcp-servers-with-rust](https://github.com/aws-samples/sample-building-mcp-servers-with-rust), which provides a similar implementation of MCP servers using Rust. We thank the authors for their work and inspiration.
