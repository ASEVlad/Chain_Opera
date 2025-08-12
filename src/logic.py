import os
import threading
from typing import List
from loguru import logger

import pandas as pd

from src.main_functions import run_profile_farm, ChainOperaProfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
csv_file_path = os.path.join(BASE_DIR, "..", "profiles.csv")


def generate_profile_groups(group_size=5) -> List[List[ChainOperaProfile]]:
    # Read the CSV file
    df = pd.read_csv(csv_file_path)

    # Shuffle the DataFrame rows
    df = df.sample(frac=1).reset_index(drop=True)

    # Generate random group sizes
    group_sizes = []
    remaining = len(df)

    while remaining > 0:
        group_size = min(group_size, remaining)  # Ensure it doesn't exceed available rows
        group_sizes.append(group_size)
        remaining -= group_size

    # Split into groups
    groups = list()
    start = 0
    for size in group_sizes:
        group = []
        for _, profile_info in df.iloc[start:start + size].iterrows():
            group.append(ChainOperaProfile(
                profile_id=profile_info["profile_id"],
                anty_type=profile_info["anty_type"],
                eth_wallet=profile_info["eth_wallet"]
            ))
        groups.append(group)
        start += size

    return groups


def run_profile_group(profile_group: List):
    threads = []
    for i, profile in enumerate(profile_group):
        t = threading.Thread(
            target=run_profile_farm,
            args=(profile, i)
        )
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    logger.info("GROUP FINISHED. All profiles completed.")