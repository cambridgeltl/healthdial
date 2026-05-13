"""Download the HEALTHDIAL dataset from HuggingFace.

The dataset lives at: https://huggingface.co/datasets/cambridgeltl/HealthDial

Usage:
    huggingface-cli login   # only needed for gated/private repos
    python download_hf.py --output-dir data
    python download_hf.py --languages english arabic --output-dir data
"""

import argparse
import os
import tarfile

from huggingface_hub import hf_hub_download

REPO_ID = "cambridgeltl/HealthDial"
REPO_TYPE = "dataset"

ALL_LANGUAGES = ["english", "arabic", "chinese", "spanish"]
SYSTEM_TARS = [
    "system_audio.part1.tar.gz",
    "system_audio.part2.tar.gz",
    "system_audio.part3.tar.gz",
]
USER_TARS = ["audio.part1.tar.gz", "audio.part2.tar.gz"]


def safe_extract(tar_path, extract_to):
    """Extract a tar.gz archive to the target folder."""
    print(f"Extracting {tar_path} -> {extract_to}")
    os.makedirs(extract_to, exist_ok=True)
    with tarfile.open(tar_path, "r:gz") as tar:
        tar.extractall(path=extract_to)


def download_and_extract(language, output_dir):
    """Download and extract all archives for one language."""
    lang_dir = os.path.join(output_dir, language)
    os.makedirs(lang_dir, exist_ok=True)

    print(f"\n=== Processing {language} ===")

    for filename in SYSTEM_TARS:
        path_in_repo = f"{language}/{filename}"
        print(f"Downloading {path_in_repo} ...")
        tar_path = hf_hub_download(
            repo_id=REPO_ID,
            repo_type=REPO_TYPE,
            filename=path_in_repo,
            local_dir=lang_dir,
        )
        safe_extract(tar_path, os.path.join(lang_dir, "system_audio"))

    for filename in USER_TARS:
        path_in_repo = f"{language}/{filename}"
        print(f"Downloading {path_in_repo} ...")
        tar_path = hf_hub_download(
            repo_id=REPO_ID,
            repo_type=REPO_TYPE,
            filename=path_in_repo,
            local_dir=lang_dir,
        )
        safe_extract(tar_path, os.path.join(lang_dir, "audio"))

    print(f"Finished {language}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--languages",
        nargs="+",
        choices=ALL_LANGUAGES,
        default=ALL_LANGUAGES,
        help="Languages to download (default: all)",
    )
    parser.add_argument(
        "--output-dir",
        default="data",
        help="Root output directory (default: ./data)",
    )
    args = parser.parse_args()

    for lang in args.languages:
        download_and_extract(lang, args.output_dir)

    print("\nAll requested languages downloaded and extracted.")


if __name__ == "__main__":
    main()
