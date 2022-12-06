# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import argparse

from azure.ai.ml.entities import ManagedOnlineEndpoint
from azure.ai.ml.entities import ManagedOnlineDeployment

from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient

import json

def parse_args():
    parser = argparse.ArgumentParser(description="Register dataset")
    parser.add_argument("-nd", type=str, help="Name of online deployment")
    parser.add_argument("-ne", type=str, help="Name of the online endpoint")
    parser.add_argument("-nm", type=str, help="Name and version of model in AML model registry format model_name:version or model_name@latest")
    parser.add_argument("-t", type=str, help="Deployment traffic percentage")

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
        name=args.nd,
        endpoint_name=args.ne,
        model=args.nm,
        instance_type="Standard_DS2_v2",
        instance_count=1,
    )

    ml_client.online_deployments.begin_create_or_update(
        deployment=online_deployment
    )

    # allocate traffic
    online_endpoint = ManagedOnlineEndpoint(
        name=args.ne
    )
    online_endpoint.traffic = {args.nd: args.t}
    ml_client.begin_create_or_update(online_endpoint)



if __name__ == "__main__":
    main()
