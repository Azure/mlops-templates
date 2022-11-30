"""MLOps v2 NLP Python SDK register environment script."""
import os
import argparse
import traceback

# Azure ML sdk v2 imports
from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential
from azure.ai.ml import MLClient
from azure.ai.ml.entities import Environment, BuildContext
from azure.core.exceptions import ResourceExistsError


def get_config_parger(parser: argparse.ArgumentParser = None):
    """Builds the argument parser for the script."""
    if parser is None:
        parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument(
        "--subscription_id",
        type=str,
        required=False,
        help="Subscription ID",
    )
    parser.add_argument(
        "--build_type",
        type=str,
        required=False,
        help="Resource group name",
    )
    parser.add_argument(
        "--resource_group",
        type=str,
        required=False,
        help="Resource group name",
    )
    parser.add_argument(
        "--workspace_name",
        type=str,
        required=False,
        help="Workspace name",
    )
    parser.add_argument(
        "--exists_ok",
        default=False,
        action="store_true",
        help="if True, will not fail if environment already exists",
    )

    parser.add_argument(
        "--environment_name",
        default="nlp_summarization_train",
        type=str,
    )
    parser.add_argument(
        "--environment_version",
        default="mlopsv2-july2022",
        type=str,
    )
    parser.add_argument(
        "--environment_context_path",
        default=os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "..",
            "data-science",
            "environments",
            "training",
        ),
        type=str,
    )
    return parser


def connect_to_aml(args):
    """Connect to Azure ML workspace using provided cli arguments."""
    try:
        credential = DefaultAzureCredential()
        # Check if given credential can get token successfully.
        credential.get_token("https://management.azure.com/.default")
    except Exception as ex:
        # Fall back to InteractiveBrowserCredential in case DefaultAzureCredential not work
        credential = InteractiveBrowserCredential()

    # Get a handle to workspace
    try:
        # ml_client to connect using local config.json
        ml_client = MLClient.from_config(credential, path='config.json')

    except Exception as ex:
        print(
            "Could not find config.json, using config.yaml refs to Azure ML workspace instead."
        )

        # tries to connect using cli args if provided else using config.yaml
        ml_client = MLClient(
            subscription_id=args.subscription_id,
            resource_group_name=args.resource_group,
            workspace_name=args.workspace_name,
            credential=credential,
        )
    return ml_client


def main():
    """Main entry point for the script."""
    parser = get_config_parger()
    args, _ = parser.parse_known_args()
    ml_client = connect_to_aml(args)

    
    build_type = args.build_type
    if build_type == 'docker':
        print("Using docker build contect")
        custom_env = Environment(
            name=args.environment_name,
            build=BuildContext(path=args.environment_context_path),
            tags={"project": "mlopsv2", "url": "https://github.com/Azure/mlops-v2"},
        )

        try:
            custom_env_create_job = ml_client.environments.create_or_update(custom_env)
            print(
                f"Environment with name {custom_env_create_job.name} is registered to workspace, the environment version is {custom_env_create_job.version}"
            )
        except ResourceExistsError as ex:
            print(f"Failed to create environment: {traceback.format_exc()}")
            if not args.exists_ok:
                raise
    else:
        print("Using conda definition")


if __name__ == "__main__":
    main()