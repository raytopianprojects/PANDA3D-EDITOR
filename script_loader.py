# script_loader.py

import importlib.util
import os

def load_script(script_path):
    """
    Dynamically load a Python module from a given file path.
    Returns the loaded module.
    """
    module_name = os.path.splitext(os.path.basename(script_path))[0]
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    else:
        raise ImportError(f"Could not load script: {script_path}")
