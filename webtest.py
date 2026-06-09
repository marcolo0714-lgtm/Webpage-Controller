from playwright.sync_api import sync_playwright
import os
import shlex
import sys
import time
from datetime import datetime, timedelta

url = "https://www.lib.cuhk.edu.hk/en/"
# url = "https://www.hkemobility.gov.hk/tc/route-search/pt"
# url = "http://youtube.com"

screen_width = 1525
screen_height = 825
image_filepath = "screenshots/"
image_capture_count = 0

def time_difference(target_datetime):
    """
    Calculates the difference between target_datetime and the current time,
    and returns a formatted string: 'x hours y minutes z seconds'
    """
    now = datetime.now()
    
    # Get the total difference in seconds
    time_delta = target_datetime - now
    total_seconds = int(time_delta.total_seconds())
    if total_seconds <= 0:
        total_seconds += 86400
    
    # Math to extract hours, minutes, and remaining seconds
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    return f"{hours} hours {minutes} minutes {seconds} seconds"

def get_target_datetime(input_time):
    """Return a datetime for the NEXT occurrence of the provided HH:MM:SS time."""
    try:
        target_time = datetime.strptime(input_time, "%H:%M:%S").time()
    except ValueError:
        raise ValueError("Time must be in HH:MM:SS format.")

    target_datetime = datetime.combine(datetime.now().date(), target_time)
    if target_datetime <= datetime.now():
        target_datetime += timedelta(days=1)
    return target_datetime

def parse_flags(arg_string):
    """Parse optional -time and -wait flags from a command string.
    Returns (args, time_value, wait_flag).
    Raises ValueError if both flags are present.
    """
    tokens = shlex.split(arg_string)
    has_time = "-time" in tokens
    has_wait = "-wait" in tokens
    
    if has_time and has_wait:
        raise ValueError("Cannot use both -time and -wait flags simultaneously.")
    
    if has_time:
        time_index = tokens.index("-time")
        if time_index == len(tokens) - 1:
            return " ".join(tokens[:time_index]), None, False
        time_value = tokens[time_index + 1]
        remaining = " ".join(tokens[:time_index] + tokens[time_index + 2:])
        return remaining.strip(), time_value, False
    
    if has_wait:
        wait_index = tokens.index("-wait")
        remaining = " ".join(tokens[:wait_index] + tokens[wait_index + 1:])
        return remaining.strip(), None, True
    
    return arg_string.strip(), None, False



def wait_until_time(input_time):
    target_datetime = get_target_datetime(input_time)
    print(f"Waiting until {input_time} (in {time_difference(target_datetime)})...")
    while datetime.now() < target_datetime:
        time.sleep(0.01)


# This function is designed to click a button or element specified by the CSS selector.
def click(page, selector, input_time=None, wait_flag=False):
    if not selector:
        print("❌ Error: Missing CSS selector. Format: click <selector>")
        return

    if input_time:
        try:
            wait_until_time(input_time)
        except ValueError as e:
            print(f"❌ Action failed: {e}")
            return
    elif wait_flag:
        print(f"Waiting for selector '{selector}' to appear on screen (timeout: 30 mins)...")
        try:
            page.wait_for_selector(selector, timeout=30 * 60 * 1000)  # 30 minutes in milliseconds
        except Exception:
            print(f"❌ Action failed: Selector '{selector}' did not appear within 30 minutes.")
            return

    print(f"Attempting to click: '{selector}'...")
    try:
        page.locator(selector).click(timeout=5000)  # 5-second limit so it doesn't hang forever
    except Exception:
        print("❌ Action failed: Make sure the CSS selector is correct and visible on screen.")
    else:
        print("✅ Button clicked successfully!")


# This function is designed to fill in text into an input field specified by the CSS selector.
def fill(page, selector, text, input_time=None, wait_flag=False):
    if not selector:
        print("❌ Error: Missing CSS selector. Format: fill <selector>")
        return
    if not text:
        print("❌ Error: Missing text to fill on input field. Please provide the text to be filled.")
        return

    if input_time:
        try:
            wait_until_time(input_time)
        except ValueError as e:
            print(f"❌ Action failed: {e}")
            return
    elif wait_flag:
        print(f"Waiting for selector '{selector}' to appear on screen (timeout: 30 mins)...")
        try:
            page.wait_for_selector(selector, timeout=30 * 60 * 1000)  # 30 minutes in milliseconds
        except Exception:
            print(f"❌ Action failed: Selector '{selector}' did not appear within 30 minutes.")
            return

    print(f"Attempting to fill: '{selector}' with '{text}'...")
    try:
        page.locator(selector).fill(text, timeout=5000)  # 5-second limit so it doesn't hang forever
    except Exception:
        print("❌ Action failed: Make sure the CSS selector is correct and visible on screen.")
    else:
        print("✅ Input field filled successfully!")

# This function is designed to retrieve text from an HTML element specified by the CSS selector.
def text(page, selector, input_time=None, wait_flag=False):
    if not selector:
        print("❌ Error: Missing CSS selector. Format: text <selector>")
        return None

    if input_time:
        try:
            wait_until_time(input_time)
        except ValueError as e:
            print(f"❌ Action failed: {e}")
            return None
    elif wait_flag:
        print(f"Waiting for selector '{selector}' to appear on screen (timeout: 30 mins)...")
        try:
            page.wait_for_selector(selector, timeout=30 * 60 * 1000)
        except Exception:
            print(f"❌ Action failed: Selector '{selector}' did not appear within 30 minutes.")
            return None

    try:
        content = page.locator(selector).text_content(timeout=5000)
        text_value = content if content is not None else ""
        print(f"✅ Text content retrieved': {text_value}")
        return text_value
    except Exception:
        print("❌ Action failed: Make sure the CSS selector is correct and visible on screen.")
        return None

# This function is designed to retrieve an image from an HTML element specified by the CSS selector.
def image(page, selector, input_time=None, wait_flag=False):
    global image_capture_count

    if not selector:
        print("❌ Error: Missing CSS selector. Format: image <selector>")
        return None

    if input_time:
        try:
            wait_until_time(input_time)
        except ValueError as e:
            print(f"❌ Action failed: {e}")
            return None
    elif wait_flag:
        print(f"Waiting for selector '{selector}' to appear on screen (timeout: 30 mins)...")
        try:
            page.wait_for_selector(selector, timeout=30 * 60 * 1000)
        except Exception:
            print(f"❌ Action failed: Selector '{selector}' did not appear within 30 minutes.")
            return None

    os.makedirs(image_filepath, exist_ok=True)
    image_capture_count += 1
    filename = f"capture{image_capture_count}.png"
    path = os.path.join(image_filepath, filename)

    try:
        page.locator(selector).screenshot(path=path)
        print(f"✅ Saved image for '{selector}' to {path}")
        return path
    except Exception:
        print("❌ Action failed: Make sure the CSS selector is correct and visible on screen.")
        return None


def interactive_browser():
    print("\nLaunching Chromium... Please wait.")

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir="./user_data_dir",  # Change this to a valid directory on your system
            headless=False,  # Set to False so you can see the screen!
            viewport={"width": 1280, "height": 720}
        )

        page = browser.new_page()

        try:
            page.goto(url)
            print(f"✅ Successfully loaded: {url}\n")
        except Exception as e:
            print(f"❌ Error loading page: {e}")
            browser.close()
            return

        # 1. Print user instructions
        print("=" * 60)
        print("COMMAND FORMATS:")
        print("  To click:         click <selector> [-time HH:MM:SS | -wait]")
        print("  To fill:          fill <selector> <text> [-time HH:MM:SS | -wait]")
        print("  To get text:      text <selector> [-time HH:MM:SS | -wait]")
        print("  To get image:     image <selector> [-time HH:MM:SS | -wait]")
        print("  To exit:          exit")
        print("=" * 60)

        # 2. Start the interactive loop
        while True:
            try:
                user_input = input("Enter command: ").strip()
                if not user_input:
                    continue

                if user_input.lower().strip() == "exit":
                    print("Closing browser and exiting.")
                    break

                # Parse the action
                action = user_input.split(" ", 1)[0].lower()

                ###################################################
                if action == "click":
                    command_body = user_input[len("click"):].strip()
                    try:
                        selector, input_time, wait_flag = parse_flags(command_body)
                        click(page, selector, input_time, wait_flag)
                    except ValueError as e:
                        print(f"❌ Error: {e}")

                elif action == "fill":
                    command_body = user_input[len("fill"):].strip()
                    try:
                        command_body, input_time, wait_flag = parse_flags(command_body)
                        tokens = shlex.split(command_body)
                        if len(tokens) < 2:
                            print("❌ Error: fill requires a selector and text. Use quotes if needed.")
                        else:
                            selector = tokens[0]
                            text_value = " ".join(tokens[1:])
                            fill(page, selector, text_value, input_time, wait_flag)
                    except ValueError as e:
                        print(f"❌ Error: {e}")

                elif action == "text":
                    command_body = user_input[len("text"):].strip()
                    try:
                        selector, input_time, wait_flag = parse_flags(command_body)
                        text(page, selector, input_time, wait_flag)
                    except ValueError as e:
                        print(f"❌ Error: {e}")

                elif action == "image":
                    command_body = user_input[len("image"):].strip()
                    try:
                        selector, input_time, wait_flag = parse_flags(command_body)
                        image(page, selector, input_time, wait_flag)
                    except ValueError as e:
                        print(f"❌ Error: {e}")

                elif action == "eval":
                    selector = user_input[len(action):].strip()
                    page.locator(selector).click()  # 5-second limit so it doesn't hang forever

                else:
                    print(f"❌ Unknown action '{action}'.")
                ###################################################

            except Exception as e:
                print(f"❌ Action failed: {e.value if hasattr(e, 'value') else e}")


if __name__ == "__main__":
    interactive_browser()