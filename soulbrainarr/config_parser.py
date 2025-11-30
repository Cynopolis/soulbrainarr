import os
from dataclasses import dataclass
from typing import Optional

import yaml


def get_config_base_path() -> str:
    """
    Returns the base config path.

    Priority:
    1. CONFIG_PATH environment variable (if set and non-empty)
    2. Current directory 'CONFIG.yaml'
    """
    path_to_return: str = "CONFIG.yaml"
    env_path = os.getenv("CONFIG_PATH", "/config/CONFIG.yaml")
    if env_path and env_path.strip():
        path_to_return = env_path.strip()

    return path_to_return


@dataclass
class SLSKD_CONFIG:
    HOST: str
    API_KEY: str
    SLSKD_DOWNLOADS: str

    SLSKD_KEY: str = "slskd"


@dataclass
class LISTEN_BRAINZ_CONFIG:
    USERNAME: str
    EMAIL: str

    LISTEN_BRAINZ_KEY: str = "listenbrainz"


@dataclass
class BEETS:
    ENABLE_BEETS: bool
    BEETS_IMPORTED: str
    BEETS_CONFIG: str
    BEETS_DATABASE: str

    BEETS_KEY: str = "beets"


@dataclass
class SOULBRAINARR_DATA:
    RUN_INTERVAL_MINUTES: int
    SONG_BATCH_SIZE: int

    SOULBRAINARR_KEY: str = "soulbrainarr"


@dataclass
class CONFIG_DATA:
    SLSKD: SLSKD_CONFIG
    LISTEN_BRAINZ: LISTEN_BRAINZ_CONFIG
    BEETS: BEETS
    SOULBRAINARR: SOULBRAINARR_DATA


def get_config() -> Optional[CONFIG_DATA]:
    try:
        with open(get_config_base_path(), 'r') as file:
            yaml_doc = yaml.safe_load(file)
    except FileNotFoundError:
        return None

    # Parse into dataclasses
    try:
        config = CONFIG_DATA(
            SLSKD=SLSKD_CONFIG(**yaml_doc[SLSKD_CONFIG.SLSKD_KEY]),
            LISTEN_BRAINZ=LISTEN_BRAINZ_CONFIG(
                **yaml_doc[LISTEN_BRAINZ_CONFIG.LISTEN_BRAINZ_KEY]),
            BEETS=BEETS(**yaml_doc[BEETS.BEETS_KEY]),
            SOULBRAINARR=SOULBRAINARR_DATA(
                **yaml_doc[SOULBRAINARR_DATA.SOULBRAINARR_KEY])
        )
    except TypeError as e:
        print("Error Parsing Config", e)
        return None

    return config


print(f"Config Path: {get_config_base_path()}")
CONFIG: Optional[CONFIG_DATA] = get_config()

if __name__ == "__main__":
    print(CONFIG)
