import json

def load_config(file_path='config.json'):
    """Load configuration from a JSON file."""
    try:
        with open(file_path, 'r') as file:
            config = json.load(file)
        return config
    except FileNotFoundError:
        print("Configuration file not found.")
        return {}
    except json.JSONDecodeError:
        print("Error decoding JSON from the configuration file.")
        return {}
