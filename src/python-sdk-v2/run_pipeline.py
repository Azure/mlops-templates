# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import argparse

from azure.ai.ml.entities import Data
from azure.ai.ml.constants import AssetTypes

from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient

from azure.ai.ml.entities import AmlCompute
from azure.ai.ml.entities import Data
from azure.ai.ml.constants import AssetTypes
from azure.ai.ml.entities import Environment
from azure.ai.ml.dsl import pipeline
from azure.ai.ml import Input, Output, load_component
from azure.ai.ml.constants import AssetTypes, InputOutputModes

import json
import yaml

def parse_args():
    parser = argparse.ArgumentParser("Deploy Training Pipeline")
    parser.add_argument("-f", type=str, help="Controller Config YAML file")
    parser.add_argument("-m", type=str, help="Enable Monitoring", default="false")
    args = parser.parse_args()

    with open(args.f, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        config = config['variables']

    return parser.parse_args(), config


def main():
    args, config = parse_args()
    print(args)
    print(config)
    
    credential = DefaultAzureCredential()
    try:
        ml_client = MLClient.from_config(credential, path='config.json')

    except Exception as ex:
        print("HERE IN THE EXCEPTION BLOCK")
        print(ex)

    try:
        cpu_compute_target = config['training_target']
        print(ml_client.compute.get(cpu_compute_target))
    except:
                
        my_cluster = AmlCompute(
            name=config['training_target'],
            type="amlcompute", 
            size=config['training_target_sku'], 
            min_instances=int(config['training_target_min_nodes']), 
            max_instances=int(config['training_target_max_nodes']),
            location="westeurope", 	
        )

        ml_client.compute.begin_create_or_update(my_cluster)


    
if __name__ == "__main__":
    main()
