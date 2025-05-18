# Contains classes/functions for TikTok interaction
# e.g., browser management, CAPTCHA handling, scraping logic

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def initialize_driver(proxy_string=None):
    """
    Initializes and returns a Selenium WebDriver instance for Chrome.
    Optionally configures a proxy.
    proxy_string: e.g., 'ip:port' or 'http://ip:port'
    """
    chrome_options = Options()

    if proxy_string:
        if "://" not in proxy_string: # Ensure scheme for some proxy types, though Selenium often just needs ip:port for --proxy-server
            print(f"Proxy string '{proxy_string}' provided. Assuming http if no scheme specified for general use, but --proxy-server typically just needs ip:port.")
            # For --proxy-server, just ip:port is usually fine.
            # If using other methods like capabilities, a full URL might be needed.
        
        # Basic validation: check for colon, indicating ip:port
        if ':' not in proxy_string.split('://')[-1]: # Check part after scheme if present
             print(f"Warning: Proxy string '{proxy_string}' does not look like a valid ip:port. Attempting to use anyway.")

        chrome_options.add_argument(f'--proxy-server={proxy_string}')
        print(f"Attempting to use proxy: {proxy_string}")
    
    # Add any other desired options here, e.g.:
    # chrome_options.add_argument("--headless")
    # chrome_options.add_argument("--disable-gpu")
    # chrome_options.add_argument("--window-size=1920,1080")
    # chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")

    try:
        # Selenium 4's SeleniumManager should automatically handle driver download and setup
        # if no service or executable_path is specified.
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_script_timeout(120) # Set script timeout to 120 seconds
        print("WebDriver initialized successfully (using Selenium Manager, script timeout set to 120s).")
        return driver
    except Exception as e:
        print(f"Error initializing WebDriver: {e}")
        print("Please ensure Chrome is installed and accessible.")
        print("If issues persist, try updating Selenium: pip install --upgrade selenium")
        # The webdriver-manager specific message is less relevant now, but keeping it just in case.
        print("You might also check 'webdriver-manager' installation: pip install webdriver-manager")
        return None

def close_driver(driver):
    """Closes the WebDriver."""
    if driver:
        try:
            driver.quit()
            print("WebDriver closed successfully.")
        except Exception as e:
            print(f"Error closing WebDriver: {e}")

def handle_captcha(driver):
    """
    Pauses script execution to allow manual CAPTCHA solving.
    The driver instance is passed for potential future use (e.g., checking if CAPTCHA is resolved).
    """
    if not driver:
        print("Driver not available, cannot handle CAPTCHA.")
        return
    print("\n" + "="*50)
    print("CAPTCHA DETECTED!")
    print("Please solve the CAPTCHA in the browser window.")
    print("Press Enter in this console once you have solved it to continue...")
    print("="*50 + "\n")
    input() # Pauses the script
    print("Resuming script...")

def search_tiktok_videos(driver, keyword):
    """
    Navigates to the TikTok VIDEO search results page for the given keyword.
    """
    if not driver:
        print("Driver not available for searching.")
        return False

    # URL encode the keyword for safety
    from urllib.parse import quote
    search_url = f"https://www.tiktok.com/search/video?q={quote(keyword)}"
    print(f"Navigating to VIDEO search URL: {search_url}")

    try:
        driver.get(search_url)
        # Wait for a known element on the search results page to ensure it loads.
        # This also serves as an implicit CAPTCHA check point, as CAPTCHA might prevent this element from appearing.
        # Using a generic body tag for now, ideally, we'd find a more specific stable element.
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "body")) # Replace with a more specific selector for search results
        )
        print(f"Successfully navigated to search results for '{keyword}'.")
        
        # Basic CAPTCHA check: if a known CAPTCHA element is visible, or if the title suggests a CAPTCHA
        # This is a placeholder. A more robust CAPTCHA detection would be needed.
        # For example, looking for elements with 'captcha' in their ID/class, or specific text.
        # If you identify a common CAPTCHA element selector, it can be used here.
        # For now, we rely on the user to identify if a CAPTCHA page is shown and the script pauses at handle_captcha.
        # if "captcha" in driver.title.lower() or driver.find_elements(By.ID, "captcha-verify-image"): # Example
        #     print("Potential CAPTCHA detected on search page.")
        #     handle_captcha(driver)
        #     driver.get(search_url) # Re-navigate after CAPTCHA
        #     WebDriverWait(driver, 20).until(
        #         EC.presence_of_element_located((By.TAG_NAME, "body"))
        #     )

        return True
    except Exception as e:
        print(f"Error navigating to search results for '{keyword}': {e}")
        print("A CAPTCHA might be blocking the page, or the page structure might have changed.")
        print("Attempting to call handle_captcha as a fallback.")
        handle_captcha(driver) # Allow user to solve if it was a CAPTCHA
        # Optionally, try to re-navigate after manual CAPTCHA solve
        try:
            print(f"Re-attempting navigation to: {search_url}")
            driver.get(search_url)
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            print(f"Successfully navigated after CAPTCHA for '{keyword}'.")
            return True
        except Exception as e2:
            print(f"Still unable to navigate to search results for '{keyword}' after CAPTCHA attempt: {e2}")
            return False

def scroll_and_extract_video_data_via_js(driver):
    """
    Executes a JavaScript snippet to scroll the video search results page
    and extract video data (username, likeCount, videoUrl).
    """
    if not driver:
        print("Driver not available for executing JS.")
        return []

    print("Executing JavaScript to scroll and extract video data...")
    
    # User's JavaScript, modified to return results instead of downloading CSV
    # and to be more robust if elements are missing for a particular video.
    javascript_to_execute = """
    return (async function () {
        // "Başka sonuç yok" elementi göründüğünde duracak scroll fonksiyonu
        async function scrollUntilNoMoreResults(waitMs = 1000) { // Increased waitMs slightly
            let scrollCount = 0;
            const maxScrolls = 50; // Safety break for very long pages or if selector fails
            console.log('Starting scroll function...');
            while (!document.querySelector('.css-t7wus4-DivNoMoreResultsContainer.eegew6e3') && scrollCount < maxScrolls) {
                window.scrollTo(0, document.body.scrollHeight);
                console.log('Scrolled to bottom. Waiting ' + waitMs + 'ms...');
                await new Promise(res => setTimeout(res, waitMs));
                scrollCount++;
            }
            if (scrollCount >= maxScrolls) {
                console.log('Max scrolls reached, stopping scroll.');
            } else if (document.querySelector('.css-t7wus4-DivNoMoreResultsContainer.eegew6e3')) {
                console.log('"No more results" container found.');
            } else {
                console.log('Scroll loop finished for other reasons.');
            }
        }

        try {
            await scrollUntilNoMoreResults();
            console.log('Scrolling complete. Starting scrape operation...');
        } catch (scrollError) {
            console.error('Error during scrolling:', scrollError);
            // Optionally, allow manual scroll then proceed
            // alert('Automatic scrolling encountered an error. Please scroll manually to the end, then click OK.');
        }


        // Scrape işlemi
        // These selectors are based on the user's initial script. They might need updates.
        const userElements = document.querySelectorAll('p[data-e2e="search-card-user-unique-id"]');
        const likeElements = document.querySelectorAll('strong[data-e2e="video-views"]');
        // The videoLinkElements selector needs to be specific to the video card's main link
        // to ensure it aligns with userElements and likeElements.
        // A common structure is that the user element is within an <a> tag that is the main link for the card.
        // Let's try to get the href from the parent of the userElement if it's an 'a', or a known video link selector.
        // For now, using a broad selector for video links, assuming one per card.
        const videoCardLinks = document.querySelectorAll('a[href*="/video/"]'); // This might grab too many or too few.

        const results = [];
        console.log(`Found ${userElements.length} user elements, ${likeElements.length} like elements, ${videoCardLinks.length} video card links.`);

        // It's safer to iterate based on a common parent "card" element if possible.
        // For now, assuming userElements is the most reliable count for "video cards".
        userElements.forEach((userElement, index) => {
            try {
                const username = userElement.textContent.trim();
                const likeCount = likeElements[index] ? likeElements[index].textContent.trim() : 'N/A';
                
                let videoUrl = 'N/A';
                // Try to find the video URL associated with this user element.
                // This logic assumes the userElement is within a "card" that also contains the video link.
                let parentCard = userElement.closest('div[data-e2e="search-video-card"]'); // Example: if cards have this attr
                if (!parentCard) { // Fallback to a few levels up if specific card selector fails
                    parentCard = userElement.closest('div.tiktok-xpd1rf-DivContainer.e1yey0rl0'); // Example from inspecting a search page
                }


                if (parentCard) {
                    const videoLinkElement = parentCard.querySelector('a[href*="/video/"]');
                    if (videoLinkElement) {
                        videoUrl = videoLinkElement.href;
                    }
                } else if (videoCardLinks[index]) { // Less reliable fallback
                     videoUrl = videoCardLinks[index].href;
                }


                const urlMatch = videoUrl.match(/tiktok\\.com\\/@([^\\/]+)/);
                const usernameFromUrl = urlMatch ? urlMatch[1] : username; // Prefer username from URL if available

                results.push({
                    username: usernameFromUrl, // This is the creator's username
                    likeCount: likeCount,
                    videoUrl: videoUrl
                });
            } catch (e) {
                console.error('Error processing one item:', e, 'at index', index);
            }
        });
        
        console.log('Scraping complete. Results:', results.length);
        return results; // Return the data
    })();
    """
    
    try:
        extracted_data = driver.execute_script(javascript_to_execute)
        if extracted_data:
            print(f"JavaScript executed successfully, extracted {len(extracted_data)} items.")
        else:
            print("JavaScript executed, but no data was returned or data is empty.")
            # This could happen if the JS itself had an error before returning, or found nothing.
            # Check browser console for JS errors.
        return extracted_data if extracted_data else []
    except Exception as e:
        print(f"Error executing JavaScript for data extraction: {e}")
        print("This could be due to a page error, CAPTCHA, or an issue in the JS itself.")
        print("Check the browser's developer console for JavaScript errors.")
        print("Attempting CAPTCHA handling and retrying JS execution...")
        handle_captcha(driver) # Offer to solve CAPTCHA
        
        # Retry JS execution after CAPTCHA
        print("Retrying JavaScript execution after CAPTCHA attempt...")
        try:
            # It might be beneficial to refresh the page or re-navigate if CAPTCHA fundamentally changed the page state
            # driver.refresh()
            # time.sleep(3) # Wait for refresh
            
            extracted_data_retry = driver.execute_script(javascript_to_execute)
            if extracted_data_retry:
                print(f"JavaScript re-executed successfully after CAPTCHA, extracted {len(extracted_data_retry)} items.")
            else:
                print("JavaScript re-executed after CAPTCHA, but no data was returned or data is empty.")
            return extracted_data_retry if extracted_data_retry else []
        except Exception as e_retry:
            print(f"Error during JavaScript re-execution after CAPTCHA: {e_retry}")
            print("Failed to extract data even after CAPTCHA handling and retry.")
            return []


def scrape_profile_data(driver, profile_url,
                        bio_selector="h2[data-e2e=\"user-bio\"].css-cm3m4u-H2ShareDesc.e1457k4r3",
                        following_selector="strong[data-e2e=\"following-count\"]",
                        followers_selector="strong[data-e2e=\"followers-count\"]",
                        likes_selector="strong[data-e2e=\"likes-count\"]"):
    """
    Navigates to a user's profile URL and scrapes their bio, following, followers, and likes count.
    Returns a dictionary with the scraped data.
    """
    if not driver:
        print("Driver not available for scraping profile data.")
        return {
            "bio_text": "N/A (Driver error)",
            "following_count": "N/A",
            "followers_count": "N/A",
            "likes_count": "N/A"
        }
    
    profile_data = {
        "bio_text": "N/A",
        "following_count": "N/A",
        "followers_count": "N/A",
        "likes_count": "N/A"
    }
    
    print(f"Navigating to profile: {profile_url}")
    try:
        driver.get(profile_url)
        # Wait for a general profile element to ensure page is somewhat loaded.
        # Waiting for the bio element as a primary indicator.
        # If bio selector is too specific and sometimes missing, can wait for a more general parent.
        # For example, the container of the like/follower counts: h3.css-1xoqgj7-H3CountInfos
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h3.css-1xoqgj7-H3CountInfos.e1457k4r0")) # Wait for counts container
        )
        
        # Scrape Bio
        try:
            bio_element = driver.find_element(By.CSS_SELECTOR, bio_selector)
            profile_data["bio_text"] = bio_element.text.strip()
            print(f"Bio found: '{profile_data['bio_text'][:100]}...'")
        except Exception as e_bio:
            print(f"Could not find or scrape bio using selector '{bio_selector}': {e_bio}")

        # Scrape Following Count
        try:
            following_element = driver.find_element(By.CSS_SELECTOR, following_selector)
            profile_data["following_count"] = following_element.text.strip()
            print(f"Following count: {profile_data['following_count']}")
        except Exception as e_following:
            print(f"Could not find or scrape following count using selector '{following_selector}': {e_following}")

        # Scrape Followers Count
        try:
            followers_element = driver.find_element(By.CSS_SELECTOR, followers_selector)
            profile_data["followers_count"] = followers_element.text.strip()
            print(f"Followers count: {profile_data['followers_count']}")
        except Exception as e_followers:
            print(f"Could not find or scrape followers count using selector '{followers_selector}': {e_followers}")

        # Scrape Likes Count
        try:
            likes_element = driver.find_element(By.CSS_SELECTOR, likes_selector)
            profile_data["likes_count"] = likes_element.text.strip()
            print(f"Likes count: {profile_data['likes_count']}")
        except Exception as e_likes:
            print(f"Could not find or scrape likes count using selector '{likes_selector}': {e_likes}")
            
        return profile_data

    except Exception as e:
        print(f"Error navigating to or scraping main data from {profile_url}: {e}")
        print("A CAPTCHA might be blocking the page, or essential elements are not found.")
        handle_captcha(driver) # Allow user to solve if it was a CAPTCHA
        
        # Retry scraping after CAPTCHA
        print(f"Re-attempting to scrape data from: {profile_url} after CAPTCHA")
        try:
            # driver.get(profile_url) # Re-navigate if necessary, or assume user handled it.
            # Ensure page is in a good state, maybe wait for a known element again
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h3.css-1xoqgj7-H3CountInfos.e1457k4r0"))
            )
            
            # Retry Scrape Bio
            try:
                bio_element = driver.find_element(By.CSS_SELECTOR, bio_selector)
                profile_data["bio_text"] = bio_element.text.strip()
            except: pass
            # Retry Scrape Following
            try:
                following_element = driver.find_element(By.CSS_SELECTOR, following_selector)
                profile_data["following_count"] = following_element.text.strip()
            except: pass
            # Retry Scrape Followers
            try:
                followers_element = driver.find_element(By.CSS_SELECTOR, followers_selector)
                profile_data["followers_count"] = followers_element.text.strip()
            except: pass
            # Retry Scrape Likes
            try:
                likes_element = driver.find_element(By.CSS_SELECTOR, likes_selector)
                profile_data["likes_count"] = likes_element.text.strip()
            except: pass
            
            print(f"Data scraped after CAPTCHA attempt: Bio='{profile_data['bio_text'][:50]}...', Following='{profile_data['following_count']}', Followers='{profile_data['followers_count']}', Likes='{profile_data['likes_count']}'")
            return profile_data
        except Exception as e_retry:
            print(f"Still unable to scrape data from {profile_url} on retry: {e_retry}")
            return profile_data

if __name__ == '__main__':
    # Example usage (for testing this module directly)
    test_driver = initialize_driver()
    if test_driver:
        try:
            print("Navigating to TikTok for initial test...")
            test_driver.get("https://www.tiktok.com")
            print("If a CAPTCHA appears on the main page, solve it now, then press Enter here.")
            handle_captcha(test_driver) # Allow solving initial CAPTCHA

            print("\nTesting VIDEO search and JS extraction functionality...")
            keyword_to_test = "manifesting app" # Use the user's example keyword
            
            if search_tiktok_videos(test_driver, keyword_to_test):
                print(f"Video search navigation for '{keyword_to_test}' successful.")
                print("Attempting to scroll and extract data via JavaScript...")
                
                # Give the page a moment to settle before executing complex JS
                time.sleep(3)
                
                video_data_list = scroll_and_extract_video_data_via_js(test_driver)
                
                if video_data_list:
                    print(f"\nSuccessfully extracted {len(video_data_list)} video data items:")
                    for item in video_data_list[:3]: # Print first 3
                        print(f"  - User: {item['username']}, Likes: {item['likeCount']}, Video: {item['videoUrl']}")
                    
                    # Test scraping bio for the first unique username from video data
                    if video_data_list:
                        first_video_creator_username = video_data_list[0]['username']
                        if first_video_creator_username and first_video_creator_username != 'N/A':
                            profile_url_to_test = f"https://www.tiktok.com/@{first_video_creator_username}"
                            print(f"\nAttempting to scrape profile data for user: {first_video_creator_username} ({profile_url_to_test})")
                            scraped_profile_info = scrape_profile_data(test_driver, profile_url_to_test)
                            if scraped_profile_info:
                                print(f"Successfully scraped profile data:")
                                print(f"  Bio: {scraped_profile_info.get('bio_text', 'N/A')[:100]}...")
                                print(f"  Following: {scraped_profile_info.get('following_count', 'N/A')}")
                                print(f"  Followers: {scraped_profile_info.get('followers_count', 'N/A')}")
                                print(f"  Likes: {scraped_profile_info.get('likes_count', 'N/A')}")
                            else: # Should not happen if scrape_profile_data always returns a dict
                                print(f"Failed to scrape profile data for {profile_url_to_test} (returned None).")
                        else:
                            print("First video item did not have a valid username to test profile data scraping.")
                else:
                    print("No video data was extracted by the JavaScript. Check JS selectors and browser console for errors.")
            else:
                print(f"Video search navigation for '{keyword_to_test}' failed.")
            
            print("\nTest script will keep the browser open for 20 seconds for inspection...")
            time.sleep(20)

        except Exception as e:
            print(f"An error occurred during testing: {e}")
        finally:
            close_driver(test_driver)
    else:
        print("Failed to initialize driver for testing.")