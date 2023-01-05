# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import argparse

from azure.ai.ml.entities import ManagedOnlineEndpoint

from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient

import json

def parse_args():
    parser = argparse.ArgumentParser(description="Create online endpoint")
    parser.add_argument("--endpoint_name", type=str, help="Name of online endpoint")
    parser.add_argument("--description", type=str, help="Description of the online endpoint")
    parser.add_argument("--auth_mode", type=str, help="endpoint authentication mode", default="aml_token")
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

    # create an online endpoint
    online_endpoint = ManagedOnlineEndpoint(
        name=args.endpoint_name, 
        description=args.description,
        auth_mode=args.auth_mode,
    )
    
    endpoint_job = ml_client.online_endpoints.begin_create_or_update(
        online_endpoint,   
    )
    endpoint_job.wait()

if __name__ == "__main__":
    main()
