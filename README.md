# Webpage Controller

This repository contains `webtest.py`, a small Playwright-based browser automation script for interacting with web pages using a simple command loop.

## Overview

The script launches a Chromium browser (via Chrome channel) and opens a predefined URL. It supports several helper functions to:

- click webpage element
- fill input field with text
- print text content from a webpage element
- save screenshots of a webpage element
- press keyboard keys on a webpage element

All of these functions support waiting until a specific time or until the element appears before acting.
- A webpage element is specified by its CSS selector. To obtain the CSS selector of a webpage element, right-click on a webpage element, select "Inspect", right-click on the highlighted line on the HTML interface, and select "Copy selector".
- Note that you can also directly operate on the webpage opened by the program, instead of using the helper functions.

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
- Adjust `screen_width` and `screen_height` to
- Update `wait_flag_timeout` to

### Supported Commands

- `click <selector> [-time HH:MM:SS | -wait]`
  - Click an element identified by the given CSS selector.

- `fill <selector> -text <text> [-time HH:MM:SS | -wait]`
  - Fill an input field identified by the given CSS selector with the provided text.

- `press <selector> -key <key> [-time HH:MM:SS | -wait]`
  - Press a keyboard key on a webpage element identified by its CSS selector.

- `text <selector> [-time HH:MM:SS | -wait]`
  - Print and return the text content of a page element identified by the CSS selector.

- `image <selector> [-time HH:MM:SS | -wait]`
  - Save a screenshot of the page element identified by the CSS selector.
  - Files are saved under `screenshots/` as `capture1.png`, `capture2.png`, etc.

All of the above functions support either a `-time` or  `-wait` flag:
  - Use `-time HH:MM:SS` to wait until the specified time before clicking.
  - Use `-wait` to wait until the element appears on screen (up to 30 minutes, can be customized) before clicking.

- `exit`
  - Close the browser and exit the interactive loop.

## Video Showcase



## Other helper files

- `iamges_2_pdf.py`: Combine images in the `screenshots/` directory to a single PDF file.
- `test_datetime.py`: Testing `time_difference()` using sample time strings.

## Notes

- Make sure the CSS selectors you provide are present and visible on the loaded page.
- The script is intended for experimentation and automating simple web tasks, not for large-scale scraping.

## Future Directions
- 