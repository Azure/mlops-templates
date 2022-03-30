# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
import argparse
from azureml.core import Run, Experiment, Model
from azureml.pipeline.core import PipelineRun

parser = argparse.ArgumentParser()
parser.add_argument('--model_name', type=str, help='Name under which model will be registered')
parser.add_argument('--model_path', type=str, help='Model directory')
parser.add_argument('--deploy_flag', type=str, help='A deploy flag whether to deploy or no')
args, _ = parser.parse_known_args()

print(f'Arguments: {args}')
model_name = args.model_name
model_path = args.model_path

with open(args.deploy_flag, 'r') as f:
    deploy_flag = int(f.read())
        
# current run is the registration step
current_run = Run.get_context()
ws = current_run.experiment.workspace

# parent run is the overall pipeline
parent_run = current_run.parent
print(f'Parent run id: {parent_run.id}')

# find pipeline step named 'train-step'
pipeline_run = PipelineRun(parent_run.experiment, parent_run.id)
training_run = pipeline_run.find_step_run('train-step')[0]
print(f'Training run: {training_run}')

#model = training_run.register_model(model_name=args.model_name,
#                                    model_path=args.model_path)

if deploy_flag==1:
    print("Registering ", args.model_name)
    registered_model = Model.register(model_path=args.model_path,
                                      model_name=args.model_name,
                                      workspace=ws)
    print("Registered ", registered_model.id)
else:
    print("Model will not be registered!")