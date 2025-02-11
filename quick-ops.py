#!/usr/bin/env python3
import iterm2
import yaml
import fire
import argparse
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# Get the path to the directory containing this file
current_directory = os.path.dirname(os.path.realpath(__file__))
logger.debug(f"Script's directory: {current_directory}")


async def main(connection):
    parser = argparse.ArgumentParser(description="Quick Ops Script")
    parser.add_argument("--config", type=str, default=f"{current_directory}/config.yaml", help="ath to the configuration file")
    parser.add_argument("--org", type=str, default="codelawcorp", help="The organization to use")
    args = parser.parse_args()

    logger.debug(f"Org: {args.org}")
    logger.debug(f"Config: {args.config}")

    # Load configuration from config.yaml
    with open(args.config, "r") as file:
        config = yaml.safe_load(file)
    app = await iterm2.async_get_app(connection)
    window = app.current_window

    # If there is no current window, create one
    if window is None:
        window = await app.async_create_window()

    # Create a new tab
    tab = await window.async_create_tab()
    session = tab.current_session

    logger.debug(config["orgs"][args.org]["layers"])
    panes = []
    for layer_name, layer_value in config["orgs"][args.org]["layers"].items():
        logger.debug(f"Layer: {layer_name}")
        directory = layer_value["tf_directory"]
        for environment_name, environment_value in layer_value["environments"].items():
            logger.debug(f"Environment: {environment_name}")
            for region in environment_value["regions"]:
                logger.debug(f"Region: {region}")
                safe_ops_args = f"{args.org} {layer_name} {environment_name} {region} {directory}"
                logger.info(f"Safe Ops Args: {safe_ops_args}")
                panes.append(safe_ops_args)

    # panes = [
    #     "prod us-east-1",
    #     "prod us-west-2",
    #     "prod ca-central-1",
    #     "prod eu-central-1",
    #     "prod af-south-1",
    #     "prod ap-southeast-2",
    #     "prod eu-west-2",
    #     "stg eu-west-2",
    #     "qa eu-west-2",
    #     "dev eu-west-2",
    # ]

    first = True
    for pane in panes:
        if first:
            await session.async_send_text(f"source safe-ops {pane}\n")
            await session.async_send_text(f"echo 'source safe-ops {pane}'\n")
            first = False
        else:
            # Split the current session into a new pane
            session = await session.async_split_pane(vertical=False)
            await session.async_send_text(f"source safe-ops {pane}\n")
            await session.async_send_text(f"echo 'source safe-ops {pane}'\n")




if __name__ == "__main__":
    iterm2.run_until_complete(main)