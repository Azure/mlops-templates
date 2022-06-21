# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import argparse
import azureml.core
from azureml.core import Workspace
from azureml.pipeline.core import PublishedPipeline, PipelineEndpoint

print("Azure ML SDK version:", azureml.core.VERSION)

parser = argparse.ArgumentParser("Add pipeline to pipeline endpoint")
parser.add_argument("-p", type=str, help="Pipeline ID of pipeline to add")
args = parser.parse_args()

ws = Workspace.from_config()

pipeline_id = args.p
published_pipeline = PublishedPipeline.get(workspace=ws, id=pipeline_id)
endpoint_name = published_pipeline.name + '-endpoint'

try:
    pl_endpoint = PipelineEndpoint.get(workspace=ws, name=endpoint_name)
    pl_endpoint.add_default(published_pipeline)
    print(f'Added pipeline {pipeline_id} to Pipeline Endpoint with name {endpoint_name}')
except Exception:
    print(f'Will create new Pipeline Endpoint with name {endpoint_name} with pipeline {pipeline_id}')
    pl_endpoint = PipelineEndpoint.publish(workspace=ws,
                                           name=endpoint_name,
                                           pipeline=published_pipeline,
                                           description='Published by MLOps V2')
