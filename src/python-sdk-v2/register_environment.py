# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import argparse

from azure.ai.ml.entities import Environment

from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient

import json

def parse_args():
    parser = argparse.ArgumentParser(description="Register dataset")
    parser.add_argument("-n", type=str, help="Name of the environment you want to register")
    parser.add_argument("-d", type=str, help="Description of the environment")
    parser.add_argument("-l", type=str, help="local path of environment file")
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


    my_environment = Environment(
        image="mcr.microsoft.com/azureml/openmpi3.1.2-ubuntu18.04",
        conda_file=args.l,
        name=args.n,
        description=args.d,
    )

    ml_client.environments.create_or_update(my_environment)    

if __name__ == "__main__":
    main()
