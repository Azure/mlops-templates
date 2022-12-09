# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
import argparse
import yaml

from azureml.core import Workspace
from azureml.core.compute import AmlCompute, ComputeTarget

parser = argparse.ArgumentParser("Get compute")
parser.add_argument("-f", type=str, help="AML Config YAML file")
parser.add_argument('--compute_type', type=str, help='Type of compute i.e. training / batch etc.')
args, _ = parser.parse_known_args()

with open(args.f, "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
    config = config['variables']
print(config)

# choose a name for your cluster
#config['training_pipeline_target']
if args.compute_type == 'training':
    compute_name = config['training_target']
    compute_min_nodes = config['training_target_min_nodes']
    compute_max_nodes = config['training_target_max_nodes']
    vm_size = os.environ.get("AML_COMPUTE_CLUSTER_SKU", config['training_target_sku'])
elif args.compute_type == 'batch':
    compute_name = config['batch_target']
    compute_min_nodes = config['batch_target_min_nodes']
    compute_max_nodes = config['batch_target_max_nodes']
    vm_size = os.environ.get("AML_COMPUTE_CLUSTER_SKU", config['batch_target_sku'])
else:
    # This example spins up a cluster of 4 STANDARD_D2_V2 nodes when it does not detect either batch or training parameters
    compute_name = os.environ.get("AML_COMPUTE_CLUSTER_NAME", "cpu-cluster")
    compute_min_nodes = os.environ.get("AML_COMPUTE_CLUSTER_MIN_NODES", 0)
    compute_max_nodes = os.environ.get("AML_COMPUTE_CLUSTER_MAX_NODES", 4)
    vm_size = os.environ.get("AML_COMPUTE_CLUSTER_SKU", "STANDARD_D2_V2")


ws = Workspace.from_config()

if compute_name in ws.compute_targets:
    compute_target = ws.compute_targets[compute_name]
    if compute_target and type(compute_target) is AmlCompute:
        print('found compute target. just use it. ' + compute_name)
else:
    print('creating a new compute target...')
    provisioning_config = AmlCompute.provisioning_configuration(vm_size = vm_size,
                                                                min_nodes = compute_min_nodes, 
                                                                max_nodes = compute_max_nodes)

    # create the cluster
    compute_target = ComputeTarget.create(ws, compute_name, provisioning_config)
    
    # can poll for a minimum number of nodes and for a specific timeout. 
    # if no min node count is provided it will use the scale settings for the cluster
    compute_target.wait_for_completion(show_output=True, min_node_count=None, timeout_in_minutes=20)
    
    # For a more detailed view of current AmlCompute status, use get_status()
    print(compute_target.get_status().serialize())
