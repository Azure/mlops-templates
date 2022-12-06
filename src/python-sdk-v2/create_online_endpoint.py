# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import argparse

from azure.ai.ml.entities import ManagedOnlineEndpoint

from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient

import json

def parse_args():
    parser = argparse.ArgumentParser(description="Register dataset")
    parser.add_argument("-n", type=str, help="Name of online endpoint")
    parser.add_argument("-d", type=str, help="Description of the online endpoint")
    parser.add_argument("-a", type=str, help="authentication mode", default="aml_token")
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
        name=args.n, 
        description=args.d,
        auth_mode=args.a,
    )
    
    endpoint_job = ml_client.online_endpoints.begin_create_or_update(
        online_endpoint,   
    )
    
    ml_client.jobs.stream(endpoint_job.name)

if __name__ == "__main__":
    main()
