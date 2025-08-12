import os
from loguru import logger
from dotenv import load_dotenv

from src.logic import generate_profile_groups, run_profile_group


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    logger.add("logfile.log", rotation="2 MB", level="INFO")

    load_dotenv(os.path.abspath(os.path.join(BASE_DIR, ".env")))
    group_of_n = int(os.getenv('PARALLEL_ACCOUNTS'))

    # create group of profiles to run in concurrent way
    profile_groups = generate_profile_groups(group_of_n)

    for profile_group in profile_groups:
        run_profile_group(profile_group)


if __name__ == "__main__":
    main()
