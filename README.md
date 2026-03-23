# Amazon Price Tracker

This Python script tracks the price of an Amazon product. It checks the price at regular intervals and sends an email alert if the price drops below a target value. Price history is saved to a CSV file for analysis.

## Features

* Track price of any Amazon product
* Save price history with timestamp
* Send email alert when price drops below target
* Analyze price history for minimum maximum and average prices

## Requirements

* Python 3
* Libraries: `requests` `beautifulsoup4` `pandas`

## Usage

1. Update the `URL` variable with the product link
2. Set your target price in `TARGET_PRICE`
3. Enter your email and password in `send_email` function
4. Run the script:

```bash
python amzn-scrap.py
