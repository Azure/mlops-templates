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
import os


def parse_args():
    parser = argparse.ArgumentParser("Deploy Training Pipeline")
    parser.add_argument("-c", type=str, help="Compute Cluster Name")
    parser.add_argument("-m", type=str, help="Enable Monitoring", default="false")
    parser.add_argument("-d", type=str, help="Data Asset Name")
    args = parser.parse_args()

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

    # try:
    #     cpu_compute_target = args.c
    #     print(ml_client.compute.get(cpu_compute_target))
    # except:
                
    #     my_cluster = AmlCompute(
    #         name=args.c,
    #         type="amlcompute", 
    #         size=config['training_target_sku'], 
    #         min_instances=int(config['training_target_min_nodes']), 
    #         max_instances=int(config['training_target_max_nodes']),
    #         location="westeurope", 	
    #     )

    #     ml_client.compute.begin_create_or_update(my_cluster)


    print(os.getcwd())
    print('current', os.listdir())

    # Create pipeline job
    parent_dir = "mlops/azureml/train"



    # 1. Load components
    prepare_data = load_component(source=os.path.join(parent_dir , "prep.yml"))
    train_model = load_component(source=os.path.join(parent_dir, "train.yml"))
    evaluate_model = load_component(source=os.path.join(parent_dir, "evaluate.yml"))
    register_model = load_component(source=os.path.join(parent_dir, "register.yml"))

    # 2. Construct pipeline
    @pipeline()
    def taxi_training_pipeline(raw_data, enable_monitoring, table_name):
        
        prepare = prepare_data(
            raw_data=raw_data,
            enable_monitoring=enable_monitoring, 
            table_name=table_name
        )

        train = train_model(
            train_data=prepare.outputs.train_data
        )

        evaluate = evaluate_model(
            model_name="taxi-model",
            model_input=train.outputs.model_output,
            test_data=prepare.outputs.test_data
        )


        register = register_model(
            model_name="taxi-model",
            model_path=train.outputs.model_output,
            evaluation_output=evaluate.outputs.evaluation_output
        )

        return {
            "pipeline_job_train_data": prepare.outputs.train_data,
            "pipeline_job_test_data": prepare.outputs.test_data,
            "pipeline_job_trained_model": train.outputs.model_output,
            "pipeline_job_score_report": evaluate.outputs.evaluation_output,
        }


    pipeline_job = taxi_training_pipeline(
        Input(type=AssetTypes.URI_FOLDER, path=args.d + "@latest"), "false", "taximonitoring"
    )

    # set pipeline level compute
    pipeline_job.settings.default_compute = args.c
    # set pipeline level datastore
    pipeline_job.settings.default_datastore = "workspaceblobstore"

    pipeline_job = ml_client.jobs.create_or_update(
        pipeline_job, experiment_name="pipeline_samples"
    )

    print(pipeline_job)


    
if __name__ == "__main__":
    main()
