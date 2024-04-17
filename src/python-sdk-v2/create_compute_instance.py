"""MLOps v2 NLP Python SDK create compute script."""
import os
import argparse
import traceback

# Azure ML sdk v2 imports
from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential
from azure.ai.ml import MLClient
from azure.ai.ml.entities import Environment, BuildContext
from azure.core.exceptions import ResourceExistsError
from azure.ai.ml.entities import ManagedIdentityConfiguration, IdentityConfiguration, AmlCompute, ComputeInstance
from azure.ai.ml.constants import ManagedServiceIdentityType

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
        "--instance_name",
        type=str,
        required=False,
        help="Name of compute cnstance to create",
    )
    parser.add_argument(
        "--size",
        type=str,
        required=False,
        help="Size of compute instance to be created",
    )
    parser.add_argument(
        "--location",
        type=str,
        required=False,
        help="The resource location",
    )
    parser.add_argument(
        "--description",
        type=str,
        required=False,
        help="Description of the resource",
    )
    parser.add_argument(
        "--identity_type",
        type=str,
        required=False,
        help="Identity type of the compute instance, SystemAssigned or UserAssigned",
    )
    parser.add_argument(
        "--user_assigned_identity",
        type=str,
        required=False,
        help="User Assigned Identity ID to be used for the compute instance",
        default="na",
        nargs="?"
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

    # Create a compute instance with system assigned managed identity
    if args.identity_type == ManagedServiceIdentityType.SYSTEM_ASSIGNED:
        # Create an identity configuration for system-assigned managed identity
        sys_identity_config = IdentityConfiguration(type = ManagedServiceIdentityType.SYSTEM_ASSIGNED)

        ci_basic = ComputeInstance(
            name=args.instance_name,
            size=args.size,
            location=args.location,
            description=args.description,
            identity = sys_identity_config
        )
    # Create a compute instance with user assigned managed identity
    elif args.identity_type == ManagedServiceIdentityType.USER_ASSIGNED:
        # Create an identity configuration from the user-assigned managed identity
        managed_identity = ManagedIdentityConfiguration(resource_id=f"/subscriptions/{args.subscription_id}/resourcegroups/{args.resource_group}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{args.user_assigned_identity}")
        ua_identity_config = IdentityConfiguration(type = ManagedServiceIdentityType.USER_ASSIGNED, user_assigned_identities=[managed_identity])

        ci_basic = ComputeInstance(
            name=args.instance_name,
            size=args.size,
            location=args.location,
            description=args.description,
            identity = ua_identity_config
        )
    # Create a compute instance without managed identity
    else:
        ci_basic = ComputeInstance(
            name=args.instance_name,
            size=args.size,
            location=args.location,
            description=args.description
        )

    ml_client.begin_create_or_update(ci_basic).result()

if __name__ == "__main__":
    main()