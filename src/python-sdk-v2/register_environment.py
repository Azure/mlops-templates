# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import argparse

from azure.ai.ml.entities import Environment, BuildContext

from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient

import json

def parse_args():
    parser = argparse.ArgumentParser(description="Register dataset")
    parser.add_argument("-n", type=str, help="Name of the environment you want to register")
    parser.add_argument("-d", type=str, help="Description of the environment")
    parser.add_argument("-p", type=str, help="Local path of environment file(s)")
    parser.add_argument("-b", type=str, help="Build type: either docker or conda")
    return parser.parse_args()

def main():
    args = parse_args()
    print(args)
    
    credential = DefaultAzureCredential()
    try:
        ml_client = MLClient.from_config(credential, path='config.json')

    except Exception as ex:
        print("Could not find config.json or config.json is not in the right format.")
        print(ex)

    build_type = args.b
    if build_type == 'docker':
        print("Using docker build contect")
        custom_env = Environment(
            name=args.n,
            build=BuildContext(path=args.p),
            description=args.d
        )
    elif build_type == 'conda':
        my_environment = Environment(
            image="mcr.microsoft.com/azureml/openmpi3.1.2-ubuntu18.04",
            conda_file=args.p,
            name=args.n,
            description=args.d,
        )
    else: 
        print("Expected 'docker' or 'conda' as build type.")
        print(ex)

    ml_client.environments.create_or_update(my_environment)    

if __name__ == "__main__":
    main()
