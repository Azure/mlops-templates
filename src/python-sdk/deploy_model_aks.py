import os
import re
import argparse
import yaml

import azureml.core
from azureml.core import Workspace, Experiment, RunConfiguration, Environment
from azureml.core.compute import AksCompute, ComputeTarget
from azureml.core.webservice import Webservice, AksWebservice
from azureml.core.model import Model
from azureml.core.model import InferenceConfig

print("Azure ML SDK version:", azureml.core.VERSION)

parser = argparse.ArgumentParser("Deploy Model to AKS")
parser.add_argument("-f", type=str, help="Controller Config YAML file")
args = parser.parse_args()

with open(args.f, "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
    config = config['variables']
print(config)

print('Connecting to workspace')
ws = Workspace.from_config()
print(f'WS name: {ws.name}\nRegion: {ws.location}\nSubscription id: {ws.subscription_id}\nResource group: {ws.resource_group}')

env = Environment.get(workspace=ws, name=config['inference_environment_name'])
model = Model(ws, config['model_name'])

aks_target = ComputeTarget(workspace=ws, name=config['inference_aks_target'])

inf_config = InferenceConfig(entry_script=config['inference_script'],
                             source_directory='code/src/',
                             environment=env)

# Full definition see https://docs.microsoft.com/en-us/python/api/azureml-core/azureml.core.webservice.akswebservice?view=azure-ml-py
aks_config = {
    'enable_app_insights': config['inference_enable_app_insights'],
    'collect_model_data': config['inference_collect_model_data'],
    'token_auth_enabled': False,
    'auth_enabled': True,
    'cpu_cores': config['inference_cpu_cores_per_replica'],
    'memory_gb': config['inference_memory_gb_per_replica'],
    'autoscale_enabled': True,
    'autoscale_min_replicas': config['inference_autoscale_min_replicas'],
    'autoscale_max_replicas': config['inference_autoscale_max_replicas'],
    'autoscale_refresh_seconds': 10,
    'autoscale_target_utilization': 70
}

aks_service = Model.deploy(workspace=ws,
                           name=config['inference_deployment_name'],
                           models=[model],
                           inference_config=inf_config,
                           deployment_config=AksWebservice.deploy_configuration(**aks_config),
                           deployment_target=aks_target,
                           overwrite=True)

aks_service.wait_for_deployment(show_output = True)
print(aks_service.state)