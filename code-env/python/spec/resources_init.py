######################## Base imports #################################
import os

import nltk

from dataiku.code_env_resources import clear_all_env_vars
from dataiku.code_env_resources import set_env_path

######################## Download NLTK data #################################
# Clear all environment variables defined by a previously run script
clear_all_env_vars()

# Download punkt resources to the NLTK_HOME cache directory
set_env_path("NLTK_HOME", "nltk_data")
cache_folder = os.getenv("NLTK_HOME")
nltk.download('punkt', download_dir=cache_folder)
