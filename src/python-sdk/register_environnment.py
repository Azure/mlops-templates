# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import argparse
from azureml.core import Workspace, Environment


def parse_args():
    parser = argparse.ArgumentParser(description="Register environment")
    parser.add_argument("-n", type=str, help="Name of the environment you want to register")
    parser.add_argument("-t", type=str, help="Type of enviroment build", choices=["conda", "folder", "dockerfile"])
    parser.add_argument("-f", type=str, help="Path to environment definition (conda yaml, folder, Dockerfile")
    parser.add_argument("-b", type=str, help="Build Docker image for Environment", default='false')
    parser.add_argument("-m", type=str, help="Enable Data and Model Monitoring", default='false')
    return parser.parse_args()

def main():
    args = parse_args()
    ws = Workspace.from_config()
    condafile = args.f
    
    print(args.m)

    if (args.m.lower() == 'true' or args.m == '1' or args.m.lower() == 'yes'):
        filename = "".join(condafile.split(".")[:-1])
        print(filename)
        fileext = condafile.split(".")[-1]
        print(fileext)
        condafile = filename+"_monitor."+fileext 
    
    print(condafile)
    

    if args.t == "conda":
        env = Environment.from_conda_specification(name=args.n, file_path=condafile)
    elif args.t == "folder":
        env = Environment.load_from_directory(path=args.f)
        env.name = args.n
    elif args.t == "dockerfile":
        env = Environment.from_dockerfile(name=args.n, dockerfile=args.f)
    else:
        raise ValueError(f"Type {args.t} not supported")

    print(f"About to register enviroment {args.n} to workspace: {env}")
    env.register(workspace=ws)
    if (args.b.lower == 'true' or args.b == '1' or args.b.lower == 'yes'):
        print("Building environment")
        build = env.build(ws)
        build.wait_for_completion(show_output=True)

if __name__ == "__main__":
    main()
