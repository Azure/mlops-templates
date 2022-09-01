# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

python --version
pip install azureml-sdk==1.41.0
pip install azureml-dataset-runtime --upgrade
pip install azure-ai-ml==0.0.62653692 --extra-index-url https://azuremlsdktestpypi.azureedge.net/sdk-cli-v2
pip install --upgrade git+https://github.com/microsoft/AzureML-Observability#subdirectory=aml-obs-collector
pip install --upgrade git+https://github.com/microsoft/AzureML-Observability#subdirectory=aml-obs-client
sudo apt install dotnet-runtime-deps-2.1
sudo apt install dotnet-runtime-2.1
