import os
import re
import argparse
import yaml
import shlex

from azureml.core import Workspace
from azureml.core.compute import AksCompute, ComputeTarget
from azureml.core.compute_target import ComputeTargetException

parser = argparse.ArgumentParser("Get inference cluster")
parser.add_argument("-f", type=str, help="Controller Config YAML file")
args, _ = parser.parse_known_args()

with open(args.f, "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
    config = config['variables']
print(config)

ws = Workspace.from_config()

aks_name = config['inference_aks_target']

try:
    aks_target = ComputeTarget(workspace=ws, name=aks_name)
    print('Found existing cluster, use it.')

except ComputeTargetException:
    prov_config = AksCompute.provisioning_configuration()
    # Create the cluster
    aks_target = ComputeTarget.create(workspace = ws,
                                        name = aks_name,
                                        provisioning_configuration = prov_config)

    # Wait for the creation process to complete
    aks_target.wait_for_completion(show_output = True)