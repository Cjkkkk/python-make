import sys
import logging
import argparse
import json
import os
import subprocess

logger = logging.getLogger("python_make")

def get_config(filename):
    if not os.path.isfile(args.config):
        logger.error("Can not find config file %s", args.config)
        exit(0)
    else:
        with open(args.config, "r") as f:
            config = json.loads(f.read())
        return config

def set_logging(if_verbose):
    if if_verbose:
        logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
    else:
        logging.basicConfig(level=logging.WARNING, format='[%(levelname)s] %(message)s')

def check_config(config):
    for target in config:
        if "dependency" not in config[target].keys():
            logging.error("Must provide dependency for target %s", target)
            exit(0)
            
        for key in config[target].keys():
            if key not in ["command", "dependency"]:
                logging.error("Key %s for target %s is not supported", key, target)
                exit(0)

        for dependency in config[target]['dependency']:
            if not dependency in config and not os.path.isfile(dependency):
                logger.error("Can not find file %s", dependency)
                exit(0)

def if_older(a, b):
    """return True if a is older than b, return False if otherwise
    """
    time_a = os.path.getmtime(a)
    time_b = os.path.getmtime(b)
    return time_a < time_b

def compile_target(config, target):
    """return True if target is recompiled, return False if otherwise
    """
    if_needs_recompile = False
    if target not in config:
        logger.error("No rule for target %s", target)
        exit(0)
    for dependency in config[target]["dependency"]:
        if dependency in config and compile_target(config, dependency):
            if_needs_recompile = True
        else:
            if not os.path.isfile(target) or if_older(target, dependency):
                if_needs_recompile = True
    
    # recompile if needed
    if if_needs_recompile:
        logger.info("Compile target: %s", target)
        for command in config[target].get("command", []):
            args = command.split(" ")
            subprocess.run(args)
            logger.info("Run command: %s", command)
    else:
        logger.info("Skip target: %s", target)
    return if_needs_recompile

def main(args):
    os.chdir(args.root)
    set_logging(args.verbose)
    config = get_config(args.config)
    check_config(config)
    compile_target(config, args.target)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--root', type=str, default=".")
    parser.add_argument('-t', '--target', type=str, default="all")
    parser.add_argument('-c', '--config', type=str, default="config.json")
    parser.add_argument('-v', '--verbose', default=False, action="store_true")

    args = parser.parse_args()
    main(args)
