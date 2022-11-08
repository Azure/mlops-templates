# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import argparse
import yaml

import azureml.core
from azureml.core import Workspace, Dataset, RunConfiguration, Environment
from azureml.pipeline.core import Pipeline, PipelineParameter
from azureml.data.dataset_consumption_config import DatasetConsumptionConfig
from azureml.pipeline.steps import ParallelRunStep, ParallelRunConfig
from azureml.data import OutputFileDatasetConfig

print("Azure ML SDK version:", azureml.core.VERSION)

parser = argparse.ArgumentParser("Deploy Batch Scoring Pipeline")
parser.add_argument("-f", type=str, help="Controller Config YAML file")
parser.add_argument("-m", type=str, help="Enable Monitoring", default="false")
args = parser.parse_args()

print("monitoring enabled:", args.m)


with open(args.f, "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
    config = config['variables']
print(config)

ws = Workspace.from_config()
env = Environment.get(workspace=ws, name=config['batch_env_name'])
runconfig = RunConfiguration()
runconfig.environment = env

# Dataset input and output
batch_dataset = Dataset.get_by_name(ws, config['batch_input_dataset_name'])
batch_dataset_parameter = PipelineParameter(name="batch_dataset", default_value=batch_dataset)
batch_dataset_consumption = DatasetConsumptionConfig("batch_dataset", batch_dataset_parameter).as_download()

datastore = ws.get_default_datastore()
output_dataset = OutputFileDatasetConfig(name='batch_results',
                                         destination=(datastore, config['batch_output_path_on_datastore'])).register_on_complete(name=config['batch_output_dataset_name'])

parallel_run_config = ParallelRunConfig(
    source_directory="data-science/src/",
    entry_script="score.py",
    environment=env,
    output_action="append_row",
    append_row_file_name=config['batch_output_filename'],
    mini_batch_size=config['batch_mini_batch_size'],
    error_threshold=config['batch_error_threshold'],
    compute_target=config['batch_target'],
    process_count_per_node=config['batch_process_count_per_node'],
    node_count=config['batch_node_count']
)

batch_step = ParallelRunStep(
    name="batch-step",
    parallel_run_config=parallel_run_config,
    arguments=['--model_name', config['model_name'], '--enable_monitoring', args.m, '--table_name', config["scoring_table_name"]],
    inputs=[batch_dataset_consumption],
    side_inputs=[],
    output=output_dataset,
    allow_reuse=False
)

steps = [batch_step]

print('Creating, validating, and publishing pipeline')
pipeline = Pipeline(workspace=ws, steps=steps)
pipeline.validate()
published_pipeline = pipeline.publish(config['batch_pipeline_name'])

# Output pipeline_id in specified format which will convert it to a variable in Azure DevOps
print(f'Exporting pipeline id {published_pipeline.id} as environment variable pipeline_id')
print(f'##vso[task.setvariable variable=pipeline_id]{published_pipeline.id}')
