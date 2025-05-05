import json
import os
import argparse
import re

INPUT_FILE = "household_output.json"
OUTPUT_DIR = "formatted_manuals"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def format_manual(manual):
    lines = []
    lines.append(f" Title: {manual.get('Title', 'N/A')}")
    lines.append(f" URL: {manual.get('Url', 'N/A')}")
    
    toolbox = manual.get("Toolbox", [])
    if toolbox:
        lines.append("\n Required Tools:")
        for tool in toolbox:
            # Handle "Name" field properly
            tool_name = tool.get("Name", "")
            if isinstance(tool_name, list):
                tool_name = ", ".join(tool_name)  # Join list items if it's a list
            tool_url = tool.get("Url", "")
            lines.append(f"- {tool_name} ({tool_url})")
    
    lines.append("\n Steps:")
    steps = manual.get("Steps", [])
    for step in steps:
        step_order = step.get("Order", "N/A")
        lines.append(f"\nStep {step_order}:")
        step_lines = step.get("Lines", [])
        for line in step_lines:
            lines.append(f"- {line.get('Text', '').strip()}")

    return "\n".join(lines)

def get_next_manual_number(output_dir):
    """Determine the next manual number based on existing files in the directory."""
    existing_files = os.listdir(output_dir)
    manual_numbers = []

    # Extract numbers from filenames like "manual_1.txt"
    for filename in existing_files:
        match = re.match(r"manual_(\d+)\.txt", filename)
        if match:
            manual_numbers.append(int(match.group(1)))

    # Return the next available number
    return max(manual_numbers, default=0) + 1

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Format and output manuals.")
    parser.add_argument(
        "-n", "--num_manuals", type=int, default=None,
        help="Number of manuals to output (default: all)"
    )
    args = parser.parse_args()

    # Read the input file
    try:
        with open(INPUT_FILE, "r") as f:
            data = json.load(f)  # Load the entire JSON file as a single object
            manuals = data.get("manuals", [])  # Extract the "manuals" array
    except FileNotFoundError:
        print(f"Error: The file '{INPUT_FILE}' does not exist.")
        return
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse JSON in the input file. {e}")
        return

    # Check if the file contains manuals
    if not manuals:
        print("Error: The input file contains no manuals.")
        return

    # Determine how many manuals to process
    num_manuals = args.num_manuals if args.num_manuals else len(manuals)
    num_manuals = min(num_manuals, len(manuals))  # Ensure it doesn't exceed available manuals

    # Get the starting manual number
    next_manual_number = get_next_manual_number(OUTPUT_DIR)

    for idx, manual in enumerate(manuals[:num_manuals]):
        # Skip invalid entries
        if not isinstance(manual, dict):
            print(f"Skipping invalid manual at index {idx}")
            continue

        formatted_text = format_manual(manual)
        print(f"\n===== Manual {next_manual_number} =====\n")
        print(formatted_text)
        
        # Save to .txt file
        filename = os.path.join(OUTPUT_DIR, f"manual_{next_manual_number}.txt")
        with open(filename, "w") as out_file:
            out_file.write(formatted_text)

        next_manual_number += 1  # Increment the manual number for the next file

if __name__ == "__main__":
    main()
