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
    
    ml_client = MLClient.from_config()
    
    my_data = Data(
        path=args.l,
        type=args.t,
        description=args.d,
        name=args.n
    )
    
    ml_client.data.create_or_update(my_data)    

if __name__ == "__main__":
    main()
