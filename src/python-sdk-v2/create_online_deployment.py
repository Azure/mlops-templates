# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import argparse

from azure.ai.ml.entities import ManagedOnlineEndpoint
from azure.ai.ml.entities import ManagedOnlineDeployment

from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient

import json

def parse_args():
    parser = argparse.ArgumentParser(description="Create online deployment")
    parser.add_argument("--deployment_name", type=str, help="Name of online deployment")
    parser.add_argument("--endpoint_name", type=str, help="Name of the online endpoint")
    parser.add_argument("--model_path", type=str, help="Path to model or AML model")
    parser.add_argument("--instance_type", type=str, help="Instance type", default="Standard_DS2_v2")
    parser.add_argument("--instance_count", type=int, help="Instance count", default=1)
    parser.add_argument("--traffic_allocation", type=str, help="Deployment traffic allocation percentage")

    return parser.parse_args()

def main():
    args = parse_args()
    print(args)
    
    credential = DefaultAzureCredential()
    try:
        ml_client = MLClient.from_config(credential, path='config.json')

    except Exception as ex:
        print("HERE IN THE EXCEPTION BLOCK")
        print(ex)

    # Create online deployment
    online_deployment = ManagedOnlineDeployment(
        name=args.deployment_name,
        endpoint_name=args.endpoint_name,
        model=args.model_path,
        instance_type=args.instance_type,
        instance_count=args.instance_count,
    )

    deployment_job = ml_client.online_deployments.begin_create_or_update(
        deployment=online_deployment
    )
    deployment_job.wait()

    # allocate traffic
    online_endpoint = ManagedOnlineEndpoint(
        name=args.endpoint_name
    )
    online_endpoint.traffic = {args.deployment_name: args.traffic_allocation}
    endpoint_update_job = ml_client.begin_create_or_update(online_endpoint)
    endpoint_update_job.wait()

if __name__ == "__main__":
    main()
