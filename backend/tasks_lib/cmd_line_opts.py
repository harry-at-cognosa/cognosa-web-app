import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Run Tasks command line options")

    # -n / --name : string with default
    parser.add_argument("-s", "--secondary", type=int, default=0, help="Specify this as a secondary run_tasks instance. With unique number.")

    # -dv / --dummy_vdb : boolean flag
    parser.add_argument("-dv", "--dummy_vdb", action="store_true", help="Dummy VectorDB flag (default: False)")
    
    # -dl / --dummy_llm : boolean flag
    parser.add_argument("-dl", "--dummy_llm", action="store_true", help="Dummy LLM flag (default: False)")

    return parser.parse_args()

args = parse_args()

SECONDARY_INSTANCE_NUMBER = args.secondary
IS_PRIMARY_INSTANCE = not SECONDARY_INSTANCE_NUMBER
IS_SECONDARY_INSTANCE = bool(SECONDARY_INSTANCE_NUMBER)
AP_NAME = f"run_tasks_secondary_{SECONDARY_INSTANCE_NUMBER}" if IS_SECONDARY_INSTANCE else "run_tasks_primary"
IS_DUMMY_VDB = args.dummy_vdb
IS_DUMMY_LLM = args.dummy_llm
