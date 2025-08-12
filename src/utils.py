import os
import time
import random
import pandas as pd
from loguru import logger

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
csv_file_path = os.path.abspath(os.path.join(BASE_DIR, "..", "profiles.csv"))  # adjust path as needed

# noinspection PyTypeChecker
def wait_until_element_is_visible(profile, by: str, selector: str, timeout: int = 30):
    try:
        return WebDriverWait(profile.driver, timeout).until(EC.visibility_of_element_located((by, selector)))
    except Exception as e:
        trimmed_error_log = trim_stacktrace_error(str(e))
        logger.error(f"Profile_id: {profile.profile_id}. {selector} got error.\n{trimmed_error_log}")
        raise


# noinspection PyTypeChecker
def wait_until_element_is_clickable(profile, by: str, selector: str, timeout: int = 30):
    try:
        return WebDriverWait(profile.driver, timeout).until(EC.element_to_be_clickable((by, selector)))
    except Exception as e:
        trimmed_error_log = trim_stacktrace_error(str(e))
        logger.error(f"Profile_id: {profile.profile_id}. {selector} got error.\n{trimmed_error_log}")
        raise


def trim_stacktrace_error(log: str) -> str:
    """
    Keeps only the first two stacktrace lines that start with '#'.
    """
    lines = log.strip().splitlines()
    trimmed_lines = []
    count = 0

    for line in lines:
        if line.strip().startswith("#"):
            if count < 2:
                trimmed_lines.append(line)
                count += 1
            else:
                break
        else:
            trimmed_lines.append(line)

    return "\n".join(trimmed_lines)


def check_csv_file(file_path: str = csv_file_path) -> bool:
    try:
        # Read the CSV file
        df = pd.read_csv(file_path)

        # Check 1: Exactly 3 columns with specific names
        expected_columns = {'profile_id', 'anty_type'}
        actual_columns = set(df.columns)
        if actual_columns != expected_columns:
            logger.error(f"Expected columns {expected_columns}, but found {actual_columns}")
            return False

        # Check 2: Unique values of anty_type in {"DOLPHIN", "ADSPOWER"}
        anty_types = set(df['anty_type'].str.upper().unique())
        allowed_anty_types = {"DOLPHIN", "ADSPOWER"}
        if not anty_types.issubset(allowed_anty_types):
            logger.error(f"anty_type values {anty_types} are not in {allowed_anty_types}")
            return False

        # Check 3: Unique values of login_with in {"TWITTER", "GOOGLE"}
        login_withs = set(df['login_with'].str.upper().unique())
        allowed_login_withs = {"TWITTER", "GOOGLE"}
        if not login_withs.issubset(allowed_login_withs):
            logger.error(f"login_with values {login_withs} are not in {allowed_login_withs}")
            return False

        logger.info("profiles.csv file checks completed successfully.")
        return True

    except FileNotFoundError:
        logger.error(f"File '{file_path}' not found.")
        return False
    except pd.errors.EmptyDataError:
        logger.error(f"File '{file_path}' is empty.")
        return False
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return False


def send_keys(element, text):
    for letter in text:
        element.send_keys(letter)
        time.sleep(random.randint(1, 20)/1000)


def trim_stacktrace_error(log: str) -> str:
    """
    Keeps only the first two stacktrace lines that start with '#'.
    """
    lines = log.strip().splitlines()
    trimmed_lines = []
    count = 0

    for line in lines:
        if line.strip().startswith("#"):
            if count < 2:
                trimmed_lines.append(line)
                count += 1
            else:
                break
        else:
            trimmed_lines.append(line)

    return "\n".join(trimmed_lines)


def get_full_xpath_element(driver, element):
    full_xpath_element = driver.execute_script(
        """function absoluteXPath(element) {
            var comp, comps = [];
            var parent = null;
            var xpath = '';
            var getPos = function(element) {
                var position = 1, curNode;
                if (element.nodeType == Node.ATTRIBUTE_NODE) {
                    return null;
                }
                for (curNode = element.previousSibling; curNode; curNode = curNode.previousSibling) {
                    if (curNode.nodeName == element.nodeName) {
                        ++position;
                    }
                }
                return position;
            };
            if (element instanceof Document) {
                return '/';
            }
            for (; element && !(element instanceof Document); element = element.nodeType == Node.ATTRIBUTE_NODE ? element.ownerElement : element.parentNode) {
                comp = comps[comps.length] = {};
                comp.name = element.nodeName;
                comp.position = getPos(element);
            }
            for (var i = comps.length - 1; i >= 0; i--) {
                comp = comps[i];
                xpath += '/' + comp.name.toLowerCase() + (comp.position > 1 ? '[' + comp.position + ']' : '');
            }
            return xpath;
        }
        return absoluteXPath(arguments[0]);""",
        element
    )
    return full_xpath_element