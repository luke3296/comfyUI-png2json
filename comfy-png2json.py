# Extracting the JSON data from the provided text
import json
import os
import argparse
import glob

def load_png_as_text(file_path):
    """
    Loads the contents of a PNG file as text.

    :param file_path: Path to the PNG file.
    :return: A string containing the text data of the PNG file.
    """
    if not os.path.exists(file_path) or not file_path.lower().endswith('.png'):
        return "Invalid file path or the file is not a PNG."

    try:
        with open(file_path, 'rb') as file:
            data = file.read()
            return data.decode('ISO-8859-1')  # Decoding as 'ISO-8859-1' to handle non-text bytes
    except Exception as e:
        return f"An error occurred while reading the file: {e}"

def extract_json_from_text(text, keyword):
    """
    Extracts and parses a JSON object embedded in a text string.
    The JSON object starts after the specified keyword and the first '{' encountered after that keyword.

    :param text: The text containing the JSON object.
    :param keyword: The keyword after which the JSON object starts.
    :return: The parsed JSON object or None if not found.
    """
    # Find the starting index of the JSON object
    start_index = text.find(keyword)
    if start_index == -1:
        return None  # Keyword not found

    # Find the first '{' after the keyword
    start_index = text.find('{', start_index)
    if start_index == -1:
        return None  # '{' not found after the keyword

    # Initialize variables for parsing
    semi_colon_count = 1
    end_index = start_index + 1

    # Loop through the text to find the matching '}'
    while end_index < len(text) and semi_colon_count > 0:
        if text[end_index] == '{':
            semi_colon_count += 1
        elif text[end_index] == '}':
            semi_colon_count -= 1
        end_index += 1

    # Extract the JSON string
    json_str = text[start_index:end_index]

    # Parse the JSON string into an object
    try:
        json_obj = json.loads(json_str)
    except json.JSONDecodeError:
        return None  # Invalid JSON

    return json_obj

def process_file(file_path):
    text_with_json = load_png_as_text(file_path)
    prompt_json = extract_json_from_text(text_with_json, "prompt")
    workflow_json = extract_json_from_text(text_with_json, "workflow")
    return [prompt_json, workflow_json]

def process_directory(directory_path):
    results = {}
    for file in glob.glob(os.path.join(directory_path, '*.png')):
        results[file] = process_file(file)
    return results

def save_as_json(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def main():
    parser = argparse.ArgumentParser(description='Process PNG files to extract JSON data.')
    parser.add_argument('path', help='Path to the PNG file or directory')
    parser.add_argument('-d', '--directory', action='store_true', help='Process all PNG files in the specified directory')
    parser.add_argument('-p', '--print', action='store_true', help='Print the JSON array rather than saving it')
    args = parser.parse_args()

    if args.directory:
        data = process_directory(args.path)
    else:
        data = {args.path: process_file(args.path)}

    if args.print:
        print(json.dumps(data, indent=4))
    else:
        for file_path, json_data in data.items():
            json_file_path = os.path.splitext(file_path)[0] + '.json'
            save_as_json(json_data, json_file_path)

if __name__ == "__main__":
    main()