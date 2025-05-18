# TikTok Profile Crawler

This Python script automates the process of searching TikTok for videos based on keywords, extracting creator profile information from those videos, and then visiting those profiles to scrape bios, email addresses (if present), and other public metrics like follower, following, and like counts.

The script uses Selenium for browser automation and allows for optional proxy configuration.

## Features

*   Searches TikTok for videos based on user-provided keywords.
*   Scrolls through video search results using a JavaScript snippet to load more content.
*   Extracts video creator usernames, video like counts, and video URLs.
*   Visits individual creator profile pages.
*   Scrapes the following data from profile pages:
    *   Bio text
    *   Emails found in the bio
    *   Following count
    *   Followers count
    *   Profile likes count
*   Handles CAPTCHAs by pausing and allowing manual user intervention.
*   Supports optional proxy usage (IP:PORT).
*   Saves all collected data into a CSV file in the `tiktok_harvester/output/` directory.

## Project Structure

```
tiktokmail/
├── tiktok_harvester/
│   ├── __init__.py
│   ├── main.py         # Main script to run the crawler
│   ├── scraper.py      # Core Selenium scraping logic
│   ├── utils.py        # Helper functions (email extraction, CSV writing)
│   └── output/         # Directory for CSV results
│       └── .gitkeep
├── requirements.txt    # Python dependencies
├── tiktok_harvester_plan.md # Original planning document
└── README.md           # This file
```

## Setup and Installation

1.  **Clone the repository (or download the files):**
    ```bash
    # If you've pushed it to GitHub:
    # git clone https://github.com/tcaslan/tiktok-profile-crawler.git
    # cd tiktok-profile-crawler
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    Ensure you have Google Chrome installed on your system.
    ```bash
    pip install -r requirements.txt
    ```

## How to Run

1.  Navigate to the project's root directory (`tiktokmail`).
2.  Run the main script:
    ```bash
    python -m tiktok_harvester.main
    ```
3.  **Enter Keywords:** The script will prompt you to enter TikTok search keywords, separated by commas (e.g., `tech, programming, ai`).
4.  **Proxy (Optional):** It will then ask if you want to use a proxy. If yes, provide the proxy string (e.g., `127.0.0.1:8080`).
5.  **CAPTCHA Handling:** If TikTok presents a CAPTCHA, the script will pause and print a message in the console. You need to manually solve the CAPTCHA in the browser window that Selenium opened. Once solved, press Enter in the console to continue.
6.  **Output:** The collected data will be saved in a CSV file (e.g., `tiktok_user_data.csv`) inside the `tiktok_harvester/output/` directory.

## Important Notes

*   **Selectors:** TikTok's website HTML structure can change frequently. If the script fails to find elements or extract data, the CSS selectors in `tiktok_harvester/scraper.py` (for video data extraction via JavaScript and profile page scraping) may need to be updated. Check the browser's developer console for JavaScript errors.
*   **Rate Limiting/Blocking:** Web scraping can lead to IP blocking or more frequent CAPTCHAs. The script includes random delays, but use responsibly. Proxies can help mitigate this.
*   **Ethical Considerations:** Always ensure your use of this tool complies with TikTok's Terms of Service and applicable laws and regulations regarding data collection and privacy.

## Disclaimer
This tool is for educational and research purposes only. The developers are not responsible for any misuse of this tool.