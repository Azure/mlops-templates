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

print("Azure ML SDK version:", azureml.core.VERSION)

parser = argparse.ArgumentParser("Deploy Training Pipeline")
parser.add_argument("-f", type=str, help="Controller Config YAML file")
args = parser.parse_args()

with open(args.f, "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
    config = config['variables']
print(config)


ws = Workspace.from_config()
env = Environment.get(workspace=ws, name=config['training_environment_name'])
runconfig = RunConfiguration()
runconfig.environment = env
training_dataset_consumption = None
arguments = []
inputs = []

for arg in shlex.split(config['training_command']):
    print(f"Processing training argument: {arg}")
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

train_step = PythonScriptStep(name="train-step",
                        runconfig=runconfig,
                        compute_target=config['training_pipeline_target'],
                        source_directory="code/src/",
                        script_name=arguments[0],
                        arguments=arguments[1:],
                        inputs=inputs,
                        allow_reuse=False)

register_step = PythonScriptStep(name="register-step",
                        runconfig=runconfig,
                        compute_target=config['training_pipeline_target'],
                        source_directory="templates/shared_code/",
                        script_name="register_model.py",
                        arguments=['--model_name', config['model_name'], '--model_path', 'outputs/'],
                        allow_reuse=False)

register_step.run_after(train_step)
steps = [train_step, register_step]

print('Creating, validating, and publishing pipeline')
pipeline = Pipeline(workspace=ws, steps=steps)
pipeline.validate()
published_pipeline = pipeline.publish(config['training_pipeline_name'])

# Output pipeline_id in specified format which will convert it to a variable in Azure DevOps
print(f'Exporting pipeline id {published_pipeline.id} as environment variable pipeline_id')
print(f'##vso[task.setvariable variable=pipeline_id]{published_pipeline.id}')