# Project Plan: TikTok Email Harvester

**Objective:** To automate the process of searching TikTok for content creators based on keywords (using direct user search), visiting their profiles, and extracting email addresses from their bios, saving the results to a CSV file. The script will use Selenium and pause for manual CAPTCHA resolution.

**Core Technologies:**

*   **Language:** Python
*   **Browser Automation:** Selenium
*   **Web Driver:** ChromeDriver (managed by `webdriver-manager`)
*   **Data Handling:** Python's built-in `csv` module.
*   **Email Parsing:** Python's `re` module (for regular expressions).

**Detailed Plan:**

**Phase 1: Setup and Foundational Browser Automation**

1.  **Project Structure:**
    *   `tiktok_harvester/`
        *   `main.py` (Main script to run the process)
        *   `scraper.py` (Contains classes/functions for TikTok interaction)
        *   `utils.py` (Helper functions, e.g., CSV writing, config loading)
        *   `config.ini` (Optional: for settings like timeouts, output file name)
        *   `requirements.txt` (Python dependencies)
        *   `output/` (Directory to store CSV results)
2.  **Environment Setup:**
    *   Create `requirements.txt`:
        ```
        selenium
        webdriver-manager
        ```
    *   User instruction: `pip install -r requirements.txt`
3.  **Browser Manager (`scraper.py`):**
    *   Function to initialize and return a Selenium WebDriver instance (e.g., Chrome).
    *   Function to close the browser.
4.  **CAPTCHA Handling Mechanism (`scraper.py`):**
    *   Function `handle_captcha(driver)`:
        *   Prints: "CAPTCHA detected. Please solve it in the browser window. Press Enter in this console when done."
        *   Uses `input()` to pause script execution.

**Phase 2: TikTok Search and Initial Data Collection**

1.  **Search Function (`scraper.py`):**
    *   Function `search_tiktok_users(driver, keyword)`:
        *   Constructs the search URL: `https://www.tiktok.com/search/user?q={keyword}`.
        *   Navigates to the URL.
        *   Implement CAPTCHA check and call `handle_captcha` if needed.
2.  **Dynamic Scrolling (`scraper.py`):**
    *   Function `scroll_to_bottom_users(driver)`:
        *   Injects and executes JavaScript to scroll the page.
        *   Loop condition based on detecting a "no more results" element or similar.
        *   Include `try-except` blocks for CAPTCHA during scroll.
        *   Add a maximum scroll limit/timeout.
3.  **Search Results Extraction (`scraper.py`):**
    *   Function `extract_user_search_results(driver)`:
        *   Uses Selenium to find usernames and profile links.
        *   Stores results as `[{'username': 'user1', 'profile_url': 'http://tiktok.com/@user1'}, ...]`.
        *   Return this list.

**Phase 3: Profile Visiting and Email Scraping**

1.  **Profile Visit and Bio Scraping (`scraper.py`):**
    *   Function `scrape_profile_bio(driver, profile_url)`:
        *   Navigates to `profile_url`.
        *   Check for CAPTCHA.
        *   Locates bio element: `h2[data-e2e="user-bio"].css-cm3m4u-H2ShareDesc.e1457k4r3`.
        *   Extracts bio text.
        *   Return bio text.
2.  **Email Extraction (`utils.py` or `scraper.py`):**
    *   Function `extract_emails_from_text(text)`:
        *   Uses regex: `r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"`
        *   Returns a list of found emails.

**Phase 4: Orchestration and Output**

1.  **CSV Handling (`utils.py`):**
    *   Function `write_to_csv(data, filename="output/tiktok_emails.csv")`:
        *   Writes `[{'username': ..., 'profile_url': ..., 'email': ...}]` to CSV.
        *   Headers: `Username,Profile URL,Email`.
2.  **Main Script Logic (`main.py`):**
    *   Initialize WebDriver.
    *   Prompt for search keyword(s).
    *   Loop through keywords:
        *   `search_tiktok_users()`
        *   `scroll_to_bottom_users()`
        *   `extract_user_search_results()`
        *   Loop through profiles:
            *   `scrape_profile_bio()`
            *   `extract_emails_from_text()`
            *   Aggregate data.
            *   Implement delays.
    *   `write_to_csv()`.
    *   Close WebDriver.
    *   Error handling.

**Workflow Diagram (Mermaid):**

```mermaid
graph TD
    A[Start] --> B[User Inputs Keyword(s)];
    B --> C[Initialize Selenium WebDriver];
    C --> D{For each Keyword};
    D --> E[Direct User Search on TikTok: scraper.search_tiktok_users];
    E --> F{CAPTCHA?};
    F -- Yes --> G[scraper.handle_captcha];
    G --> E;
    F -- No --> H[Scroll Page for Users: scraper.scroll_to_bottom_users];
    H --> I{CAPTCHA during scroll?};
    I -- Yes --> J[scraper.handle_captcha];
    J --> H;
    I -- No --> K[Extract User Profiles: scraper.extract_user_search_results];
    K --> L{For each Profile URL};
    L --> M[Visit Profile: scraper.scrape_profile_bio];
    M --> N{CAPTCHA?};
    N -- Yes --> O[scraper.handle_captcha];
    O --> M;
    N -- No --> P[Extract Bio Text];
    P --> Q[Extract Emails: utils.extract_emails_from_text];
    Q --> R[Store User Data (Username, Profile URL, Email)];
    R --> S{More Profiles for Keyword?};
    S -- Yes --> L;
    S -- No --> T{More Keywords?};
    T -- Yes --> D;
    T -- No --> U[Write All Data to CSV: utils.write_to_csv];
    U --> V[Close WebDriver];
    V --> W[End];