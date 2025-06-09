"""
Update README.md with a CloudFormation Template Table

This script scans all folders in the `templates/` directory for `template.yaml` files,
extracts their descriptions, generates a Markdown table of available templates,
and inserts it between predefined markers in a README.md file.

Usage:
    python update_readme.py --bucket <s3-bucket-name> [--branch main] [--readme README.md]

Markers expected in README.md:
    <!-- TEMPLATE TABLE START -->
    <!-- TEMPLATE TABLE END -->
"""

import argparse
import logging
import re
from pathlib import Path
from typing import Dict, List

import yaml  # type: ignore

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

START_MARKER = "<!-- TEMPLATE TABLE START -->"
END_MARKER = "<!-- TEMPLATE TABLE END -->"


def extract_description(template_path: Path) -> str:
    """
    Extract the Description field from CloudFormation template YAML.
    """
    try:
        with open(template_path, "r") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        logger.error(f"Failed to parse YAML file {template_path}: {e}")
        raise
    except FileNotFoundError:
        logger.error(f"Template file not found: {template_path}")
        raise

    desc = data.get("Description") if data else None
    if not desc or not isinstance(desc, str):
        logger.warning(f"No description found in {template_path}")
        raise ValueError(
            f"No description found in {template_path}. Please add a 'Description' field."
        )
    return desc.strip()


def list_all_folders(root_folder_name: str) -> set[str]:
    """
    Given a root folder name (like 'templates'), return the set of all first-level subfolder names inside it.
    """
    root_path = Path(root_folder_name)
    if not root_path.exists() or not root_path.is_dir():
        return set()
    return {p.name for p in root_path.iterdir() if p.is_dir()}


def create_entities_map(bucket_name: str, base_branch: str) -> List[Dict[str, str]]:
    """
    Create a list of template metadata including name, description, and S3 URL.
    """
    all_folders = list_all_folders("templates")
    if not all_folders:
        logger.warning("No folders found in 'templates' directory.")
        return []

    entities_map = []

    for folder in sorted(all_folders):
        template_path = Path("templates") / folder / "template.yaml"
        if not template_path.exists():
            logger.warning(f"Template file not found for {folder}: {template_path}")
            continue

        try:
            description = extract_description(template_path)
        except Exception as e:
            logger.warning(str(e))
            continue

        url = (
            f"https://{bucket_name}.s3.ap-south-1.amazonaws.com/"
            f"jd-35656/{base_branch}/cfts/templates"
            f"/{folder}/template.yaml"
        )
        entities_map.append(
            {
                "name": folder,
                "description": description,
                "url": url,
            }
        )

    return entities_map


def generate_markdown_table(entities_map: List[Dict[str, str]]) -> str:
    """
    Generate a Markdown table from the entities map.
    """
    header = "| Name | Description | S3 URL | Download Link |\n|------|------|-------|------|\n"
    rows = [
        f"| {e['name']} | {e['description']} | `{e['url']}` | [download]({e['url']}) |"
        for e in entities_map
    ]
    return header + "\n".join(rows)


def update_readme(readme_path: Path, entities_map: List[Dict[str, str]]) -> None:
    """
    Update README.md to add or update the CFT table section between the markers.
    """
    if not readme_path.exists():
        raise FileNotFoundError(f"{readme_path} does not exist")

    with open(readme_path, "r") as f:
        readme = f.read()

    if START_MARKER not in readme or END_MARKER not in readme:
        raise ValueError(
            f"README.md does not contain the required markers: {START_MARKER} and {END_MARKER}"
        )

    table = generate_markdown_table(entities_map)
    pattern = re.compile(
        f"{re.escape(START_MARKER)}.*?{re.escape(END_MARKER)}", flags=re.DOTALL
    )
    replacement = f"{START_MARKER}\n\n{table}\n\n{END_MARKER}"

    new_readme = pattern.sub(replacement, readme)

    if readme == new_readme:
        logger.info("README is already up to date.")
        return

    with open(readme_path, "w") as f:
        f.write(new_readme)
        logger.info("README.md updated successfully.")


def main() -> None:
    """
    Main function to update README.md with the latest CFT table.
    """
    parser = argparse.ArgumentParser(
        description="Update README.md with the latest CFT table"
    )
    parser.add_argument(
        "--readme",
        type=Path,
        default=Path("README.md"),
        help="Path to the README.md file to update",
    )
    parser.add_argument(
        "--bucket",
        required=True,
        help="S3 bucket name where templates are stored",
    )
    parser.add_argument(
        "--branch",
        default="main",
        help="Base branch to use for S3 path generation",
    )
    args = parser.parse_args()

    try:
        entities_map = create_entities_map(args.bucket, args.branch)
        if not entities_map:
            logger.info("No templates found to update in README.md.")
            return

        update_readme(args.readme, entities_map)

    except Exception as e:
        logger.error(f"Error updating README.md: {e}")
        raise


if __name__ == "__main__":
    main()
