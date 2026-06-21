# Webpage Controller

`Webpage Controller` is a browser automation CLI built around `webtest.py`. It uses Playwright's async API to launch a persistent Chromium session and accept interactive commands against page elements — clicking, filling, pressing keys, extracting text, capturing screenshots, and navigating tabs.

## What it does

- click a page element
- fill text into an input field
- press keyboard keys on an element
- extract text content from an element
- save a screenshot of an element
- navigate to a URL
- open new tabs
- list and switch between browser tabs
- reload the current page
- run custom batch actions via `batch()`

Actions support scheduled execution (`-time`) and element-appearance polling (`-wait`). Ctrl+C cancellation is handled at the OS signal level, keeping Playwright's event loop clean.

## Prerequisites

- Python 3.8 or newer
- Chrome installed on your machine
- `playwright` Python package

## Setup

```bash
pip install playwright
python -m playwright install chromium
```

Then run from the repository root:

```bash
python webtest.py
```

## Customization

Edit these values in `webtest.py`:

| Variable | Purpose | Default |
|---|---|---|
| `url` | Page opened at startup | `https://www.lib.cuhk.edu.hk/en/` |
| `screen_width` / `screen_height` | Browser viewport (pixels) | `1280` × `720` |
| `wait_flag_timeout` | Max wait for `-wait` (minutes) | `30` |
| `standard_timeout` | Timeout for individual actions (seconds) | `5` |
| `image_filepath` | Folder for element screenshots | `screenshots/` |
| `user_data_dir` | Persistent browser profile | `./user_data_dir` |

## Interactive commands

```
click   <selector> [-time HH:MM:SS] [-wait]
fill    <selector> -text <text> [-time HH:MM:SS] [-wait]
press   <selector> -key <key> [-time HH:MM:SS] [-wait]
text    <selector> [-time HH:MM:SS] [-wait]
image   <selector> [-time HH:MM:SS] [-wait]
goto    <url> [-time HH:MM:SS]
reload  [-time HH:MM:SS]
newtab
tabs
switch  <tab index>
batch
help
exit
```

### Details

| Command | Behavior |
|---|---|
| `click <selector>` | Click the element matching the CSS selector |
| `fill <selector> -text <text>` | Fill an input with the provided text |
| `press <selector> -key <key>` | Press a keyboard key on the element (e.g. `Enter`, `Control+V`, `a`, `A`, `Digit1`) |
| `text <selector>` | Print the text content of the element |
| `image <selector>` | Save a screenshot of the element as `captureX.png` in `screenshots/`, where X is the smallest unused number |
| `goto <url>` | Navigate the current tab to the given URL (supports `-time`) |
| `reload` | Reload the current tab (supports `-time`; does not support `-wait`) |
| `newtab` | Open a new blank tab and switch to it |
| `tabs` | List all open tabs — the current tab is marked with `▶` |
| `switch <index>` | Switch to the tab at the given index |
| `batch` | Execute the custom `batch(page)` routine defined in `webtest.py` |
| `help` | Print the command menu |
| `exit` | Close the browser and exit |

## Video Showcase

[![Watch the video on YouTube](https://img.youtube.com/vi/W6z0WTP7a5Y/maxresdefault.jpg)](https://youtu.be/W6z0WTP7a5Y)


## IMPORTANT: Do not manually open or navigate tabs

This CLI does **not** support tabs opened manually in the browser window (Ctrl+T, Ctrl+click, typing URLs in the address bar). Playwright cannot reliably track pages created outside its own API, and commands like `tabs`, `switch`, `click`, `fill`, etc. will silently fail or produce incorrect results on manually opened tabs.

**Always use `newtab` and `goto`** to create tabs and navigate:

```
➜ ] newtab
✅ Opened new tab [1]: about:blank
➜ ] goto https://example.com
✅ Successfully loaded: https://example.com/
➜ ] click .my-button -wait
✅ Button clicked successfully!
```

## Wait behavior

### Flag semantics

| Flag | Behavior |
|---|---|
| `-time HH:MM:SS` | Waits until the next occurrence of that clock time before executing the action. Ctrl+C cancels. |
| `-wait` | Polls for the CSS selector to appear in the DOM (up to `wait_flag_timeout` minutes). Checks every ~10 ms. Ctrl+C cancels. |
| Both together | Waits until the scheduled time, then polls for the selector. |

### Program flow during a wait

When you issue `click .btn -wait`, the call chain is:

```
main loop  →  click()  →  wait_until_time_or_appear()
```

`wait_until_time_or_appear` is the core wait function. It runs a `while` loop that polls the page:

```
while deadline not reached:
    if _cancelled flag is set:     ← check for Ctrl+C
        return "cancelled"
    if page URL changed:           ← print "Page navigated to: ..."
        update tracking
    try page.locator(selector).wait_for(timeout=10ms):
        if selector found → return "ok"
        if not → continue looping
```

The 10 ms `wait_for` timeout means each poll is quick. If the selector exists, it returns immediately. If not, it blocks for at most 10 ms and then the loop checks the cancellation flag and URL again.

### Signal handling (Ctrl+C)

Ctrl+C is handled by an OS-level signal handler, **not** by Python exceptions:

1. `signal.signal(signal.SIGINT, _handle_sigint)` is installed before `asyncio.run()` starts.
2. When the user presses Ctrl+C, `_handle_sigint` sets a module-level `_cancelled = True` flag. The signal is consumed here and never reaches `asyncio.run()` or Playwright's event loop.
3. The polling loops in `wait_until_time_or_appear` check `_cancelled` on every iteration and return cleanly if it is set.
4. At the main loop prompt, `_cancelled` is reset to `False` before each command so cancellation does not bleed across commands.

This approach avoids Playwright's internal `CancelledError` propagation, which would leave the CDP connection in a stuck state and cause subsequent commands to hang.

### Key functions involved

| Function | Role |
|---|---|
| `wait_until_time_or_appear` | Runs the polling loop for both `-time` and `-wait`. Checks the cancellation flag, tracks URL changes, delegates to Playwright's `wait_for`. |
| `_handle_sigint` | OS-level signal handler. Sets `_cancelled = True`. |
| `parse_flags` | Parses the command body into selector, required text, time value, and boolean flags. |
| `time_difference` / `get_target_datetime` | Compute and format the time delta for `-time` scheduling. |

## Architecture

- **Async Playwright**: `webtest.py` uses `playwright.async_api` with `asyncio.run()`. All browser interactions (`click`, `fill`, `goto`, `wait_for`, etc.) are `await`ed.
- **Persistent context**: `launch_persistent_context` with `handle_sigint=False` so Playwright does not interfere with the custom signal handler.
- **Tab tracking**: `current_tab_index` tracks which tab is active. `newtab` and `switch` update it. The `tabs` command shows a `▶` marker on the current tab.
- **No `page.wait_for_timeout`**: The codebase deliberately avoids Playwright's `wait_for_timeout` because it can hang indefinitely if the CDP connection is in a bad state. Delays use Python's native `asyncio.sleep` or are removed entirely.

## Notes

- Use valid, visible CSS selectors for elements.
- Do not quote selectors or keys in command input. Quote text for `fill` only if the text itself contains quotation marks.
- The `batch()` function in `webtest.py` is a stub for users to customize with their own action sequences.
- The browser profile is stored persistently in `user_data_dir` (defaults to `user_data_dir/`) — cookies, localStorage, and session data survive across restarts.
- Screenshots saved by `image` are numbered by scanning for the smallest unused `captureX.png` in `image_filepath` (defaults to `screenshots/`).

## Other files

- `images_2_pdf.py` — combine saved screenshots from `screenshots/` into a single PDF.
- `test_datetime.py` — tests the `time_difference()` helper used by `webtest.py`.
