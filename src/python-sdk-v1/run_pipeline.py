# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import argparse
import azureml.core
from azureml.core import Workspace, Experiment
from azureml.pipeline.core import PublishedPipeline

print("Azure ML SDK version:", azureml.core.VERSION)

parser = argparse.ArgumentParser("Run Pipeline")
parser.add_argument("-p", type=str, help="Pipeline Id")
args = parser.parse_args()

ws = Workspace.from_config()

pipeline = PublishedPipeline.get(workspace=ws, id=args.p)
experiment_name = pipeline.name + '-ci'
pipeline_run = Experiment(ws, experiment_name).submit(pipeline, regenerate_outputs=True)
print(pipeline_run)
pipeline_run.wait_for_completion()
