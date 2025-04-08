# test_vhpop.py
import sys
import tempfile
from vhpop_wrapper import run_vhpop_planner

def test_vhpop_wrapper():
    # Logistics domain with complex ordering constraints
    domain_str = """
    (define (domain logistics)
      (:requirements :strips :typing)
      (:types 
        package - object
        location - object
        city - location
        airport - location
        truck - object
        airplane - object
      )
      (:predicates 
        (in-city ?loc - location ?city - city)
        (at ?obj - object ?loc - location)
        (in ?pkg - package ?veh - object)
      )
      (:action load-truck
        :parameters (?pkg - package ?truck - truck ?loc - location)
        :precondition (and (at ?truck ?loc) (at ?pkg ?loc))
        :effect (and (not (at ?pkg ?loc)) (in ?pkg ?truck))
      )
      (:action unload-truck
        :parameters (?pkg - package ?truck - truck ?loc - location)
        :precondition (and (at ?truck ?loc) (in ?pkg ?truck))
        :effect (and (not (in ?pkg ?truck)) (at ?pkg ?loc))
      )
      (:action load-airplane
        :parameters (?pkg - package ?airplane - airplane ?loc - airport)
        :precondition (and (at ?airplane ?loc) (at ?pkg ?loc))
        :effect (and (not (at ?pkg ?loc)) (in ?pkg ?airplane))
      )
      (:action unload-airplane
        :parameters (?pkg - package ?airplane - airplane ?loc - airport)
        :precondition (and (at ?airplane ?loc) (in ?pkg ?airplane))
        :effect (and (not (in ?pkg ?airplane)) (at ?pkg ?loc))
      )
      (:action drive-truck
        :parameters (?truck - truck ?from - location ?to - location ?city - city)
        :precondition (and (at ?truck ?from) (in-city ?from ?city) (in-city ?to ?city))
        :effect (and (not (at ?truck ?from)) (at ?truck ?to))
      )
      (:action fly-airplane
        :parameters (?airplane - airplane ?from - airport ?to - airport)
        :precondition (at ?airplane ?from)
        :effect (and (not (at ?airplane ?from)) (at ?airplane ?to))
      )
    )
    """
    
    # Complex logistics problem with multiple cities, packages, and vehicles
    problem_str = """
    (define (problem logistics-complex)
      (:domain logistics)
      (:objects
        pkg1 pkg2 pkg3 - package
        truck1 truck2 - truck
        airplane1 - airplane
        sfo lax jfk - airport
        berkeley palo-alto - location
        san-francisco los-angeles new-york - city
      )
      (:init
        (in-city sfo san-francisco)
        (in-city lax los-angeles)
        (in-city jfk new-york)
        (in-city berkeley san-francisco)
        (in-city palo-alto san-francisco)
        
        (at pkg1 berkeley)
        (at pkg2 palo-alto)
        (at pkg3 lax)
        
        (at truck1 berkeley)
        (at truck2 palo-alto)
        (at airplane1 sfo)
      )
      (:goal (and
        (at pkg1 jfk)
        (at pkg2 lax)
        (at pkg3 palo-alto)
      ))
    )
    """
    
    print("Testing VHPOP wrapper with complex logistics problem...")
    print("Domain:")
    print(domain_str)
    print("\nProblem:")
    print(problem_str)
    
    # Try different heuristics to get more interesting plans
    heuristics = ["add", "addr", "oc", "oc1", "loc", "loc1"]
    best_output = None
    best_heuristic = None
    
    for heuristic in heuristics:
        print(f"\nTrying heuristic: {heuristic}")
        success, output, metrics = run_vhpop_planner(domain_str, problem_str, heuristic, 30.0)
        print(f"Success: {success}")
        print(f"Output: {output}")
        print(f"Metrics: {metrics}")
        
        if success and (best_output is None or len(output.split('\n')) > len(best_output.split('\n'))):
            best_output = output
            best_heuristic = heuristic
    
    if best_output:
        print(f"\nBest plan found with heuristic: {best_heuristic}")
        print("Plan:")
        print(best_output)
        
        # Save the output to a file for visualization
        output_file = "/home/veronica/Documents/Semantic_Action_Recognition/task_planning/predicators/predicators/third_party/vhpop/vhpop_output.txt"
        with open(output_file, 'w') as f:
            f.write(best_output)
        print(f"\nOutput saved to {output_file}")
        
        return True
    else:
        print("\nNo successful plan found with any heuristic")
        return False

if __name__ == "__main__":
    success = test_vhpop_wrapper()
    sys.exit(0 if success else 1)