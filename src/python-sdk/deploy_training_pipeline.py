# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
import re
import argparse
import yaml
import shlex

import azureml.core
from azureml.core import Workspace, Experiment, Datastore, Dataset, RunConfiguration, Environment

from azureml.core.compute import AmlCompute, ComputeTarget
from azureml.pipeline.core import Pipeline, PipelineData, PipelineParameter
from azureml.pipeline.steps import PythonScriptStep
from azureml.data.dataset_consumption_config import DatasetConsumptionConfig
from azureml.data.output_dataset_config import OutputFileDatasetConfig 

print("Azure ML SDK version:", azureml.core.VERSION)

parser = argparse.ArgumentParser("Deploy Training Pipeline")
parser.add_argument("-f", type=str, help="Controller Config YAML file")
args = parser.parse_args()

with open(args.f, "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
    config = config['variables']
print(config)


ws = Workspace.from_config()
env = Environment.get(workspace=ws, name=config['training_env_name'])
datastore = Datastore.get_default(ws)
runconfig = RunConfiguration()
runconfig.environment = env
training_dataset_consumption = None
arguments = []
inputs = []

for arg in shlex.split(config['training_arguments']):
    print(f"Processing training pipeline argument: {arg}")
    result = re.search(r"azureml:(\S+):(\S+)", str(arg))
    if result:
        print("in the if condition")
        dataset_name = result.group(1)
        dataset_version = result.group(2)
        print(f"Will use dataset {dataset_name} in version {dataset_version}")
        
        # FIXME: Won't work with multiple input datasets
        # FIXME: Make download or mount configurable
        # FIXME: Allow version==latest
        training_dataset = Dataset.get_by_name(ws, dataset_name, dataset_version)
        training_dataset_parameter = PipelineParameter(name="training_dataset", default_value=training_dataset)
        training_dataset_consumption = DatasetConsumptionConfig("training_dataset", training_dataset_parameter).as_download()
        arguments.append(training_dataset_consumption)
        inputs.append(training_dataset_consumption)
        print(training_dataset_consumption)
    else:
        print("in the else condition")
        arguments.append(arg)
print(f"Expanded arguments: {arguments}")
print(training_dataset_consumption)

transformed_data_path = OutputFileDatasetConfig(name="transformed_data", destination=(datastore, "pipeline_artifacts/transformed_data")).as_upload()
trained_model_path = OutputFileDatasetConfig(name="trained_model", destination=(datastore, "pipeline_artifacts/trained_model")).as_upload()
explainer_path = OutputFileDatasetConfig(name="explainer", destination=(datastore, "pipeline_artifacts/trained_model")).as_upload()
evaluation_results_path = OutputFileDatasetConfig(name="evaluation_results", destination=(datastore, "pipeline_artifacts/evaluation_results")).as_upload()
deploy_flag = PipelineData("deploy_flag")


arguments = arguments + ['--transformed_data_path', transformed_data_path]

transform_step = PythonScriptStep(name="transform-step",
                        runconfig=runconfig,
                        compute_target=config['training_target'],
                        source_directory="data-science/src/",
                        script_name="transform.py",
                        arguments=arguments,
                        inputs=inputs,
                        allow_reuse=False)

train_step = PythonScriptStep(name="train-step",
                        runconfig=runconfig,
                        compute_target=config['training_target'],
                        source_directory="data-science/src/",
                        script_name="train.py",
                        arguments=['--transformed_data_path', transformed_data_path.as_input("transformed_data"),
                                   '--model_path', trained_model_path],
                        allow_reuse=False)

evaluate_step = PythonScriptStep(name="evaluate-step",
                        runconfig=runconfig,
                        compute_target=config['training_target'],
                        source_directory="data-science/src/",
                        script_name="evaluate.py",
                        arguments=['--transformed_data_path', transformed_data_path.as_input("transformed_data"),
                                   '--model_name', config['model_name'], 
                                   '--model_path', trained_model_path.as_input("trained_model"),
                                   '--explainer_path', explainer_path,
                                   '--evaluation_path', evaluation_results_path,
                                   '--deploy_flag', deploy_flag],
                        outputs=[deploy_flag],
                        allow_reuse=False)

register_step = PythonScriptStep(name="register-step",
                        runconfig=runconfig,
                        compute_target=config['training_target'],
                        source_directory="templates/src/python-sdk/",
                        script_name="register_model.py",
                        arguments=['--model_name', config['model_name'], 
                                   '--model_path', trained_model_path.as_input("trained_model"),
                                   '--deploy_flag', deploy_flag],
                        inputs=[deploy_flag],
                        allow_reuse=False)

#register_step.run_after(evaluate_step)
steps = [transform_step, train_step, evaluate_step, register_step]

print('Creating, validating, and publishing pipeline')
pipeline = Pipeline(workspace=ws, steps=steps)
pipeline.validate()
published_pipeline = pipeline.publish(config['training_pipeline_name'])

# Output pipeline_id in specified format which will convert it to a variable in Azure DevOps
print(f'Exporting pipeline id {published_pipeline.id} as environment variable pipeline_id')
print(f'##vso[task.setvariable variable=pipeline_id]{published_pipeline.id}')