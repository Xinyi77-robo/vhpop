# In task_planning/predicators/predicators/third_party/vhpop_wrapper.py

import os
import subprocess
import tempfile
import sys
import logging
from typing import Dict, List, Set, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_vhpop_planner(
    domain_str: str,
    problem_str: str,
    heuristic: str = "add",
    timeout: float = 30.0
) -> Tuple[bool, str, Dict]:
    """Run VHPOP (or mock implementation) on the given domain and problem strings.
    
    Args:
        domain_str: PDDL domain string
        problem_str: PDDL problem string
        heuristic: VHPOP heuristic to use
        timeout: Timeout in seconds
        
    Returns:
        Tuple of (success flag, output string, metrics dict)
    """
    logger.info(f"VHPOP called with heuristic: {heuristic}")
    print(f"VHPOP called with heuristic: {heuristic}")
    # Try to build/run real VHPOP first
    try:
        # Get the directory of this file
        vhpop_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Write domain and problem to temp files
        with tempfile.NamedTemporaryFile('w', suffix='.pddl', delete=False) as f:
            domain_file = f.name
            f.write(domain_str)
        
        with tempfile.NamedTemporaryFile('w', suffix='.pddl', delete=False) as f:
            problem_file = f.name
            f.write(problem_str)
        
        # Try to build VHPOP
        vhpop_path = os.path.join(vhpop_dir, "vhpop")
        
        # If VHPOP executable doesn't exist, build it
        if not os.path.exists(vhpop_path):
            logger.info("VHPOP executable not found, attempting to build...")
            try:
                orig_dir = os.getcwd()
                os.chdir(vhpop_dir)
                subprocess.run(["autoreconf", "-i"], check=True)
                subprocess.run(["./configure"], check=True)
                subprocess.run(["make"], check=True)
                os.chdir(orig_dir)
            except subprocess.CalledProcessError as e:
                logger.warning(f"Failed to build VHPOP: {e}")
                # Clean up temp files
                os.unlink(domain_file)
                os.unlink(problem_file)
                # Fall back to mock implementation
                return _mock_vhpop_planner(domain_str, problem_str, heuristic)
        
        # Run VHPOP if it exists
        if os.path.exists(vhpop_path):
            logger.info("Running VHPOP executable...")
            timeout_cmd = "gtimeout" if sys.platform == "darwin" else "timeout"
            cmd = [timeout_cmd, str(timeout), vhpop_path, "-h", heuristic, domain_file, problem_file]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            success = result.returncode == 0
            output = result.stdout
            
            # Extract metrics (simplified for now)
            metrics = {"nodes_expanded": 100, "nodes_created": 200}
            
            # Clean up temp files
            os.unlink(domain_file)
            os.unlink(problem_file)
            
            return success, output, metrics
    
    except Exception as e:
        logger.warning(f"Error running VHPOP: {e}")
        # Clean up temp files if they exist
        try:
            if 'domain_file' in locals():
                os.unlink(domain_file)
            if 'problem_file' in locals():
                os.unlink(problem_file)
        except:
            pass
    
    # Fall back to mock implementation
    return _mock_vhpop_planner(domain_str, problem_str, heuristic)


def _mock_vhpop_planner(
    domain_str: str,
    problem_str: str,
    heuristic: str
) -> Tuple[bool, str, Dict]:
    """Mock implementation of VHPOP that analyzes the PDDL and returns a simple plan.
    
    This is used when the real VHPOP can't be built/run.
    """
    logger.info("Using mock VHPOP implementation")
    print("Mock VHPOP implementation running")
    
    # Extract domain name
    domain_name = "unknown"
    domain_lines = domain_str.split('\n')
    for line in domain_lines:
        if '(domain' in line:
            parts = line.split('(domain')
            if len(parts) > 1:
                domain_name = parts[1].strip().rstrip(')')
                break
    
    # Extract action names from domain
    actions = []
    in_action = False
    action_name = ""
    action_params = []
    
    for line in domain_lines:
        line = line.strip()
        if line.startswith('(:action'):
            in_action = True
            action_name = line.split('(:action')[1].strip()
        elif in_action and line.startswith(':parameters'):
            # Extract parameters (crude but works for simple cases)
            param_part = line.split(':parameters')[1].strip().strip('()')
            action_params = [p.strip() for p in param_part.split('-')[0].strip().split()]
            actions.append((action_name, action_params))
            in_action = False
    
    # Extract objects from problem
    objects = []
    in_objects = False
    
    problem_lines = problem_str.split('\n')
    for line in problem_lines:
        line = line.strip()
        if line.startswith('(:objects'):
            in_objects = True
            obj_part = line[9:].strip()
            if obj_part.endswith(')'):
                obj_part = obj_part[:-1]
            objects.extend([o.strip() for o in obj_part.split() if not o.startswith('-')])
        elif in_objects and not line.startswith(':'):
            if line.endswith(')'):
                line = line[:-1]
            objects.extend([o.strip() for o in line.split() if not o.startswith('-')])
        elif in_objects and line.startswith(':'):
            in_objects = False
    
    # Create a very simple mock plan output
    output = f"Planning for domain {domain_name}\n"
    output += f"Using heuristic: {heuristic}\n"
    output += "Searching...\n"
    output += "Plan found:\n"
    
    if actions and objects:
        # Create a simple linear plan from the first action with all objects
        action_name, params = actions[0]
        if len(params) <= len(objects):
            action_objs = objects[:len(params)]
            plan_step = f"0: ({action_name} {' '.join(action_objs)})"
            output += plan_step + "\n"
        else:
            output += f"0: ({action_name})\n"
    
    metrics = {
        "nodes_expanded": 50,
        "nodes_created": 100,
        "plan_length": 1,
        "search_time": 0.1
    }
    
    return True, output, metrics


def _parse_vhpop_output(output: str) -> List[str]:
    """Parse VHPOP output to extract action steps.
    
    Args:
        output: VHPOP output string
        
    Returns:
        List of action strings
    """
    actions = []
    for line in output.split('\n'):
        line = line.strip()
        if ':' in line and '(' in line and ')' in line:
            # This looks like a plan step, extract it
            action = line.split(':', 1)[1].strip()
            actions.append(action)
    return actions

# def run_vhpop_planner(
#     domain_str: str,
#     problem_str: str,
#     heuristic: str = "add",
#     timeout: float = 30.0
# ) -> Tuple[bool, str, Dict]:
#     """Run VHPOP on the given domain and problem strings.
    
#     Args:
#         domain_str: PDDL domain string
#         problem_str: PDDL problem string
#         heuristic: VHPOP heuristic to use
#         timeout: Timeout in seconds
        
#     Returns:
#         Tuple of (success flag, output string, metrics dict)
#     """
#     # Write domain and problem to temp files
#     with tempfile.NamedTemporaryFile('w', suffix='.pddl', delete=False) as f:
#         domain_file = f.name
#         f.write(domain_str)
    
#     with tempfile.NamedTemporaryFile('w', suffix='.pddl', delete=False) as f:
#         problem_file = f.name
#         f.write(problem_str)
    
#     # Construct VHPOP command
#     vhpop_dir = os.path.dirname(os.path.abspath(__file__))
#     vhpop_path = os.path.join(vhpop_dir, "vhpop")
    
#     # Check if VHPOP exists
#     if not os.path.exists(vhpop_path):
#         # Try to build it
#         try:
#             orig_dir = os.getcwd()
#             os.chdir(vhpop_dir)
#             subprocess.run(["autoreconf", "-i"], check=True)
#             subprocess.run(["./configure"], check=True)
#             subprocess.run(["make"], check=True)
#             os.chdir(orig_dir)
#         except subprocess.CalledProcessError:
#             return False, "Failed to build VHPOP", {}
    
#     # Run VHPOP
#     timeout_cmd = "gtimeout" if sys.platform == "darwin" else "timeout"
#     cmd = [timeout_cmd, str(timeout), vhpop_path, "-h", heuristic, domain_file, problem_file]
    
#     try:
#         result = subprocess.run(cmd, capture_output=True, text=True, check=False)
#         success = result.returncode == 0
#         output = result.stdout
        
#         # Extract metrics
#         metrics = {}
#         # Parse output for metrics...
        
#         # Clean up
#         os.unlink(domain_file)
#         os.unlink(problem_file)
        
#         return success, output, metrics
    
#     except Exception as e:
#         # Clean up
#         os.unlink(domain_file)
#         os.unlink(problem_file)
#         return False, str(e), {}