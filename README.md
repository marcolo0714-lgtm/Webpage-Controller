# Webpage Controller

This repository contains `webtest.py`, a small Playwright-based browser automation script for interacting with web pages using a simple command loop.

## Overview

The script launches a Chromium browser (via Chrome channel) and opens a predefined URL. It supports several helper functions to:

- click page elements by CSS selector
- fill input fields by CSS selector
- print text content from page elements
- save screenshots of page elements
- wait until a specific time or until an element appears before acting

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

- `click <selector> [-time HH:MM:SS | -wait]`
  - Click an element identified by the given CSS selector.
  - Use `-time HH:MM:SS` to wait until the specified time before clicking.
  - Use `-wait` to wait until the element appears on screen (up to 30 minutes) before clicking.

- `fill <selector> <text> [-time HH:MM:SS | -wait]`
  - Fill an input field identified by the given CSS selector with the provided text.
  - Use `-time HH:MM:SS` to delay the fill until a specific time.
  - Use `-wait` to wait until the element appears on screen (up to 30 minutes) before filling.

- `text <selector> [-time HH:MM:SS | -wait]`
  - Print and return the text content of a page element identified by the CSS selector.
  - Supports `-time` and `-wait` like `click` and `fill`.

- `image <selector> [-time HH:MM:SS | -wait]`
  - Save a screenshot of the page element identified by the CSS selector.
  - Files are saved under `screenshots/` as `capture1.png`, `capture2.png`, etc.
  - Supports `-time` and `-wait` like `click` and `fill`.

- `exit`
  - Close the browser and exit the interactive loop.

## Video Showcase


## `webtest.py` functions specifications

- `click(page, selector, input_time=None, wait_flag=False)`
  - Clicks a page element by CSS selector.
  - Supports `input_time` to delay the click until a specific `HH:MM:SS` time.
  - Supports `wait_flag` to wait for the selector to appear on screen for up to 30 minutes.
  - Prints errors and returns if the selector is missing, invalid, or not visible.

- `fill(page, selector, text, input_time=None, wait_flag=False)`
  - Fills an input element with the provided text within a 5 second limit.
  - Supports `input_time` to delay the fill until a specific `HH:MM:SS` time.
  - Supports `wait_flag` to wait for the selector to appear on screen for up to 30 minutes.
  - Prints errors if the selector is missing or invalid, or the text is empty.

- `text(page, selector, input_time=None, wait_flag=False)`
  - Prints and returns the text content of the selected element.
  - Supports delayed execution with `-time` or waiting for the element with `-wait`.

- `image(page, selector, input_time=None, wait_flag=False)`
  - Saves a screenshot of the selected element.
  - Screenshots are stored in `screenshots/` with sequential names like `capture1.png`, `capture2.png`, etc.
  - Supports delayed execution with `-time` or waiting for the element with `-wait`.

## Other helper files

- `iamges_2_pdf.py`: Combine images in the `screenshots/` directory to a single PDF file.
- `test_datetime.py`: Testing `time_difference()` using sample time strings.

## Notes

- Make sure the CSS selectors you provide are present and visible on the loaded page.
- The script is intended for experimentation and automating simple web tasks, not for large-scale scraping.
