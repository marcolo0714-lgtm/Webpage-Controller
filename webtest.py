from playwright.sync_api import sync_playwright
import os
import sys
from datetime import datetime, timedelta

url = "https://www.lib.cuhk.edu.hk/en/"
# url = "https://www.hkemobility.gov.hk/tc/route-search/pt"
# url = "http://youtube.com"

screen_width = 1525  # 1525
screen_height = 500  # 825
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
    Raises ValueError if more than 1 kind of required flags are present.
    """
    tokens = list(command_body.split())

    # Parsing optional flags (-time or -wait)
    has_time = "-time" in tokens
    wait_flag = "-wait" in tokens
    try:
        time_value = tokens[tokens.index("-time") + 1] if has_time else None
    except (IndexError, ValueError):
        raise ValueError("-time flag present, but contain no arguments.")
    
    # Parsing required flags (-text or -key)
    has_text = "-text" in tokens
    has_key = "-key" in tokens

    if has_text and has_key:
        raise ValueError("Cannot use both -text and -key flags simultaneously.")

    if has_time and wait_flag:
        final_flag_pos = min(tokens.index("-time"), tokens.index("-wait"))
    elif has_time:
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
    """Wait until a target time and/or until selector appears.
    Returns True when wait completed normally, False when user cancelled.
    """
    # Wait for a specific time (polling so user can Ctrl+C to cancel)
    if input_time:
        try:
            target_datetime = get_target_datetime(input_time)
        except ValueError as e:
            print(f"❌ Action failed: {e}")
            return True  # treat invalid time as non-cancellable failure so caller prints the error

        print(f"🕒 Waiting until {input_time} (in {time_difference(target_datetime)})... Press Ctrl+C to cancel.")
        try:
            while datetime.now() < target_datetime:
                page.wait_for_timeout(10)
        except KeyboardInterrupt:
            print("⚠️ Wait cancelled by user.")
            return False

    if wait_flag:
        timeout_ms = wait_flag_timeout * 60 * 1000
        print(f"🕒 Waiting for selector '{selector}' to appear on screen (timeout: {wait_flag_timeout} mins). Press Ctrl+C to cancel.")
        try:
            page.locator(selector).wait_for(state="attached", timeout=timeout_ms)
            return True
        except KeyboardInterrupt:
            print("⚠️ Wait cancelled by user.")
            return False
        except Exception:
            pass
        print(f"❌ Action failed: Selector '{selector}' did not appear within {wait_flag_timeout} minutes.")
        return True

    return True


# Click a button or element specified by the CSS selector.
def click(page, selector, input_time=None, wait_flag=False):
    if not selector:
        print("❌ Error: Missing CSS selector. Format: click <selector>")
        return

    ok = wait_until_time_or_appear(page, selector, input_time, wait_flag)
    if ok is False:
        return

    print(f"➡️ Attempting to click: '{selector}'...")
    try:
        page.locator(selector).click(timeout=30000)
    except Exception as e:
        print(f"❌ Action failed: {e}")
    else:
        print("✅ Button clicked successfully!")


# Fill in text into an input field specified by the CSS selector.
def fill(page, selector, text, input_time=None, wait_flag=False):
    if not selector:
        print("❌ Error: Missing CSS selector. Format: fill <selector>")
        return
    if not text:
        print("❌ Error: Missing text to fill on input field. Please provide the text to be filled.")
        return

    ok = wait_until_time_or_appear(page, selector, input_time, wait_flag)
    if ok is False:
        return

    print(f"➡️ Attempting to fill: '{selector}' with '{text}'...")
    try:
        page.locator(selector).fill(text, timeout=30000)
    except Exception as e:
        print(f"❌ Action failed: {e}")
    else:
        print("✅ Input field filled successfully!")


# Press a keyboard key on a selected element.
def press(page, selector, key, input_time=None, wait_flag=False):
    if not selector:
        print("❌ Error: Missing CSS selector. Format: fill <selector>")
        return
    if not key:
        print("❌ Error: Missing key string. Format: press <selector> <key>")
        return

    ok = wait_until_time_or_appear(page, selector, input_time, wait_flag)
    if ok is False:
        return

    print(f"➡️ Attempting to press '{key}' on '{selector}'...")
    try:
        page.locator(selector).press(key, timeout=30000)
    except Exception as e:
        print(f"❌ Action failed: {e}")
    else:
        print("✅ Key press completed successfully!")


# Retrieve text from an HTML element specified by the CSS selector.
def text(page, selector, input_time=None, wait_flag=False):
    if not selector:
        print("❌ Error: Missing CSS selector. Format: text <selector>")
        return None

    ok = wait_until_time_or_appear(page, selector, input_time, wait_flag)
    if ok is False:
        return None

    try:
        content = page.locator(selector).text_content(timeout=30000)
        text_value = content if content is not None else ""
        print(f"✅ Text content retrieved': {text_value}")
        return text_value
    except Exception as e:
        print(f"❌ Action failed: {e}")
        return None


# Retrieve an image from an HTML element specified by the CSS selector.
def image(page, selector, input_time=None, wait_flag=False):
    global image_capture_count

    if not selector:
        print("❌ Error: Missing CSS selector. Format: image <selector>")
        return None

    ok = wait_until_time_or_appear(page, selector, input_time, wait_flag)
    if ok is False:
        return None

    os.makedirs(image_filepath, exist_ok=True)
    filename = f"capture{image_capture_count + 1}.png"
    path = os.path.join(image_filepath, filename)

    try:
        page.locator(selector).screenshot(path=path, timeout=30000)
        image_capture_count += 1
        print(f"✅ Saved image for '{selector}' to {path}")
        return path
    except Exception as e:
        print(f"❌ Action failed: {e}")
        return None


def list_tabs(page):
    # To refresh state of pages
    try:
        page.wait_for_timeout(1)
    except Exception:
        pass

    pages = page.context.pages
    if not pages:
        print("⚠️ No open tabs found.")
        return
    print("✅ Open tabs:")
    for index, page in enumerate(pages):
        try:
            if page.is_closed():
                continue
            print(f"  [{index}] {page.url} | {page.title()}")
        except Exception:
            try:
                print(f"  [{index}] {page.url} | <unavailable>")
            except Exception:
                continue



def switch_tab(page, switch_body):
    # To refresh state of pages
    try:
        page.wait_for_timeout(1)
    except Exception:
        pass

    # Validate switch_body and tab index
    if not switch_body:
        print("❌ Error: switch requires a tab index.")
        return
    try:
        index = int(switch_body)
    except ValueError:
        print("❌ Error: switch requires a numeric tab index.")
        return
    
    # Validate whether the tab index is within range of open tabs
    pages = page.context.pages
    if not pages:
        print("❌ No open tabs to switch.")
        return None
    if index < 0 or index >= len(pages):
        print(f"❌ Invalid tab index {index}. Use the tabs command to see valid tab indexes.")
        return None
    
    # Switch to tab
    page = pages[index]
    try:
        if page.is_closed():
            print("❌ The selected tab is closed. Cannot switch.")
            return
        title = page.title()
    except Exception:
        title = "<unavailable>"
    print(f"✅ Switched to tab {index}: {page.url} | {title}")
    return page


def reload(page, input_time=None):
    ok = wait_until_time_or_appear(page, None, input_time, False)  # reload doesn't need a selector or wait_flag, but we can still use the time-based waiting
    if ok is False:
        return
    
    try:
        page.wait_for_timeout(1)     # To refresh state of pages
        if page.is_closed():
            raise Exception("Current page is closed. Cannot reload.")
    except Exception as e:
        print("❌ The page cannot be loaded properly or the page does not exist. Reload aborted.")
        return

    print("➡️ Reloading page...")
    try:
        page.reload(timeout=10000)  # 10-second limit so it doesn't hang forever
    except Exception as e:
        print(f"⚠️ The page is still loading or the reload failed: {e}")
    else:
        print("✅ Page reloaded successfully!")


# Run a custom batch of browser actions.
def batch(page):
    # Customize this function to perform a series of browser actions.
    # You can also add loops, sleeps, or any other control flow here.
    # Function prototypes:
    #    1. click(page, selector, input_time=None, wait_flag=False)
    #    2. fill(page, selector, text, input_time=None, wait_flag=False)
    #    3. press(page, selector, key, input_time=None, wait_flag=False)
    #    4. text(page, selector, input_time=None, wait_flag=False)
    #    5. image(page, selector, input_time=None, wait_flag=False)
    #    6. switch_tab(page, switch_body)
    #    7. reload(page, input_time=None)
    # Notes:
    #    1. selector, input_time, text, key are all of str | None type
    #    2. key is in the format so that page.locator().press(key) is valid. Examples of key:
    #        'Enter', 'Control+V', 'a', 'A', 'Digit1'
    #    3. Both input_time and wait_flag may be used together. When both are provided, the function
    #       waits until the scheduled time first and then waits for the selector to appear.
    #    4. Use page.wait_for_timeout(milliseconds) instead of time.sleep() to add extra waiting time between actions if needed.
    # Example usage:
    #    click(page, selector, input_time="20:30:00", wait_flag=True)  # Click a button at 8:30pm when it appears
    #    fill(page, selector, "secure_password", wait_flag=True)  # Fill in text when field appears
    #    press(page, selector, "Enter")  # Press 'Enter' on an element immediately
    #    text(page, selector, wait_flag=True)  # Extract text from element when it appears
    #    image(page, selector, input_time="00:00:00")  # Get image of an element at midnight
    #    switch_tab(page, "1")  # Switch to the second tab
    #    reload(page, input_time="09:15:00")  # Reload the page at 9:15am
    pass


def help():
    print("=" * 60)
    print("COMMAND FORMATS:")
    print("  To click:           click <selector> [-time HH:MM:SS] [-wait]")
    print("  To fill:            fill <selector> -text <text> [-time HH:MM:SS] [-wait]")
    print("  To press a key:     press <selector> -key <key> [-time HH:MM:SS] [-wait]")
    print("      <key> examples:   'Enter', 'Control+V', 'a', 'A', 'Digit1'")
    print("  To get text:        text <selector> [-time HH:MM:SS] [-wait]")
    print("  To get image:       image <selector> [-time HH:MM:SS] [-wait]")
    print("  To list tabs:       tabs")
    print("  To switch tab:      switch <tab index>")
    print("  To reload page:     reload [-time HH:MM:SS]")
    print("  To run batch:       batch")
    print("  To print help menu: help")
    print("  To exit:            exit")
    print("=" * 60)


# Main interactive loop to accept user commands and perform browser actions accordingly.
def interactive_browser():
    print("\n➡️ Launching Chromium... Please wait.")

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir="./user_data_dir",  # Change this to a valid directory on your system
            headless=False,  # Set to False so you can see the screen!
            viewport={"width": screen_width, "height": screen_height},
            handle_sigint=False  # so that ctrl+c while waiting will keep the webpage
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
        help()

        # 2. Start the interactive loop
        while True:
            try:
                user_input = input("➜ ] Enter command: ").strip()
                if not user_input:
                    continue
                    
                # try:
                #     page.wait_for_timeout(1)   # To refresh state of pages
                # except Exception:
                #     pass
                if page.is_closed():
                    print("⚠️ Warning: The current page is closed. Some actions may not work until you switch to another open tab.")

                # 3. Handle standalone commands
                action = user_input.split(" ", 1)[0].lower().strip()
                if action == "exit":
                    print("Closing browser and exiting.")
                    break
                elif action == "batch":
                    batch(page)
                    continue
                elif action == "help":
                    help()
                    continue
                elif action == "tabs":
                    list_tabs(page)
                    continue
                elif action == "switch":
                    switch_body = user_input[len("switch"):].strip()
                    new_page = switch_tab(page, switch_body)
                    if new_page is not None:
                        page = new_page
                    continue

                # 4. Parse the flags to handle commands supporting optional or required flags
                command_body = user_input[len(action):].strip()
                selector, required_text, input_time, wait_flag = parse_flags(command_body)

                if selector == "" and action in ["click", "fill", "press", "text", "image"]:
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
                        raise ValueError("Expected flags (-key) not present.")
                    press(page, selector, required_text, input_time, wait_flag)

                elif action == "text":
                    if required_text != None:
                        raise ValueError("Unexpected extra flags (-text or -key).")
                    text(page, selector, input_time, wait_flag)

                elif action == "image":
                    if required_text != None:
                        raise ValueError("Unexpected extra flags (-text or -key).")
                    image(page, selector, input_time, wait_flag)

                elif action == "reload":
                    if wait_flag != False:
                        raise ValueError("-wait flag is not applicable for reload command.")
                    if required_text != None:
                        raise ValueError("Unexpected extra flags (-text or -key).")
                    reload(page, input_time)

                else:
                    print(f"❌ Unknown action '{action}'.")
                ###################################################

           # 5. Catch any errors in command parsing or execution and print user-friendly messages
            except ValueError as e:
                print(f"❌ Invalid action: {e}")
                continue
            except Exception as e:
                print(f"❌ Action failed: {e}")
            
            print()  # Print new line for readability between commands


if __name__ == "__main__":
    interactive_browser()