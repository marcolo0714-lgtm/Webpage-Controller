from playwright.sync_api import sync_playwright
import sys
import time
from datetime import datetime

url = "https://ebookcentral.proquest.com/lib/cuhk-ebooks/detail.action?pq-origsite=primo&docID=5186043"
# url = "https://www.hkemobility.gov.hk/tc/route-search/pt"
# url = "http://youtube.com"

screen_width = 1525
screen_height = 825

# Helper function for ctime() to calculate the time difference and format it nicely for user feedback
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

# This function is designed to click a button or element specified by the CSS selector.
def click(page, selector):
    if not selector:
        print("❌ Error: Missing CSS selector. Format: click <selector>")
        return
    print(f"Attempting to click: '{selector}'...")
    try:
        page.click(selector, timeout=5000)  # 5-second limit so it doesn't hang forever
    except Exception as e:
        print(f"❌ Action failed: Make sure the CSS selector is correct and visible on screen.")
    finally:
        print("✅ Button clicked successfully!")


# This function is designed to click a button or element specified by the CSS selector at a specific time.
def ctime(page, selector, input_time):
    if not selector:
        print("❌ Error: Missing CSS selector. Format: ctime <selector>")
        return
    if not input_time:
        print("❌ Error: Missing time input. Please provide the time in HH:MM:SS format.")
        return
    if page.locator(selector).count() == 0:
        print(f"❌ Aborted: Selector '{selector}' cannot be found on the page right now.")
        return
    
    target_time = datetime.strptime(input_time, "%H:%M:%S").time()
    target_datetime = datetime.combine(datetime.now().date(), target_time)
    print(f"Waiting to click '{selector}' at {input_time} (in {time_difference(target_datetime)})...")
    try:
        # checking every 10 milliseconds to see if we've reached the target time, then click immediately when we do
        while True:
            now = datetime.now()
            if now >= target_datetime:
                page.click(selector, timeout=5000)  # 5-second limit so it doesn't hang forever
                print("✅ Button clicked successfully!")
                break
            time.sleep(0.01)  # Check every 10 milliseconds to avoid busy-waiting
    except Exception as e:
        print(f"❌ Action failed: Make sure the CSS selector is correct and visible on screen, and the time format is correct.")


# This function is designed to fill in text into an input field specified by the CSS selector.
def fill(page, selector, text):
    if not selector:
        print("❌ Error: Missing CSS selector. Format: fill <selector>")
        return
    if not text:
        print("❌ Error: Missing text to fill on input field. Please provide the text to be filled.")
        return
    print(f"Attempting to fill: '{selector}' with '{text}'...")
    try:
        page.fill(selector, text, timeout=5000)  # 5-second limit so it doesn't hang forever
    # If a selector is wrong or takes too long, catch the error so the script doesn't crash
    except Exception as e:
        print(f"❌ Action failed: Make sure the CSS selector is correct and visible on screen.")
    finally:
        print("✅ Input field filled successfully!")

# This function is designed to retrieve text from an HTML element specified by the CSS selector.
def text(page, selector):
    pass

# This function is designed to retrieve an image from an HTML element specified by the CSS selector.
def image(page, selector):
    pass


def interactive_browser():
    print("\nLaunching Google Chrome... Please wait.")

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
        print("  To click:         click <selector>")
        print("  To click at time: ctime <selector>")
        print("  To fill:          fill <selector>")
        print("  To get text:      text <selector>")
        print("  To get image:     image <selector>")
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
                    click(page, user_input.lstrip('click '))   

                elif action == "ctime":
                    input_time = input("Time to click (in HH:MM:SS): ").strip()
                    ctime(page, user_input.lstrip('ctime '), input_time)

                elif action == "fill":
                    input_text = input("Text to be filled in the input field: ").strip()
                    fill(page, user_input.lstrip('fill '), input_text)

                elif action == "text":
                    text(page, user_input.lstrip('text '))

                elif action == "image":
                    image(page, user_input.lstrip('image '))

                else:
                    print(f"❌ Unknown action '{action}'.")
                ###################################################

            except Exception as e:
                print(f"❌ Action failed: {e.value if hasattr(e, 'value') else e}")


if __name__ == "__main__":
    interactive_browser()