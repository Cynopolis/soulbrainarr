import sqlite3
from pathlib import Path
from soulbrainarr.config_parser import get_config, CONFIG_DATA


MINIMAL_BEETS_CONFIG = """\
directory: {music_path}
library: {library_path}

import:
  move: yes
  timid: no

paths:
  default: $artist/$album/$track - $title
"""


def init_beets() -> None:
    """
    Ensures that the Beets config.yaml and library.db exist.
    - Creates parent directories if missing.
    - Writes a minimal but valid config.yaml if not present.
    - Creates an empty library.db with the schema Beets expects.
      (Beets will populate tables automatically on first import.)
    """

    config: CONFIG_DATA = get_config()

    config_file = Path(config.BEETS.BEETS_CONFIG).expanduser()
    db_file = Path(config.BEETS.BEETS_DATABASE).expanduser()
    music_folder_path = Path(config.SLSKD.SLSKD_DOWNLOADS).expanduser()

    # --- Ensure directory structure exists ---
    config_file.parent.mkdir(parents=True, exist_ok=True)
    db_file.parent.mkdir(parents=True, exist_ok=True)

    # --- 1. Create config.yaml if missing ---
    if not config_file.exists():
        minimal_cfg = MINIMAL_BEETS_CONFIG.format(
            library_path=str(db_file),
            music_path=str(music_folder_path)
        )
        config_file.write_text(minimal_cfg, encoding="utf-8")
        print(f"[beets] Created config file: {config_file}")

    # --- 2. Create library.db if missing ---
    if not db_file.exists():
        # Create empty SQLite DB — Beets creates tables automatically
        conn = sqlite3.connect(db_file)
        conn.close()
        print(f"[beets] Created empty database file: {db_file}")
