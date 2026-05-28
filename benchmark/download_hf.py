"""Download the HEALTHDIAL dataset from HuggingFace.

The dataset lives at: https://huggingface.co/datasets/cambridgeltl/HealthDial

Usage:
    huggingface-cli login   # only needed for gated/private repos
    python download_hf.py --output-dir data
    python download_hf.py --languages english arabic --output-dir data
"""

import argparse
import os
import shutil
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
# (path-in-repo suffix, local filename). The dialogue file is renamed so it
# matches the path that every downstream script expects.
LANG_JSON_FILES = [
    ("dialogue_list_final_with_sys_speech.json", "dialogue_list_final.json"),
    ("user_list_final.json", "user_list_final.json"),
]
ROOT_FILES = ["who_database.json"]


def safe_extract(tar_path, extract_to):
    """Extract a tar.gz archive to the target folder."""
    print(f"Extracting {tar_path} -> {extract_to}")
    os.makedirs(extract_to, exist_ok=True)
    with tarfile.open(tar_path, "r:gz") as tar:
        tar.extractall(path=extract_to)


def download_to(path_in_repo, local_dir, local_name=None):
    """Download a single file from the dataset repo into ``local_dir``.

    If ``local_name`` is provided and differs from the basename of
    ``path_in_repo``, the downloaded file is renamed in-place.
    """
    print(f"Downloading {path_in_repo} ...")
    src = hf_hub_download(
        repo_id=REPO_ID,
        repo_type=REPO_TYPE,
        filename=path_in_repo,
        local_dir=local_dir,
    )
    if local_name is None:
        return src
    dst = os.path.join(local_dir, local_name)
    if os.path.abspath(src) != os.path.abspath(dst):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.move(src, dst)
    return dst


def download_and_extract(language, output_dir, skip_audio=False):
    """Download JSONs and (optionally) audio archives for one language."""
    lang_dir = os.path.join(output_dir, language)
    os.makedirs(lang_dir, exist_ok=True)

    print(f"\n=== Processing {language} ===")

    for repo_name, local_name in LANG_JSON_FILES:
        download_to(f"{language}/{repo_name}", output_dir, local_name=f"{language}/{local_name}")

    if skip_audio:
        print(f"Skipping audio for {language} (--no-audio)")
    else:
        for filename in SYSTEM_TARS:
            tar_path = download_to(f"{language}/{filename}", lang_dir)
            safe_extract(tar_path, os.path.join(lang_dir, "system_audio"))

        for filename in USER_TARS:
            tar_path = download_to(f"{language}/{filename}", lang_dir)
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
    parser.add_argument(
        "--no-audio",
        action="store_true",
        help="Skip the audio tarballs and only fetch the JSON files (knowledge base + dialogues).",
    )
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    for filename in ROOT_FILES:
        download_to(filename, args.output_dir)

    for lang in args.languages:
        download_and_extract(lang, args.output_dir, skip_audio=args.no_audio)

    print("\nAll requested files downloaded.")


if __name__ == "__main__":
    main()
