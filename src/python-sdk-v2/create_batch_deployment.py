# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import argparse

from azure.ai.ml.entities import BatchEndpoint, BatchDeployment
from azure.ai.ml.constants import BatchDeploymentOutputAction

from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient

import json

def parse_args():
    parser = argparse.ArgumentParser(description="Create batch deployment")
    parser.add_argument("--deployment_name", type=str, help="Name of batch deployment")
    parser.add_argument("--description", type=str, help="Description of batch deployment")
    parser.add_argument("--endpoint_name", type=str, help="Name of the online endpoint")
    parser.add_argument("--model_path", type=str, help="Path to model or AML model")
    parser.add_argument("--compute", type=str, help="Name of the compute cluster")
    parser.add_argument("--instance_count", type=int, help="Number of instances to provision for job", default=2)
    parser.add_argument("--max_concurrency_per_instance", type=int, help="Maximum number of cuncurrent jobs per instance", default=4)
    parser.add_argument("--mini_batch_size", type=int, help="The number of examples to score per job", default=32)
    parser.add_argument("--output_file_name", type=str, help="Output file name", default="predictions.csv")

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

    batch_deployment = BatchDeployment(
        name=args.deployment_name,
        description=args.description,
        endpoint_name=args.endpoint_name,
        model=args.model_path,
        compute=args.compute,
        instance_count=args.instance_count,
        max_concurrency_per_instance=args.max_concurrency_per_instance,
        mini_batch_size=args.mini_batch_size,
        output_action=BatchDeploymentOutputAction.APPEND_ROW,
        output_file_name=args.output_file_name
    )

    deployment_job = ml_client.batch_deployments.begin_create_or_update(
        deployment=batch_deployment
    )
    deployment_job.wait()

    batch_endpoint = ml_client.batch_endpoints.get(args.endpoint_name)
    batch_endpoint.defaults.deployment_name = batch_deployment.name

    endpoint_update_job = ml_client.batch_endpoints.begin_create_or_update(
        batch_endpoint
    )
    endpoint_update_job.wait()


if __name__ == "__main__":
    main()
