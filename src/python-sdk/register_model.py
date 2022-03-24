import os
import argparse
from azureml.core import Run, Experiment
from azureml.pipeline.core import PipelineRun

parser = argparse.ArgumentParser()
parser.add_argument('--model_name', type=str, help='Name under which model will be registered')
parser.add_argument('--model_path', type=str, help='Model directory')
args, _ = parser.parse_known_args()

print(f'Arguments: {args}')
model_name = args.model_name
model_path = args.model_path

# current run is the registration step
current_run = Run.get_context()

# parent run is the overall pipeline
parent_run = current_run.parent
print(f'Parent run id: {parent_run.id}')

# find pipeline step named 'train-step'
pipeline_run = PipelineRun(parent_run.experiment, parent_run.id)
training_run = pipeline_run.find_step_run('train-step')[0]
print(f'Training run: {training_run}')

model = training_run.register_model(model_name=args.model_name,
                                    model_path=args.model_path)