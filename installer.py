# Install Required Modules
from subprocess import run
from sys import version_info
import os

# Get the directory of the currently running script
script_directory = os.path.dirname(os.path.abspath(__file__))
print(f"Installation Directory: {script_directory}")
modules = ["py-cord", "python-dotenv"]


def install_module(module):
    if version_info.major < 3:
        print("We're sorry! Toolbox was built in 3.13.0 and isn't compatible with any python version lower than 3.11.x")
    elif version_info.minor < 11 and version_info.major <= 3:
        print("We're sorry! Toolbox was built in 3.13.0 and isn't compatible with any python version lower than 3.11.x")
    else:
        python_cmd = f"python{version_info.major}.{version_info.minor}"
        pip_command = [python_cmd, "-m", "pip", "install", "-q"]

        try:
            print(f"Installing {module}...")
            run(pip_command + [module], check=True)
            print(f"Successfully installed {module}")
        except Exception as e:
            print(f"Failed to install {module}: {e}")

install_module("urllib3")
import urllib3

def download_file(url, destination):
    http = urllib3.PoolManager()
    try:
        print(f"Downloading {url}...")
        response = http.request("GET", url, preload_content=False)
        if response.status != 200:
            raise Exception(f"Failed to download {url}. HTTP Status: {response.status}")

        with open(destination, "wb") as out_file:
            for chunk in response.stream(1024):
                out_file.write(chunk)
        print(f"File saved to {destination}")
    except Exception as e:
        print(f"Failed to download {url}: {e}")
    finally:
        response.release_conn()

