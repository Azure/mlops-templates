# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import argparse

from azure.ai.ml.entities import Environment

from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient

import json

def parse_args():
    parser = argparse.ArgumentParser(description="Register Environment")
    parser.add_argument("--environment_name", type=str, help="Name of the environment you want to register")
    parser.add_argument("--description", type=str, help="Description of the environment")
    parser.add_argument("--conda_file", type=str, help="local path of conda file")
    parser.add_argument("--base_image", type=str, help="base image path", default="mcr.microsoft.com/azureml/openmpi3.1.2-ubuntu18.04")
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


    environment = Environment(
        image=args.base_image,
        conda_file=args.conda_file,
        name=args.environment_name,
        description=args.description,
    )

    ml_client.environments.create_or_update(environment)    

if __name__ == "__main__":
    main()
