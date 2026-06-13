import sys
import argparse
from src.call_me_maybe import CallMeMaybe


def parse_cla() -> argparse.Namespace:
   
    parser = argparse.ArgumentParser()
    parser.add_argument("--function_definition", default="data/input/functions_definition.json")
    parser.add_argument("--input", default="data/input/function_calling_tests.json")
    parser.add_argument("--output", default="data/output/function_calls.json")
    parser.add_argument("--visualize", action="store_true")
    return parser.parse_args()


def main():

    try:
        args = parse_cla()

        call_me_maybe = CallMeMaybe(args=args)
        call_me_maybe.run()
    except Exception as error:
        print(f"Error in main: {error}")
        sys.exit(0)

    if args.visualize:
        try:
            from src.tui import Simulation
            sim = Simulation()
            sim.run()
        except Exception:
            print("TUI Error: call failed")


if __name__ == "__main__":
    main()
