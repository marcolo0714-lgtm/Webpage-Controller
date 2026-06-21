from playwright.async_api import async_playwright
import asyncio
import os
import signal
from datetime import datetime, timedelta

_cancelled = False

def _handle_sigint(signum, frame):
    global _cancelled
    _cancelled = True

url = "https://www.lib.cuhk.edu.hk/en/"
# url = "https://www.hkemobility.gov.hk/tc/route-search/pt"
# url = "http://youtube.com"

screen_width = 1525  # 1525
screen_height = 475  # 825
wait_flag_timeout = 30  # in minutes
standard_timeout = 5  # in seconds

image_filepath = "screenshots/"
image_capture_count = 0


def time_difference(target_datetime):
    """
    Calculates the difference between target_datetime and the current time,
    and returns a formatted string: 'x hours y minutes z seconds'
    """
    now = datetime.now()
    time_delta = target_datetime - now
    total_seconds = int(time_delta.total_seconds())
    if total_seconds <= 0:
        total_seconds += 86400
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

    has_time = "-time" in tokens
    wait_flag = "-wait" in tokens
    try:
        time_value = tokens[tokens.index("-time") + 1] if has_time else None
    except (IndexError, ValueError):
        raise ValueError("-time flag present, but contain no arguments.")

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

    if req_flag_pos == -1:
        selector = ' '.join(tokens[0 : final_flag_pos])
    else:
        selector = ' '.join(tokens[0 : min(req_flag_pos, final_flag_pos)])

    return selector, required_text, time_value, wait_flag


async def wait_until_time_or_appear(page, selector, input_time, wait_flag, current_tab_index=0):
    """Wait until a target time and/or until selector appears.
    Returns (ok, maybe_recovered_page) — ok is True when wait completed,
    False when user cancelled. The returned page may differ if recovery happened."""
    global _cancelled

    if input_time:
        try:
            target_datetime = get_target_datetime(input_time)
        except ValueError as e:
            print(f"❌ Action failed: {e}")
            return True, page

        print(f"🕒 Waiting until {input_time} (in {time_difference(target_datetime)})... Press Ctrl+C to cancel.")
        _cancelled = False
        previous_url = page.url
        while datetime.now() < target_datetime:
            if _cancelled:
                print("⚠️ Wait cancelled by user.")
                return False, page
            if page.url != previous_url:
                print(f"🔗 Page navigated to: {page.url}")
                previous_url = page.url

    if wait_flag:
        deadline = datetime.now() + timedelta(minutes=wait_flag_timeout)
        print(f"🕒 Waiting for selector '{selector}' to appear on screen (timeout: {wait_flag_timeout} mins). Press Ctrl+C to cancel.")
        _cancelled = False
        previous_url = page.url
        while datetime.now() < deadline:
            if _cancelled:
                print("⚠️ Wait cancelled by user.")
                return False, page
            if page.url != previous_url:
                print(f"🔗 Page navigated to: {page.url}")
                previous_url = page.url
            try:
                await page.locator(selector).wait_for(state="attached", timeout=100)
                return True, page
            except Exception:
                pass
        print(f"❌ Action failed: Selector '{selector}' did not appear within {wait_flag_timeout} minutes.")
        return True, page

    return True, page


async def click(page, selector, input_time=None, wait_flag=False, current_tab_index=0):
    if not selector:
        print("❌ Error: Missing CSS selector. Format: click <selector>")
        return page

    ok, page = await wait_until_time_or_appear(page, selector, input_time, wait_flag, current_tab_index)
    if ok is False:
        return page

    print(f"➡️ Attempting to click: '{selector}'...")
    try:
        await page.locator(selector).click(timeout=standard_timeout * 1000)
    except Exception as e:
        print(f"❌ Action failed: {e}")
    else:
        print("✅ Button clicked successfully!")
    return page


async def fill(page, selector, text, input_time=None, wait_flag=False, current_tab_index=0):
    if not selector:
        print("❌ Error: Missing CSS selector. Format: fill <selector>")
        return page
    if not text:
        print("❌ Error: Missing text to fill on input field. Please provide the text to be filled.")
        return page

    ok, page = await wait_until_time_or_appear(page, selector, input_time, wait_flag, current_tab_index)
    if ok is False:
        return page

    print(f"➡️ Attempting to fill: '{selector}' with '{text}'...")
    try:
        await page.locator(selector).fill(text, timeout=standard_timeout * 1000)
    except Exception as e:
        print(f"❌ Action failed: {e}")
    else:
        print("✅ Input field filled successfully!")
    return page


async def press(page, selector, key, input_time=None, wait_flag=False, current_tab_index=0):
    if not selector:
        print("❌ Error: Missing CSS selector. Format: fill <selector>")
        return page
    if not key:
        print("❌ Error: Missing key string. Format: press <selector> <key>")
        return page

    ok, page = await wait_until_time_or_appear(page, selector, input_time, wait_flag, current_tab_index)
    if ok is False:
        return page

    print(f"➡️ Attempting to press '{key}' on '{selector}'...")
    try:
        await page.locator(selector).press(key, timeout=standard_timeout * 1000)
    except Exception as e:
        print(f"❌ Action failed: {e}")
    else:
        print("✅ Key press completed successfully!")
    return page


async def text(page, selector, input_time=None, wait_flag=False, current_tab_index=0):
    if not selector:
        print("❌ Error: Missing CSS selector. Format: text <selector>")
        return None, page

    ok, page = await wait_until_time_or_appear(page, selector, input_time, wait_flag, current_tab_index)
    if ok is False:
        return None, page

    try:
        content = await page.locator(selector).text_content(timeout=standard_timeout * 1000)
        text_value = content if content is not None else ""
        print(f"✅ Text content retrieved: {text_value}")
        return text_value, page
    except Exception as e:
        print(f"❌ Action failed: {e}")
        return None, page


async def image(page, selector, input_time=None, wait_flag=False, current_tab_index=0):
    global image_capture_count

    if not selector:
        print("❌ Error: Missing CSS selector. Format: image <selector>")
        return None, page

    ok, page = await wait_until_time_or_appear(page, selector, input_time, wait_flag, current_tab_index)
    if ok is False:
        return None, page

    os.makedirs(image_filepath, exist_ok=True)

    i = 1
    while True:
        filename = f"capture{i}.png"
        path = os.path.join(image_filepath, filename)
        if not os.path.exists(path):
            break
        i += 1

    try:
        await page.locator(selector).screenshot(path=path, timeout=standard_timeout * 1000)
        image_capture_count = i
        print(f"✅ Saved image for '{selector}' to {path}")
        return path, page
    except Exception as e:
        print(f"❌ Action failed: {e}")
        return None, page


async def list_tabs(page):
    pages = page.context.pages
    if not pages:
        print("⚠️ No open tabs found.")
        return
    print("✅ Open tabs:")
    for index, p in enumerate(pages):
        try:
            if p.is_closed():
                continue
            marker = " ▶" if p is page else "  "
            print(f"  [{index}]{marker} {p.url} | {await p.title()}")
        except Exception:
            try:
                print(f"  [{index}] {p.url} | <unavailable>")
            except Exception:
                continue


async def switch_tab(page, switch_body):
    if not switch_body:
        print("❌ Error: switch requires a tab index.")
        return page, None
    try:
        index = int(switch_body)
    except ValueError:
        print("❌ Error: switch requires a numeric tab index.")
        return page, None

    pages = page.context.pages
    if not pages:
        print("❌ No open tabs to switch.")
        return page, None
    if index < 0 or index >= len(pages):
        print(f"❌ Invalid tab index {index}. Use the tabs command to see valid tab indexes.")
        return page, None

    new_page = pages[index]
    try:
        if new_page.is_closed():
            print("❌ The selected tab is closed. Cannot switch.")
            return page, None
        title = await new_page.title()
    except Exception:
        title = "<unavailable>"
    print(f"✅ Switched to tab {index}: {new_page.url} | {title}")
    return new_page, index


async def reload(page, input_time=None, current_tab_index=0):
    if page.is_closed():
        print("❌ The page cannot be loaded properly or the page does not exist. Reload aborted.")
        return page

    ok, page = await wait_until_time_or_appear(page, None, input_time, False, current_tab_index)
    if ok is False:
        return page

    print("➡️ Reloading page...")
    try:
        await page.reload(timeout=standard_timeout * 1000)
    except Exception as e:
        print(f"⚠️ The page is still loading or the reload failed: {e}")
    else:
        print("✅ Page reloaded successfully!")
    return page


async def goto(page, goto_url, input_time=None):
    if not goto_url:
        print("❌ Error: goto requires a URL. Format: goto <url> [-time HH:MM:SS]")
        return page

    if input_time:
        ok, page = await wait_until_time_or_appear(page, None, input_time, False)
        if ok is False:
            return page

    print(f"➡️ Navigating to: {goto_url}...")
    try:
        await page.goto(goto_url, timeout=standard_timeout * 1000)
    except Exception as e:
        print(f"❌ Navigation failed: {e}")
    else:
        print(f"✅ Successfully loaded: {page.url}")
    return page


async def newtab(page):
    new_page = await page.context.new_page()
    new_index = len(page.context.pages) - 1
    print(f"✅ Opened new tab [{new_index}]: {new_page.url}")
    return new_page, new_index


async def batch(page):
    # Customize this function to perform a series of browser actions.
    # You can also add loops, sleeps, or any other control flow here.
    # Function prototypes:
    #    1. page = await click(page, selector, input_time=None, wait_flag=False, current_tab_index=0)
    #    2. page = await fill(page, selector, text, input_time=None, wait_flag=False, current_tab_index=0)
    #    3. page = await press(page, selector, key, input_time=None, wait_flag=False, current_tab_index=0)
    #    4. text_value, page = await text(page, selector, input_time=None, wait_flag=False, current_tab_index=0)
    #    5. image_path, page = await image(page, selector, input_time=None, wait_flag=False, current_tab_index=0)
    #    6. result = await switch_tab(page, switch_body) -> returns (page, index) tuple or (page, None)
    #    7. page = await reload(page, input_time=None, current_tab_index=0)
    #    8. page = await goto(page, url)
    #    9. new_page, new_index = await newtab(page)
    # Notes:
    #    1. selector, input_time, text, key are all of str | None type
    #    2. key is in the format so that page.locator().press(key) is valid. Examples of key:
    #        'Enter', 'Control+V', 'a', 'A', 'Digit1'
    #    3. Both input_time and wait_flag may be used together. When both are provided, the function
    #       waits until the scheduled time first and then waits for the selector to appear.
    #    4. Use page.wait_for_load_state to wait for the page to load between actions.
    # Example usage:
    #    page = await click(page, selector, input_time="20:30:00", wait_flag=True)
    #    page = await fill(page, selector, "secure_password", wait_flag=True)
    #    page = await press(page, selector, "Enter")
    #    text_value, page = await text(page, selector, wait_flag=True)
    #    image_path, page = await image(page, selector, input_time="00:00:00")
    #    result = await switch_tab(page, "1")
    #    if result is not None:
    #        page, _ = result
    #    page = await reload(page, input_time="09:15:00")
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
    print("  To navigate to URL: goto <url> [-time HH:MM:SS]")
    print("  To open new tab:    newtab")
    print("  To run batch:       batch")
    print("  To print help menu: help")
    print("  To exit:            exit")
    print("=" * 60)


async def interactive_browser():
    print("\n➡️ Launching Chromium... Please wait.")

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir="./user_data_dir",
            headless=False,
            viewport={"width": screen_width, "height": screen_height},
            handle_sigint=False
        )

        page = await context.new_page()
        current_tab_index = 0

        try:
            await page.goto(url)
            print(f"✅ Successfully loaded: {url}\n")
        except Exception as e:
            print(f"❌ Error loading page: {e}")
            await context.close()
            return

        help()

        while True:
            _cancelled = False
            try:
                try:
                    user_input = input("➜ ] Enter command: ").strip()
                except (EOFError, KeyboardInterrupt):
                    print()
                    continue

                if not user_input:
                    continue

                action = user_input.split(" ", 1)[0].lower().strip()
                if action == "exit":
                    print("Closing browser and exiting.\n")
                    break
                elif action == "batch":
                    await batch(page)
                    print()
                    continue
                elif action == "help":
                    help()
                    print()
                    continue
                elif action == "tabs":
                    await list_tabs(page)
                    print()
                    continue
                elif action == "switch":
                    switch_body = user_input[len("switch"):].strip()
                    new_page, new_index = await switch_tab(page, switch_body)
                    if new_index is not None:
                        page, current_tab_index = new_page, new_index
                    print()
                    continue
                elif action == "newtab":
                    new_page, new_index = await newtab(page)
                    page, current_tab_index = new_page, new_index
                    print()
                    continue

                command_body = user_input[len(action):].strip()
                selector, required_text, input_time, wait_flag = parse_flags(command_body)

                if selector == "" and action in ["click", "fill", "press", "text", "image"]:
                    raise ValueError("Selector is required, but not present.")

                ###################################################
                if action == "click":
                    if required_text is not None:
                        raise ValueError("Unexpected extra flags (-text or -key).")
                    page = await click(page, selector, input_time, wait_flag, current_tab_index)

                elif action == "fill":
                    if required_text is None:
                        raise ValueError("Expected flags (-text) not present.")
                    page = await fill(page, selector, required_text, input_time, wait_flag, current_tab_index)

                elif action == "press":
                    if required_text is None:
                        raise ValueError("Expected flags (-key) not present.")
                    page = await press(page, selector, required_text, input_time, wait_flag, current_tab_index)

                elif action == "text":
                    if required_text is not None:
                        raise ValueError("Unexpected extra flags (-text or -key).")
                    _, page = await text(page, selector, input_time, wait_flag, current_tab_index)

                elif action == "image":
                    if required_text is not None:
                        raise ValueError("Unexpected extra flags (-text or -key).")
                    _, page = await image(page, selector, input_time, wait_flag, current_tab_index)

                elif action == "reload":
                    if wait_flag != False:
                        raise ValueError("-wait flag is not applicable for reload command.")
                    if required_text is not None:
                        raise ValueError("Unexpected extra flags (-text or -key).")
                    page = await reload(page, input_time, current_tab_index)

                elif action == "goto":
                    if wait_flag != False:
                        raise ValueError("-wait flag is not applicable for goto command.")
                    if required_text is not None:
                        raise ValueError("Unexpected extra flags (-text or -key).")
                    page = await goto(page, selector, input_time)  # selector contains the URL for goto command

                else:
                    print(f"❌ Unknown action '{action}'.")
                ###################################################

            except ValueError as e:
                print(f"❌ Invalid action: {e}")
                continue
            except Exception as e:
                print(f"❌ Action failed: {e}")

            print()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, _handle_sigint)
    asyncio.run(interactive_browser())
