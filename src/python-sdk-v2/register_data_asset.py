# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import argparse

from azure.ai.ml.entities import Data
from azure.ai.ml.constants import AssetTypes

from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient

import json

def parse_args():
    parser = argparse.ArgumentParser(description="Register dataset")
    parser.add_argument("--data_name", type=str, help="Name of the data asset to register")
    parser.add_argument("--description", type=str, help="Description of the data asset to register")
    parser.add_argument("--data_type", type=str, help="type of data asset", default='uri_file')    
    parser.add_argument("--data_path", type=str, help="path of the data")
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

    
    data = Data(
        path=args.data_path,
        type=args.data_type,
        description=args.description,
        name=args.data_name
    )
    
    ml_client.data.create_or_update(data)    

if __name__ == "__main__":
    main()
