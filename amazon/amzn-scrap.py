from bs4 import BeautifulSoup
import requests
import smtplib
import time
import datetime
import os
import pandas as pd
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

URL = "https://www.amazon.com/Data-Science-Analytics-Funny-T-Shirt/dp/B07PB9XYH8"

headers = {
    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}

cookies = {
    'i18n-prefs': 'USD',
    'lc-main': 'en_US',
}

def check_price():
    try:
        page = requests.get(URL, headers=headers, cookies=cookies, timeout=10)
        page.raise_for_status()
        
        soup = BeautifulSoup(page.content, "html.parser")
    
        if "captcha" in page.url.lower():
            print("Amazon blocked the request with a captcha")
            return None
        
        price_selectors = [
            'span.a-price span.a-offscreen',
            'span#priceblock_ourprice',
            'span#priceblock_dealprice',
            'span.a-price-whole',
            '.a-price .a-offscreen'
        ]
        
        price_text = None
        for selector in price_selectors:
            price_element = soup.select_one(selector)
            if price_element:
                price_text = price_element.get_text().strip()
                print(f"Found price text: {price_text}")
                break
    
        title_selectors = [
            'span#productTitle',
            'h1#title span',
            'h1.a-size-large span'
        ]
        
        title = None
        for selector in title_selectors:
            title_element = soup.select_one(selector)
            if title_element:
                title = title_element.get_text().strip()
                break
        
        if price_text:
            price_clean = re.sub(r'[^\d.,]', '', price_text)
        
            if ',' in price_clean and '.' in price_clean:
                price_clean = price_clean.replace(',', '')
            elif ',' in price_clean:
                price_clean = price_clean.replace(',', '.')
            
            try:
                price_float = float(price_clean)
                print(f"Cleaned price: {price_clean} -> {price_float}")
                
                return {
                    'title': title,
                    'price': price_float,
                    'price_text': price_text
                }
            except ValueError as e:
                print(f"Could not convert '{price_clean}' to float: {e}")
                return None
        else:
            print("Could not find price on the page")
            print("Page title:", soup.title.string if soup.title else "No title")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def save_to_csv(price_data):
    df = pd.DataFrame([price_data])
    df['timestamp'] = datetime.datetime.now()
    
    csv_file = 'price_tracking.csv'
    if os.path.exists(csv_file):
        existing_df = pd.read_csv(csv_file)
        updated_df = pd.concat([existing_df, df], ignore_index=True)
        updated_df.to_csv(csv_file, index=False)
    else:
        df.to_csv(csv_file, index=False)
    print(f"Data saved to {csv_file}")

def send_email(product_info, target_price):
    sender_email = "giorgiggogua@gmail.com"
    sender_password = "************"
    receiver_email = "receiver@gmail.com"
    
    subject = f"Price Drop Alert: {product_info['title']}"
    
    body = f"""
    Price Drop Alert!
    
    Product: {product_info['title']}
    Current Price: {product_info['price_text']}
    Target Price: ${target_price}
    
    Link: {URL}
    """
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print("Email sent successfully!")
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def analyze_price_history():
    csv_file = 'price_tracking.csv'
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        if not df.empty:
            print("\n=== Price History Analysis ===")
            print(f"Total checks: {len(df)}")
            print(f"Minimum price: ${df['price'].min():.2f}")
            print(f"Maximum price: ${df['price'].max():.2f}")
            print(f"Average price: ${df['price'].mean():.2f}")
            print(f"Current price: ${df['price'].iloc[-1]:.2f}")
            print(f"First check: {df['timestamp'].iloc[0]}")
            print(f"Last check: {df['timestamp'].iloc[-1]}")
            return df
    return None

def main():
    TARGET_PRICE = 15.00 
    CHECK_INTERVAL = 3600 
    
    print("Starting Amazon Price Tracker...")
    print(f"Monitoring: {URL}")
    print(f"Target Price: ${TARGET_PRICE}")
    
    check_count = 0
    
    while True:
        check_count += 1
        print(f"\nCheck #{check_count} at {datetime.datetime.now()}")
        product_info = check_price()
        
        if product_info:
            price_data = {
                'title': product_info['title'],
                'price': product_info['price'],
                'price_text': product_info['price_text'],
                'url': URL
            }
            save_to_csv(price_data)
            
            if product_info['price'] <= TARGET_PRICE:
                print(f"Price dropped to ${product_info['price']}!")
                send_email(product_info, TARGET_PRICE)
                analyze_price_history()
                break
            else:
                print(f"Current price ${product_info['price']} is above target ${TARGET_PRICE}")
        else:
            print("Failed to get product information")
        
        if check_count % 24 == 0:
            analyze_price_history()
        
        print(f"Waiting {CHECK_INTERVAL/3600} hours before next check...")
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
    