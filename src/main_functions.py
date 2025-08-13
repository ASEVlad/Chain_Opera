import os
import time
import random
from loguru import logger
from dotenv import load_dotenv

from src.llm_helper import generate_test_prompt
from src.profile_manager import ProfileManager
from src.utils import wait_until_element_is_visible, trim_stacktrace_error, send_keys, get_full_xpath_element


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.abspath(os.path.join(BASE_DIR, "..", ".env")))
PASSWORD = os.getenv('PASSWORD')

class ChainOperaProfile(ProfileManager):
    def __init__(self, profile_id: str, anty_type: str, eth_wallet: 'str'):
        super().__init__(profile_id, anty_type)
        self.eth_wallet = eth_wallet

def open_okx_wallet(web_profile: ChainOperaProfile):
    try:
        web_profile.driver.switch_to.new_window('tab')
        web_profile.driver.switch_to.window(web_profile.driver.window_handles[-1])

        web_profile.driver.get(f"chrome-extension://mcohilncbfahbmgdjkbpemcciiolgcge/popup.html#/unlock")

        pass_input_element = wait_until_element_is_visible(web_profile, "xpath", "//input[@data-testid='okd-input']")
        pass_input_element.send_keys(PASSWORD)

        pass_input_element = wait_until_element_is_visible(web_profile, "xpath", "//button[@data-testid='okd-button']")
        pass_input_element.click()

        okx_wallet_handle = web_profile.driver.current_window_handle
        return okx_wallet_handle

    except Exception as e:
        trimmed_error_log = trim_stacktrace_error(str(e))
        logger.error(f"Profile_id: {web_profile.profile_id}. {trimmed_error_log}")
        raise e

def turn_to_proper_wallet(web_profile: ChainOperaProfile, okx_handle: str):
    try:
        web_profile.driver.switch_to.window(okx_handle)
        curr_wallet_element = wait_until_element_is_visible(web_profile, "xpath", "//div[@data-testid='home-page-wallet-account-name']")
        if curr_wallet_element.text[:6].lower() == web_profile.eth_wallet[:6].lower():
            logger.info(f"Profile_id: {web_profile.profile_id}. No need to change wallet.")
        else:
            curr_wallet_element.click()

            wait_until_element_is_visible(web_profile, "xpath", "//div[@data-testid='wallet-management-page-wallet-account-detail']")
            available_wallets_elements = web_profile.driver.find_elements("xpath", "//div[@data-testid='wallet-management-page-wallet-account-detail']")
            available_wallets_elements[0].click()

            logger.info(f"Profile_id: {web_profile.profile_id}. Successfully changed the wallet.")

    except Exception as e:
        trimmed_error_log = trim_stacktrace_error(str(e))
        logger.error(f"Profile_id: {web_profile.profile_id}. {trimmed_error_log}")


def close_related_tabs(web_profile: ChainOperaProfile):
    try:
        original_window = web_profile.driver.current_window_handle
        okx_handles = []

        # Collect all handles for tabs with "OKX" in title
        for handle in web_profile.driver.window_handles:
            web_profile.driver.switch_to.window(handle)
            if "OKX" in web_profile.driver.title.upper() or "ChainOpera" in web_profile.driver.title.upper():
                okx_handles.append(handle)

        # Close each matching tab
        for handle in okx_handles:
            web_profile.driver.switch_to.window(handle)
            web_profile.driver.close()

        # Switch back to the first remaining tab
        if web_profile.driver.window_handles:
            web_profile.driver.switch_to.window(web_profile.driver.window_handles[0])
        else:
            print("All tabs were closed — no remaining window to switch to.")

    except Exception as e:
        trimmed_error_log = trim_stacktrace_error(str(e))
        logger.error(f"Profile_id: {web_profile.profile_id}. {trimmed_error_log}")


def run_profile_farm(web_profile: ProfileManager, profile_num: int):
    try:
        time.sleep(profile_num)
        website_handle, okx_handle = start_profile(web_profile)
        start_points = get_earned_points(web_profile)

        # farm daily points
        farm_daily_points(web_profile, website_handle, okx_handle)

        prompts_to_farm = random.randint(6, 8)

        for i in range(prompts_to_farm):
            farm_prompt_point(web_profile)

        end_points = get_earned_points(web_profile)

        logger.info(f"Profile_id: {web_profile.profile_id}. SUCCESSFULLY FARMED. Earned {end_points - start_points}. Total points: {end_points}")
        finalize_profile(web_profile)

    except Exception as e:
        handle_error(web_profile, e)

def start_profile(web_profile):
    # open profile
    web_profile.open_profile()
    time.sleep(1)
    close_related_tabs(web_profile)
    time.sleep(1)
    web_profile.driver.switch_to.new_window('tab')
    time.sleep(1)
    web_profile.driver.get("https://chat.chainopera.ai/invite?code=RXSN3VOL")
    wait_until_element_is_visible(web_profile, "xpath", "//body")

    website_handle = web_profile.driver.current_window_handle
    okx_handle = open_okx_wallet(web_profile)
    turn_to_proper_wallet(web_profile, okx_handle)
    web_profile.driver.switch_to.window(website_handle)

    sign_in(web_profile, website_handle, okx_handle)
    login_elements = web_profile.driver.find_elements("xpath", "//button[text()='Login']")
    if len(login_elements) != 0:
        sign_in(web_profile, website_handle, okx_handle)

    return website_handle, okx_handle

def finalize_profile(web_profile):
    close_related_tabs(web_profile)
    web_profile.close_profile()

def handle_error(web_profile, error):
    trimmed_error_log = trim_stacktrace_error(str(error))
    logger.error(f"Profile_id: {web_profile.profile_id}. {trimmed_error_log}")

    try:
        finalize_profile(web_profile)
    except Exception as e:
        trimmed_error_log = trim_stacktrace_error(str(e))
        logger.error(f"Profile_id: {web_profile.profile_id}. {trimmed_error_log}")

def sign_in(web_profile: ProfileManager, website_handle: str, okx_handle: str):
    try:
        time.sleep(3)
        login_elements = web_profile.driver.find_elements("xpath", "//button[text()='Login']")

        if len(login_elements) != 0:
            #first confirm
            for _ in range(2):
                time.sleep(2)
                web_profile.driver.switch_to.window(website_handle)
                time.sleep(2)
                wait_until_element_is_visible(web_profile, "xpath", "//span[text()='OKX Wallet']").click()
                time.sleep(2)
                web_profile.driver.switch_to.window(okx_handle)
                time.sleep(2)

                wait_until_element_is_visible(web_profile, "xpath", "//div[text()='Cancel' or text()='Скасувати']")

                connect_button_elements = web_profile.driver.find_elements("xpath", "//div[text()='Connect' or text()='Підключити']")
                if len(connect_button_elements) != 0:
                    connect_button_elements[0].click()

                confirm_button_elements = web_profile.driver.find_elements("xpath", "//div[text()='Confirm' or text()='Підтвердити']")
                if len(confirm_button_elements) != 0:
                    confirm_button_elements[0].click()
                    break

                time.sleep(2)


            # Referral code
            time.sleep(2)
            web_profile.driver.switch_to.window(website_handle)
            web_profile.driver.get("https://chat.chainopera.ai/invite?code=RXSN3VOL")

            wait_until_element_is_visible(web_profile, "xpath", "//a[@href='https://x.com/ChainOpera_AI']")
            time.sleep(1)
            confirm_referral_elements = web_profile.driver.find_elements("xpath", "//button[text()='Confirm']")

            if len(confirm_referral_elements) != 0:
                confirm_referral_elements[0].click()
                wait_until_element_is_visible(web_profile, "xpath", "//a[@href='https://x.com/ChainOpera_AI']")
                logger.info(f"Profile_id: {web_profile.profile_id}. Referral code has been entered successfully")

            logger.info(f"Profile_id: {web_profile.profile_id}. Sign in has been successfully performed")

    except Exception as e:
        trimmed_error_log = trim_stacktrace_error(str(e))
        logger.error(f"Profile_id: {web_profile.profile_id}. {trimmed_error_log}")
        raise

def open_side_bar(web_profile: ProfileManager):
    try:
        twitter_element = wait_until_element_is_visible(web_profile, "xpath", "//a[@href='https://x.com/ChainOpera_AI']")
        side_bar_element = web_profile.driver.find_elements("xpath", "//span[text()='Total Points Earned']")
        if len(side_bar_element) == 0:
            twitter_xpath = get_full_xpath_element(web_profile.driver, twitter_element)
            wallet_xpath = twitter_xpath[:-4] + "button"
            wait_until_element_is_visible(web_profile, "xpath", wallet_xpath).click()

        wait_until_element_is_visible(web_profile, "xpath", "//span[text()='Total Points Earned']")

    except Exception as e:
        trimmed_error_log = trim_stacktrace_error(str(e))
        logger.error(f"Profile_id: {web_profile.profile_id}. {trimmed_error_log}")
        raise

def farm_daily_points(web_profile: ProfileManager, website_handle: str, okx_handle: str):
    try:
        open_side_bar(web_profile)

        time.sleep(3)
        daily_points_elements = web_profile.driver.find_elements("xpath", "//div[@data-signed='false']")
        daily_points_elements[0].click()
        time.sleep(2)

        cooldown_elements = web_profile.driver.find_elements("xpath", "//div[text()='Thank you! You have already checked-in today!']")
        if len(cooldown_elements) == 0:
            wait_until_element_is_visible(web_profile, "xpath", "//button[text()='Check-In']").click()

            time.sleep(1)
            web_profile.driver.switch_to.window(okx_handle)
            time.sleep(1)
            wait_until_element_is_visible(web_profile, "xpath", "//div[text()='Confirm' or text()='Підтвердити']").click()
            time.sleep(2)

            warning_message = web_profile.driver.find_elements(
                "xpath",
                "//div[text()='Continue on this network' or text()='Продовжити в цій мережі']"
            )
            if len(warning_message) == 1:
                warning_message[0].click()

            time.sleep(1)
            web_profile.driver.switch_to.window(website_handle)
            time.sleep(1)

            wait_until_element_is_visible(web_profile, "xpath", "//button[text()='Got it!']").click()

            logger.info(f"Profile_id: {web_profile.profile_id}. Daily points are clicked")
        else:
            logger.info(f"Profile_id: {web_profile.profile_id}. Daily points have been earned earlier. Can not farm it today.")


    except Exception as e:
        trimmed_error_log = trim_stacktrace_error(str(e))
        logger.error(f"Profile_id: {web_profile.profile_id}. {trimmed_error_log}")

def farm_prompt_point(web_profile):
    # open main page
    web_profile.driver.get("https://chat.chainopera.ai/")
    time.sleep(10)

    try:
        # generate and write a prompt
        prompt_area_element = wait_until_element_is_visible(web_profile, "xpath",
                                                            "//textarea[@placeholder='Ask AI anything...']")
        prompt_to_test = generate_test_prompt()
        send_keys(prompt_area_element, prompt_to_test)

        # send prompt to get responses
        prompt_area_xpath = get_full_xpath_element(web_profile.driver, prompt_area_element)
        prompt_area_parent_element = wait_until_element_is_visible(web_profile, "xpath", prompt_area_xpath[:-9])
        send_button_element = prompt_area_parent_element.find_elements("xpath", ".//button")[-1]
        send_button_element.click()

        # wait a bit
        time_to_sleep = 50 + random.randint(1, 20)
        time.sleep(time_to_sleep)

        logger.info(f"Profile_id: {web_profile.profile_id}. Prompt is sent.")
        return True

    except Exception as e:
        trimmed_error_log = trim_stacktrace_error(str(e))
        logger.error(f"Profile_id: {web_profile.profile_id}. {trimmed_error_log}")
        return False

def get_earned_points(web_profile: ProfileManager):
    try:
        web_profile.driver.get("https://chat.chainopera.ai/")
        open_side_bar(web_profile)

        points_text_element = wait_until_element_is_visible(
            web_profile,
            "xpath",
            "//span[text()='Total Points Earned']"
        )
        time.sleep(5)

        points_text_xpath = get_full_xpath_element(web_profile.driver, points_text_element)
        points_info_xpath = points_text_xpath[:-8] + "[3]"
        points_info_element = wait_until_element_is_visible(web_profile, "xpath", points_info_xpath)
        return int(points_info_element.find_element("xpath", ".//span").text)

    except Exception as e:
        trimmed_error_log = trim_stacktrace_error(str(e))
        logger.error(f"Profile_id: {web_profile.profile_id}. {trimmed_error_log}")
        return 0
