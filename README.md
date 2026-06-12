# Webpage Controller

`Webpage Controller` is a small browser automation utility built around `webtest.py`.
It uses Playwright to launch Chromium, open a predefined URL, and let you run simple interactive commands against page elements.

## What it does

The main script supports:
- clicking a page element
- filling text into an input field
- pressing keyboard keys on an element
- extracting text content from an element
- taking a screenshot of an element
- listing and switching browser tabs
- reloading the current page
- running custom batch actions via `batch()`

Each action can optionally wait until a target time or until the target element appears.

## Prerequisites

- Python 3.8 or newer
- Chrome installed on your machine
- `playwright` Python package

## Setup

If you only want to run the main script `webtest.py`, install the required dependencies and browser runtime:

```bash
pip install playwright
python -m playwright install chromium
```

Then run the script from the repository root:

```bash
python webtest.py
```

## Customization

You can change default behavior by editing the following values in `webtest.py`:
- `url` — the page opened at startup
- `screen_width` / `screen_height` — browser viewport size
- `wait_flag_timeout` — maximum wait time in minutes for `-wait`
- `image_filepath` — folder where element screenshots are saved
- `user_data_dir` — persistent browser profile directory

## Interactive commands

Supported commands in the prompt:

- `click <selector> [-time HH:MM:SS | -wait]`
  - Click the element matching the CSS selector.

- `fill <selector> -text <text> [-time HH:MM:SS | -wait]`
  - Fill an input with the provided text.

- `press <selector> -key <key> [-time HH:MM:SS | -wait]`
  - Press a keyboard key on the element.
  - Examples: `Enter`, `Control+v`, `a`, `A`, `Digit1`

- `text <selector> [-time HH:MM:SS | -wait]`
  - Print the text content of the element.

- `image <selector> [-time HH:MM:SS | -wait]`
  - Save a screenshot of the element.
  - Files are saved under `image_filepath` (defaults to `screenshots/`) as `capture1.png`, `capture2.png`, etc.

- `tabs`
  - List all open browser tabs.

- `switch <tab index>`
  - Switch the active context to a different open tab.

- `reload [-time HH:MM:SS]`
  - Reload the current page.
  - Supports `-time` scheduling; does not support `-wait`.

- `batch`
  - Execute the custom `batch(page)` routine.
  - Edit `webtest.py` to add your own sequence of actions.

- `help`
  - Print the command menu.

- `exit`
  - Close the browser and exit.

## Wait behavior

- `-time HH:MM:SS` waits until the next occurrence of that clock time.
- `-wait` waits for the element to appear in the page, up to `wait_flag_timeout` minutes.
- `reload` can be scheduled with `-time` but does not accept `-wait`.

## Notes

- Use a valid and visible CSS selector for each element you target.
- Do not use quotation marks around \<selector> or \<key> (for `press`) in the command input. Only use quotation marks around \<text> (for `fill`) if you want to fill with text that really contains quotation marks.
- The script uses a persistent Chromium context and stores browser profile data in `user_data_dir/`.
- This tool is meant for small automation experiments, not large-scale scraping.

## Other helper files

- `images_2_pdf.py` — combine saved screenshots from `screenshots/` into a single PDF.
- `test_datetime.py` — tests the `time_difference()` helper used by `webtest.py`.
