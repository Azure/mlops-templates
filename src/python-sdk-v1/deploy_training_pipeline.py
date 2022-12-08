# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import re
import argparse
import yaml
import shlex

import azureml.core
from azureml.core import Workspace, Datastore, Dataset, RunConfiguration, Environment

from azureml.pipeline.core import Pipeline, PipelineData
from azureml.pipeline.steps import PythonScriptStep
from azureml.data.dataset_consumption_config import DatasetConsumptionConfig
from azureml.data.output_dataset_config import OutputFileDatasetConfig 

print("Azure ML SDK version:", azureml.core.VERSION)

parser = argparse.ArgumentParser("Deploy Training Pipeline")
parser.add_argument("-f", type=str, help="Controller Config YAML file")
parser.add_argument("-m", type=str, help="Enable Monitoring", default="false")
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

## Read datasets

STEPS_KEYS = ['prep', 'train', 'eval']
steps_inputs = {s: [] for s in STEPS_KEYS}
steps_arguments = {s: [] for s in STEPS_KEYS}
for dataset_def in config['training_datasets'].split(' '):
    print(f"Processing training pipeline argument: {dataset_def}")
    result = re.search(r"(\S+):(\S+):(\S+):(\S+)", dataset_def)
    if not result:
        raise ValueError("Wrong dataset definition. Expected format: <name>:<version>:<mode>:<steps (names separated by +)>")

    dataset_name, dataset_version, dataset_mode = result.group(1, 2, 3)
    dataset_steps =  result.group(4).split('+')
    if any(s not in STEPS_KEYS for s in dataset_steps):
        raise ValueError(f'Wrong step name. Options are: {", ".join(STEPS_KEYS)}')

    dataset_consumption = DatasetConsumptionConfig(
        name=dataset_name.replace('-', '_'),
        dataset=Dataset.get_by_name(ws, dataset_name, dataset_version),
        mode=dataset_mode
    )
    for s in dataset_steps:
        steps_inputs[s].append(dataset_consumption)
        steps_arguments[s] += [f'--{dataset_name}', dataset_consumption]

    print((
        f'Will use dataset "{dataset_name}" in version "{dataset_version}"'
        f' as input ({dataset_mode} mode) in steps: {", ".join(dataset_steps)}'
    ))


## Read arguments

arguments = []
for arg in shlex.split(config['training_arguments']):
    print(f"Processing training pipeline argument: {arg}")
    arguments.append(arg)
print(f"Expanded arguments: {arguments}")


## Build pipeline

# Set up data connections between steps - {run-id} is automatically replaced with the corresponding ID during execution
prepared_data_path = OutputFileDatasetConfig(name="prepared_data", destination=(datastore, "pipeline_artifacts/prepared_data/{run-id}/")).as_upload()
trained_model_path = OutputFileDatasetConfig(name="trained_model", destination=(datastore, "pipeline_artifacts/trained_model/{run-id}/")).as_upload()
explainer_path = OutputFileDatasetConfig(name="explainer", destination=(datastore, "pipeline_artifacts/trained_model/{run-id}/")).as_upload()
evaluation_results_path = OutputFileDatasetConfig(name="evaluation_results", destination=(datastore, "pipeline_artifacts/evaluation_results/{run-id}/")).as_upload()
deploy_flag = PipelineData("deploy_flag")


prepare_step = PythonScriptStep(name="prepare-step",
                        runconfig=runconfig,
                        compute_target=config['training_target'],
                        source_directory="data-science/src/",
                        script_name="prep.py",
                        arguments=[
                            '--prepared_data_path', prepared_data_path,
                            '--enable_monitoring', args.m,
                            '--table_name', config["training_table_name"]
                            ] + arguments + steps_arguments['prep'],
                        inputs=steps_inputs['prep'],
                        allow_reuse=False)

train_step = PythonScriptStep(name="train-step",
                        runconfig=runconfig,
                        compute_target=config['training_target'],
                        source_directory="data-science/src/",
                        script_name="train.py",
                        arguments=[
                            '--prepared_data_path', prepared_data_path.as_input("prepared_data"),
                            '--model_path', trained_model_path
                        ] + arguments + steps_arguments['train'],
                        inputs=steps_inputs['train'],
                        allow_reuse=False)

evaluate_step = PythonScriptStep(name="evaluate-step",
                        runconfig=runconfig,
                        compute_target=config['training_target'],
                        source_directory="data-science/src/",
                        script_name="evaluate.py",
                        arguments=[
                            '--prepared_data_path', prepared_data_path.as_input("prepared_data"),
                            '--model_name', config['model_name'], 
                            '--model_path', trained_model_path.as_input("trained_model"),
                            '--explainer_path', explainer_path,
                            '--evaluation_path', evaluation_results_path,
                            '--deploy_flag', deploy_flag
                        ] + arguments + steps_arguments['eval'],
                        inputs=steps_inputs['eval'],
                        outputs=[deploy_flag],
                        allow_reuse=False)

register_step = PythonScriptStep(name="register-step",
                        runconfig=runconfig,
                        compute_target=config['training_target'],
                        source_directory="templates/src/python-sdk-v1/",
                        script_name="register_model.py",
                        arguments=['--model_name', config['model_name'], 
                                   '--model_path', trained_model_path.as_input("trained_model"),
                                   '--deploy_flag', deploy_flag],
                        inputs=[deploy_flag],
                        allow_reuse=False)

#register_step.run_after(evaluate_step)
steps = [prepare_step, train_step, evaluate_step, register_step]

print('Creating, validating, and publishing pipeline')
pipeline = Pipeline(workspace=ws, steps=steps)
pipeline.validate()
published_pipeline = pipeline.publish(config['training_pipeline_name'])

# Output pipeline_id in specified format which will convert it to a variable in Azure DevOps
print(f'Exporting pipeline id {published_pipeline.id} as environment variable pipeline_id')
print(f'##vso[task.setvariable variable=pipeline_id]{published_pipeline.id}')
