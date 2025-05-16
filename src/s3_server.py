# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import boto3
from fastmcp import FastMCP
from typing import Annotated, List, Dict, Any, Optional
from pydantic import Field
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("S3Server")

mcp = FastMCP("S3 Server")

class S3Operator:
    def __init__(self):
        # Initialize with default AWS configuration
        self.session = boto3.Session()
        logger.info("S3 Operator initialized")
    
    def get_client(self, region: str = ""):
        """Get an S3 client for a specific region or default"""
        if region:
            logger.info(f"Creating S3 client for region: {region}")
            return self.session.client('s3', region_name=region)
        logger.info("Creating S3 client with default region")
        return self.session.client('s3')

s3_operator = S3Operator()

@mcp.tool()
def list_buckets(
    region: Annotated[str, Field(description="AWS region (optional)")] = ""
) -> Dict[str, List[str]]:
    """List S3 buckets in the specified region"""
    client = s3_operator.get_client(region)
    response = client.list_buckets()
    buckets = [bucket['Name'] for bucket in response['Buckets']]
    logger.info(f"Listed {len(buckets)} buckets")
    return {"buckets": buckets}

@mcp.tool()
def list_objects(
    bucket: Annotated[str, Field(description="S3 bucket name")],
    prefix: Annotated[str, Field(description="Object prefix (optional)")] = "",
    region: Annotated[str, Field(description="AWS region (optional)")] = ""
) -> Dict[str, List[Dict[str, Any]]]:
    """List objects in an S3 bucket with optional prefix"""
    client = s3_operator.get_client(region)
    
    params = {'Bucket': bucket}
    if prefix:
        params['Prefix'] = prefix
    
    response = client.list_objects_v2(**params)
    
    objects = []
    if 'Contents' in response:
        for obj in response['Contents']:
            objects.append({
                'key': obj['Key'],
                'size': obj['Size'],
                'last_modified': obj['LastModified'].isoformat(),
            })
    
    logger.info(f"Listed {len(objects)} objects in bucket {bucket}")
    return {"objects": objects}

@mcp.tool()
def get_bucket_location(
    bucket: Annotated[str, Field(description="S3 bucket name")]
) -> Dict[str, str]:
    """Get the region where an S3 bucket is located"""
    client = s3_operator.get_client()
    response = client.get_bucket_location(Bucket=bucket)
    
    # S3 returns None for us-east-1, so handle that case
    location = response.get('LocationConstraint') or 'us-east-1'
    
    logger.info(f"Bucket {bucket} is located in {location}")
    return {"region": location}

if __name__ == "__main__":
    mcp.run()
