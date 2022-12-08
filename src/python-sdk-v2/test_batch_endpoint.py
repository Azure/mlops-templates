# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import argparse

from azure.ai.ml.entities import BatchEndpoint
from azure.ai.ml import Input
from azure.ai.ml.constants import AssetTypes, InputOutputModes

from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient

import json

def parse_args():
    parser = argparse.ArgumentParser(description="Test batch endpoint")
    parser.add_argument("--endpoint_name", type=str, help="Name of the batch endpoint")
    parser.add_argument("--request_batch_file", type=str, help="Path of the request batch file")
    parser.add_argument("--request_type", type=str, help="either uri_folder or uri_file")
    
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

    # invoke the endpoint for batch scoring job
    ml_client.batch_endpoints.invoke(
        endpoint_name=args.endpoint_name,
        input=Input(path=args.request_batch_file,
                    type=args.request_type, 
                    mode=InputOutputModes.DOWNLOAD)
    )

if __name__ == "__main__":
    main()
