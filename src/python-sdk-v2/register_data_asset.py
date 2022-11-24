# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import argparse

from azure.ai.ml.entities import Data
from azure.ai.ml.constants import AssetTypes

from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient

def parse_args():
    parser = argparse.ArgumentParser(description="Register dataset")
    parser.add_argument("-n", type=str, help="Name of the dataset you want to register")
    parser.add_argument("-d", type=str, help="Description of the dataset you want to register")
    parser.add_argument("-t", type=str, help="type of dataset", default='uri_file')    
    parser.add_argument("-l", type=str, help="local path of the dataset folder", default='data/')
    return parser.parse_args()

def main():
    args = parse_args()
    print(args)
    
    credential = DefaultAzureCredential()
    try:
        ml_client = MLClient.from_config(credential, path='config.json')
        print("Found the config file config.json")
        f = open('config.json')
        print(json.load(f))
        f.close()

    except Exception as ex:
        print(ex)
        # Enter details of your AzureML workspace
        # NOT GOOD PRACTICE TO HARDCODE, JUST TESTING 
        subscription_id = "1717a761-4803-4999-9d6e-3fdc1454c085"
        resource_group = "rg-mlopsv2-0518prod"
        workspace = "mlw-mlopsv2-0518prod"
        ml_client = MLClient(credential, subscription_id, resource_group, workspace)

    
    my_data = Data(
        path=args.l,
        type=args.t,
        description=args.d,
        name=args.n
    )
    
    ml_client.data.create_or_update(my_data)    

if __name__ == "__main__":
    main()
