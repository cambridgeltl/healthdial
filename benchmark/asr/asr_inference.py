import argparse
import os
import json

import asr_utils
import evaluation
import inference


def main(args):
    data = asr_utils.load_data(args.folder)
    if args.stage == "evaluation":
        metrics = evaluation.evaluate(data, args.model_name)
    elif args.stage == "inference":
        updated_data = inference.run_inference(data, args.model_name, args.folder)
        with open(
            os.path.join(args.folder, "second_processed_result.json"), "w", encoding="utf-8") as file:
            json.dump(updated_data, file, indent=4, ensure_ascii = False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Command line arguments")
    parser.add_argument(
        "-f", "--folder", type=str, help="Folder where the data is stored"
    )
    parser.add_argument(
        "-m", "--model_name", type=str, help="The model used for inference/evaluation"
    )
    parser.add_argument(
        "-s",
        "--stage",
        type=str,
        help="The stage we're at; Options: [inference, evaluation]",
    )
    args = parser.parse_args()

    main(args)
