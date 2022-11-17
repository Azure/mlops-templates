"""MLOps v2 NLP Python SDK training submission script."""
import os
import argparse

# Azure ML sdk v2 imports
from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential
from azure.ai.ml import MLClient
from azure.ai.ml import command
from azure.ai.ml import Input, Output
from azure.ai.ml import dsl, Input, Output
import json


def get_config_parger(parser: argparse.ArgumentParser = None):
    """Builds the argument parser for the script."""
    if parser is None:
        parser = argparse.ArgumentParser(description=__doc__)

    group = parser.add_argument_group("Azure ML references")
    group.add_argument(
        "--config_location",
        type=str,
        required=False,
        help="Subscription ID",
    )
    group.add_argument(
        "--subscription_id",
        type=str,
        required=False,
        help="Subscription ID",
    )
    group.add_argument(
        "--resource_group",
        type=str,
        required=False,
        help="Resource group name",
    )
    group.add_argument(
        "--workspace_name",
        type=str,
        required=False,
        help="Workspace name",
    )
    group.add_argument(
        "--experiment_name",
        type=str,
        required=False,
        default="nlp_summarization_train",
        help="Experiment name",
    )
    parser.add_argument(
        "--wait",
        default=False,
        action="store_true",
        help="wait for the job to finish",
    )

    return parser

def main():
    """Main entry point for the script."""
    parser = get_config_parger()
    args, _ = parser.parse_known_args()
    print(args)


if __name__ == "__main__":
    main()