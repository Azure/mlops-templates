# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
import argparse
from azureml.core import Workspace, Environment


def parse_args():
    parser = argparse.ArgumentParser(description="Register environment")
    parser.add_argument("-n", type=str, help="Name of the environment you want to register")
    parser.add_argument("-f", type=str, help="Path to conda environment yaml file")
    parser.add_argument("-b", type=str, help="Build Docker image for Environment", default='false')
    return parser.parse_args()

def main():
    args = parse_args()
    ws = Workspace.from_config()
    env = Environment.from_conda_specification(name=args.n, file_path=args.f)
    print(f"About to register enviroment {args.n} to workspace: {env}")
    env.register(workspace=ws)
    if (args.b.lower == 'true' or args.b == '1' or args.b.lower == 'yes'):
        print("Building environment")
        build = env.build(ws)
        build.wait_for_completion(show_output=True)

if __name__ == "__main__":
    main()