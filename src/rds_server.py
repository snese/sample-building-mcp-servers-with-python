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
logger = logging.getLogger("RDSServer")

mcp = FastMCP("RDS Server")

class RDSOperator:
    def __init__(self):
        # Initialize with default AWS configuration
        self.session = boto3.Session()
        logger.info("RDS Operator initialized")
    
    def get_client(self, region: str = ""):
        """Get an RDS client for a specific region or default"""
        if region:
            logger.info(f"Creating RDS client for region: {region}")
            return self.session.client('rds', region_name=region)
        logger.info("Creating RDS client with default region")
        return self.session.client('rds')

rds_operator = RDSOperator()

@mcp.tool()
def list_db_instances(
    region: Annotated[str, Field(description="AWS region (optional)")] = ""
) -> Dict[str, List[Dict[str, Any]]]:
    """List RDS instances in the specified region"""
    client = rds_operator.get_client(region)
    response = client.describe_db_instances()
    
    instances = []
    for instance in response['DBInstances']:
        instances.append({
            "identifier": instance['DBInstanceIdentifier'],
            "engine": instance['Engine'],
            "status": instance['DBInstanceStatus'],
            "endpoint": instance.get('Endpoint', {}).get('Address', 'N/A'),
            "port": instance.get('Endpoint', {}).get('Port', 'N/A'),
        })
    
    logger.info(f"Listed {len(instances)} RDS instances")
    return {"instances": instances}

@mcp.tool()
def describe_db_instance(
    instance_id: Annotated[str, Field(description="RDS instance identifier")],
    region: Annotated[str, Field(description="AWS region (optional)")] = ""
) -> Dict[str, Any]:
    """Get detailed information about an RDS instance"""
    client = rds_operator.get_client(region)
    
    try:
        response = client.describe_db_instances(DBInstanceIdentifier=instance_id)
        
        if not response['DBInstances']:
            return {"error": f"No instance found with ID {instance_id}"}
        
        instance = response['DBInstances'][0]
        
        # Extract the most relevant information
        result = {
            "identifier": instance['DBInstanceIdentifier'],
            "engine": instance['Engine'],
            "engine_version": instance['EngineVersion'],
            "status": instance['DBInstanceStatus'],
            "instance_class": instance['DBInstanceClass'],
            "allocated_storage": instance['AllocatedStorage'],
            "endpoint": instance.get('Endpoint', {}).get('Address', 'N/A'),
            "port": instance.get('Endpoint', {}).get('Port', 'N/A'),
            "multi_az": instance['MultiAZ'],
            "publicly_accessible": instance['PubliclyAccessible'],
            "storage_type": instance['StorageType'],
            "vpc_id": instance.get('DBSubnetGroup', {}).get('VpcId', 'N/A'),
        }
        
        logger.info(f"Retrieved details for RDS instance {instance_id}")
        return {"instance": result}
    
    except client.exceptions.DBInstanceNotFoundFault:
        logger.error(f"RDS instance {instance_id} not found")
        return {"error": f"Instance {instance_id} not found"}
    except Exception as e:
        logger.error(f"Error describing RDS instance {instance_id}: {str(e)}")
        return {"error": str(e)}

@mcp.tool()
def list_db_engine_versions(
    engine: Annotated[str, Field(description="Database engine (e.g., mysql, postgres)")],
    region: Annotated[str, Field(description="AWS region (optional)")] = ""
) -> Dict[str, List[Dict[str, Any]]]:
    """List available engine versions for a specific database engine"""
    client = rds_operator.get_client(region)
    
    response = client.describe_db_engine_versions(Engine=engine)
    
    versions = []
    for version in response['DBEngineVersions']:
        versions.append({
            "engine": version['Engine'],
            "version": version['EngineVersion'],
            "description": version.get('DBEngineVersionDescription', 'N/A'),
            "default_parameter_family": version.get('DBParameterGroupFamily', 'N/A'),
        })
    
    logger.info(f"Listed {len(versions)} engine versions for {engine}")
    return {"versions": versions}

if __name__ == "__main__":
    mcp.run()
