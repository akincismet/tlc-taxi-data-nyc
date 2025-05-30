# single day
# ingest_yellow_tripdata(year=2023, month=1, day=15, dest="./data")

# whole month
# ingest_yellow_tripdata(year=2023, month=1, dest="./data")

# whole year
# ingest_yellow_tripdata(year=2023, dest="./data")
import logging, requests
from pathlib import Path
from typing import Optional, Union, List

OWNER, REPO, BRANCH = "erkansirin78", "datasets", "master"
API_BASE = f"https://api.github.com/repos/{OWNER}/{REPO}/contents"
RAW_BASE = f"https://raw.githubusercontent.com/{OWNER}/{REPO}/{BRANCH}"
SUBDIR = "yellow_tripdata_partitioned_by_day"

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("ingest")


def _list_files(prefix: str) -> List[str]:
    url = f"{API_BASE}/{prefix}?ref={BRANCH}"
    r = requests.get(url, timeout=30)
    if r.status_code == 404:
        raise FileNotFoundError(f"partition “{prefix}” not found in repo")
    r.raise_for_status()
    files = []
    for entry in r.json():
        if entry["type"] == "file" and entry["name"].endswith(".parquet"):
            files.append(entry["path"])
        elif entry["type"] == "dir":
            files.extend(_list_files(entry["path"]))
    return files


def ingest_yellow_tripdata(*,
                           year: Union[int, str],
                           month: Optional[Union[int, str]] = None,
                           day: Optional[Union[int, str]] = None,
                           dest: Union[str, Path] = "./ingested") -> Path:
    """Download parquet partitions for the given year / month / day."""
    if day is not None and month is None:
        raise ValueError("When `day` is given, `month` is required.")

    # build repo prefix WITHOUT zero-padding
    parts = [SUBDIR, f"year={int(year)}"]
    if month is not None:
        parts.append(f"month={int(month)}")
    if day is not None:
        parts.append(f"day={int(day)}")
    prefix = "/".join(parts)

    log.info("Listing files at %s", prefix)
    repo_files = _list_files(prefix)

    dest_root = Path(dest).expanduser().resolve()
    for repo_path in repo_files:
        rel_path = Path(repo_path).relative_to(SUBDIR)
        local_path = dest_root / rel_path
        local_path.parent.mkdir(parents=True, exist_ok=True)

        raw_url = f"{RAW_BASE}/{repo_path}"
        log.info("↓ %s", local_path)
        with requests.get(raw_url, stream=True, timeout=60) as r:
            r.raise_for_status()
            with local_path.open("wb") as fh:
                for chunk in r.iter_content(1 << 20):
                    fh.write(chunk)
    log.info("✓ %d parquet files written to %s", len(repo_files), dest_root)
    return dest_root