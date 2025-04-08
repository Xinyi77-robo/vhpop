#!/usr/bin/env python3
"""Test script for VHPOP with burger environment."""

import os
import sys
import logging
from typing import List, Set, Tuple

# Add the predicators root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from predicators import utils
from predicators.envs.burger import BurgerEnv
from predicators.structs import Task, Predicate, Type, NSRT
from predicators.planning import _sesame_plan_with_vhpop
from predicators.settings import CFG

def run_burger_test() -> None:
    """Run a test of VHPOP with the burger environment."""
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Initialize the burger environment
    env = BurgerEnv()
    
    # Get predicates, types, and options
    predicates = env.predicates
    types = env.types
    options = env.options
    
    # Create a simple task
    task = env.get_train_tasks()[0]  # Get the first training task
    
    # Log some details about the task
    logger.info("Task goal: %s", task.goal)
    logger.info("Initial state objects: %s", task.init.objects)
    logger.info("Number of NSRTs: %d", len(env.nsrts))
    
    # Try planning with VHPOP
    try:
        logger.info("Attempting to plan with VHPOP...")
        options, skeleton, metrics = _sesame_plan_with_vhpop(
            task=task,
            option_model=env.option_model,
            nsrts=env.nsrts,
            predicates=predicates,
            types=types,
            timeout=CFG.vhpop_timeout,
            seed=0,
            max_horizon=100,
            heuristic="add"
        )
        logger.info("Planning succeeded!")
        logger.info("Plan length: %d", len(options))
        logger.info("Skeleton length: %d", len(skeleton))
        logger.info("Metrics: %s", metrics)
    except Exception as e:
        logger.error("Planning failed: %s", str(e))
        raise

if __name__ == "__main__":
    run_burger_test() 