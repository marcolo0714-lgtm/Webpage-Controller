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
wait_flag_timeout = 30  # in minutes

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

def parse_flags(command_body):
    """Parse selector, required flags (-text or -key), and optional flags (-time or -wait) from the command body.
    Returns (selector -> str | None, required_text -> str | None, time_value -> str | None, wait_flag -> bool).
    Raises ValueError if more than 1 flag of the same kind (required or optional) are present.
    """
    tokens = list(shlex.split(command_body))

    # Parsing optional flags (-time or -wait)
    has_time = "-time" in tokens
    wait_flag = "-wait" in tokens
    if has_time and wait_flag:
        raise ValueError("Cannot use both -time and -wait flags simultaneously.")
    try:
        time_value = tokens[tokens.index("-time") + 1] if has_time else None
    except:
        raise ValueError("-time flag present, but contain no arguments.")
    
    # Parsing required flags (-text or -key)
    has_text = "-text" in tokens
    has_key = "-key" in tokens

    if has_text and has_key:
        raise ValueError("Cannot use both -text and -key flags simultaneously.")
    if has_time:
        final_flag_pos = tokens.index("-time")
    elif wait_flag:
        final_flag_pos = tokens.index("-wait")
    else:
        final_flag_pos = len(tokens)

    if has_text:
        req_flag_pos = tokens.index("-text")
    elif has_key:
        req_flag_pos = tokens.index("-key")
    else:
        req_flag_pos = -1
    if req_flag_pos > final_flag_pos:
        raise ValueError(f"Required flags ({"-text" if has_text else "-key"}) appears before optional flags ({"-time" if has_time else "-wait"}).")
    
    if has_text or has_key:
        required_text = ' '.join(tokens[req_flag_pos + 1: final_flag_pos])
        if required_text == "":
            raise ValueError("-text flag present, but contain no arguments.")
    else:
        required_text = None
    
    # Parsing selector
    if req_flag_pos == -1:
        selector = ' '.join(tokens[0 : final_flag_pos])
    else:
        selector = ' '.join(tokens[0 : min(req_flag_pos, final_flag_pos)])

    return selector, required_text, time_value, wait_flag


def wait_until_time_or_appear(page, selector, input_time, wait_flag):
    if input_time:
        try:
            target_datetime = get_target_datetime(input_time)
            print(f"Waiting until {input_time} (in {time_difference(target_datetime)})...")
            while datetime.now() < target_datetime:
                time.sleep(0.01)
        except ValueError as e:
            print(f"❌ Action failed: {e}")
            return
    elif wait_flag:
        print(f"Waiting for selector '{selector}' to appear on screen (timeout: {wait_flag_timeout} mins)...")
        try:
            page.wait_for_selector(selector, timeout=wait_flag_timeout * 60 * 1000)  # in milliseconds
        except Exception:
            print(f"❌ Action failed: Selector '{selector}' did not appear within {wait_flag_timeout} minutes.")
            return
        
# This function is designed to click a button or element specified by the CSS selector.
def click(page, selector, input_time=None, wait_flag=False):
    if not selector:
        print("❌ Error: Missing CSS selector. Format: click <selector>")
        return

    wait_until_time_or_appear(page, selector, input_time, wait_flag)

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

    wait_until_time_or_appear(page, selector, input_time, wait_flag)

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

    wait_until_time_or_appear(page, selector, input_time, wait_flag)

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

    wait_until_time_or_appear(page, selector, input_time, wait_flag)

    os.makedirs(image_filepath, exist_ok=True)
    image_capture_count += 1
    filename = f"capture{image_capture_count}.png"
    path = os.path.join(image_filepath, filename)

    try:
        page.locator(selector).screenshot(path=path)
        print(f"✅ Saved image for '{selector}' to {path}")
        return path
    except Exception:
        print("❌ Action failed: Make sure the CSS selector is correct and visible on screen, and the screenshot path exists.")
        return None


# This function is designed to press a keyboard key on a selected element.
def press(page, selector, key, input_time=None, wait_flag=False):
    if not selector:
        print("❌ Error: Missing CSS selector. Format: press <selector> <key>")
        return
    if not key:
        print("❌ Error: Missing key string. Format: press <selector> <key>")
        return

    wait_until_time_or_appear(page, selector, input_time, wait_flag)

    print(f"Attempting to press '{key}' on '{selector}'...")
    try:
        page.locator(selector).press(key, timeout=5000)
    except Exception:
        print("❌ Action failed: Make sure the CSS selector is correct and visible on screen.")
    else:
        print("✅ Key press completed successfully!")


# This function is designed to run a custom batch of browser actions.
def batch(page):
    # Customize this function to perform a series of browser actions.
    # Example:
    #     click(page, "button.submit")
    #     fill(page, "input[name='q']", "Hello world")
    #     press(page, "input[name='q']", "Enter")
    #     text(page, ".result")
    #     image(page, ".screenshot-target")
    # You can also add loops, sleeps, or any other control flow here.
    pass


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
        print("  To fill:          fill <selector> -text <text> [-time HH:MM:SS | -wait]")
        print("  To press a key:   press <selector> -key <key> [-time HH:MM:SS | -wait]")
        print("  To get text:      text <selector> [-time HH:MM:SS | -wait]")
        print("  To get image:     image <selector> [-time HH:MM:SS | -wait]")
        print("  To run batch:     batch")
        print("  To exit:          exit")
        print("=" * 60)

        # 2. Start the interactive loop
        while True:
            try:
                user_input = input("Enter command: ").strip()
                if not user_input:
                    continue

                # 3. Handle standalone commands
                action = user_input.split(" ", 1)[0].lower().strip()
                if action == "exit":
                    print("Closing browser and exiting.")
                    break
                elif action == "batch":
                    batch(page)
                    continue

                # 4. Parse the flags to handle commands supporting optional or required flags
                command_body = user_input[len(action):].strip()
                selector, required_text, input_time, wait_flag = parse_flags(command_body)
                if selector == "":
                    raise ValueError("Selector is required, but not present.")

                ###################################################
                if action == "click":
                    if required_text != None:
                        raise ValueError("Unexpected extra flags (-text or -key).")
                    click(page, selector, input_time, wait_flag)

                elif action == "fill":
                    if required_text == None:
                        raise ValueError("Expected flags (-text) not present.")
                    fill(page, selector, required_text, input_time, wait_flag)

                elif action == "press":
                    if required_text == None:
                        raise ValueError("Expected flags (-text) not present.")
                    press(page, selector, required_text, input_time, wait_flag)

                elif action == "text":
                    if required_text != None:
                        raise ValueError("Unexpected extra flags (-text or -key).")
                    text(page, selector, input_time, wait_flag)

                elif action == "image":
                    if required_text != None:
                        raise ValueError("Unexpected extra flags (-text or -key).")
                    text(page, selector, input_time, wait_flag)

                else:
                    print(f"❌ Unknown action '{action}'.")
                ###################################################

            except Exception as e:
                print(f"❌ Action failed: {e.value if hasattr(e, 'value') else e}")


if __name__ == "__main__":
    interactive_browser()