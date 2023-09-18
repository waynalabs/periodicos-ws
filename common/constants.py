

import pathlib
import os
import sys

# Absolute paths
ROOT_PATH = os.path.abspath(os.path.join(pathlib.Path(__file__).parent.resolve(),  ".."))
root_path = pathlib.Path(ROOT_PATH)

DATA_PATH = os.environ.get("DATA_PATH", str(root_path.joinpath("data").absolute()))
data_path = pathlib.Path(DATA_PATH)
LOG_PATH = os.environ.get("LOG_PATH", str(root_path.joinpath("logs").absolute()))
log_path = pathlib.Path(LOG_PATH)


ABS_PATHS = {
    "root": ROOT_PATH,
    "common": str(root_path.joinpath('common').absolute()),
    "src": str(root_path.joinpath("src").absolute()),
    "data": DATA_PATH,
    "data/csv": str(data_path.joinpath("csv").absolute()),
    "db": str(root_path.joinpath("db").absolute()),
}

# mappings
datafiles_for_data_apps = {
    "El Deber": {
        "normalized": f"{ABS_PATHS['data/csv']}/eldeber.normalized.csv",
        "nername": "eldeber"
    },
    "La Razón": {
        "normalized": f"{ABS_PATHS['data/csv']}/larazon.normalized.csv",
        "nername": "larazon"
    },
    "Los tiempos": {
        "normalized": f"{ABS_PATHS['data/csv']}/lostiempos.normalized.csv",
        "nername": "lostiempos"
    }
}
