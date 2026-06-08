# Webpage Controller

This repository contains `webtest.py`, a small Playwright-based browser automation script for interacting with web pages using a simple command loop.

## Overview

The script launches a Chromium browser (via Chrome channel) and opens a predefined URL. It supports several helper functions to:

- click page elements by CSS selector
- click page elements by CSS selector at a specific time
- fill input fields by CSS selector

Note that you can also directly operate on the webpage instead of using the helper functions.

## Prerequisites

- Python 3.8+
- `playwright` package
- Chrome installed on the machine

## Setup

Install the required Python dependency:

```bash
pip install playwright
python -m playwright install chromium
```

## Usage

Run the script from the repository root:

```bash
python webtest.py
```

The script will open a browser window and print available command formats.

Moreover, customize the webpage controller in the following ways:

- Update the `url` variable in `webtest.py` to change the starting page.
- Adjust `screen_width` and `screen_height` if your display requires a different viewport.

### Supported Commands

- `click <selector>`
  - Click an element identified by the given CSS selector.

- `ctime <selector>`
  - The script prompts for the target time in `HH:MM:SS` format.
  - Wait until a specified time has passed, and then click the element identified by the given CSS selector.

- `fill <selector>`
  - The script prompts for the text to insert.
  - Fill an input field identified by the given CSS selector.

- `exit`
  - Close the browser and exit the interactive loop.

## Video Showcase


## `webtest.py` functions specifications

- `click(page, selector)`
  - Clicks a page element within a 5 second limit.
  - Prints errors and returns immediately if the CSS selector is missing or invalid.

- `ctime(page, selector, input_time)`
  - Waits until the target time and clicks the page element.
  - Clicks immediately if the time has passed, and every 10ms after the time has passed, until it is successfully clicked.
  - Uses `time_difference()` to display how much time remains.
  - Prints errors and returns immediately if the selector is missing or invalid, or the time format is invalid.

- `fill(page, selector, text)`
  - Fills an input element with the provided text within a 5 second limit.
  - Prints errors if the selector is missing or invalid, or the text is empty.


## Other helper files

- `iamges_2_pdf.py`: Combine images in the `screenshots/` directory to a single PDF file.
- `test_datatime.py`: Testing `time_difference()` using sample time strings.

## Notes

- Make sure the CSS selectors you provide are present and visible on the loaded page.
- The script is intended for experimentation and automating simple web tasks, not for large-scale scraping.
