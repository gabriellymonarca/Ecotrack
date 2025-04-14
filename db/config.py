import yaml
import os 

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.yaml")

def load_config():
    with open(CONFIG_PATH, "r") as file:
        return yaml.safe_load(file)
    
CONFIG = load_config()