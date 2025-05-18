# Main script to run the TikTok Email Harvester

import time
import random
from tiktok_harvester.scraper import (
    initialize_driver,
    close_driver,
    search_tiktok_videos,
    scroll_and_extract_video_data_via_js,
    scrape_profile_data # Changed from scrape_profile_bio
)
from tiktok_harvester.utils import extract_emails_from_text, write_to_csv

def main():
    print("Starting TikTok Email Harvester...")
    driver = None  # Initialize driver to None
    all_collected_data = []

    try:
        keywords_input = input("Enter TikTok search keyword(s), separated by commas: ")
        if not keywords_input.strip():
            print("No keywords provided. Exiting.")
            return
        
        keywords = [keyword.strip() for keyword in keywords_input.split(',')]

        proxy_to_use = None
        use_proxy_input = input("Do you want to use a proxy? (yes/no, default: no): ").strip().lower()
        if use_proxy_input == 'yes' or use_proxy_input == 'y':
            proxy_input_str = input("Enter proxy (e.g., 127.0.0.1:8080 or http://username:password@ip:port): ").strip()
            if proxy_input_str:
                proxy_to_use = proxy_input_str
            else:
                print("No proxy string entered. Proceeding without proxy.")
        
        driver = initialize_driver(proxy_string=proxy_to_use)
        if not driver:
            print("Failed to initialize WebDriver. Exiting.")
            return

        for keyword in keywords:
            print(f"\nProcessing keyword: '{keyword}'")
            
            if not search_tiktok_videos(driver, keyword): # Changed function call
                print(f"Failed to search for videos with keyword '{keyword}'. Skipping.")
                continue

            print(f"Successfully navigated to video search results for '{keyword}'.")
            print("Now executing JavaScript to scroll and extract video data (usernames, likes, video URLs)...")
            
            # Give the page a moment to settle before executing complex JS
            time.sleep(3)
            
            video_data_list = scroll_and_extract_video_data_via_js(driver)

            if not video_data_list:
                print(f"No video data extracted for keyword '{keyword}'. Skipping.")
                continue

            print(f"Found {len(video_data_list)} video data items for '{keyword}'. Now processing unique users from this data...")

            # Process unique usernames from the video data
            unique_usernames = set()
            users_to_process = []
            for video_item in video_data_list:
                # 'username' from JS is actually the creator's username
                creator_username = video_item.get('username')
                if creator_username and creator_username != 'N/A' and creator_username not in unique_usernames:
                    unique_usernames.add(creator_username)
                    users_to_process.append({
                        'username': creator_username,
                        'profile_url': f"https://www.tiktok.com/@{creator_username}",
                        # Optionally, carry over first video URL or like count if needed for CSV
                        'related_video_url': video_item.get('videoUrl', 'N/A'),
                        'related_video_likes': video_item.get('likeCount', 'N/A')
                    })
            
            if not users_to_process:
                print(f"No valid unique usernames found from video data for '{keyword}'.")
                continue

            print(f"Found {len(users_to_process)} unique users to process for bio scraping from keyword '{keyword}'.")

            for i, user_info in enumerate(users_to_process):
                username = user_info['username']
                profile_url = user_info['profile_url']
                
                print(f"\nProcessing user {i+1}/{len(users_to_process)}: {username} ({profile_url})")

                if not profile_url or username == 'N/A':
                    print(f"Skipping user '{username}' due to missing URL or invalid username.")
                    continue
                
                # Fixed delay before visiting profile.
                delay = 2 # Fixed 2-second delay
                print(f"Waiting for {delay} seconds before visiting profile...")
                time.sleep(delay)

                profile_page_data = scrape_profile_data(driver, profile_url)
                
                bio_text = "N/A"
                emails_found = []
                profile_following = "N/A"
                profile_followers = "N/A"
                profile_likes = "N/A"

                if profile_page_data:
                    bio_text = profile_page_data.get("bio_text", "N/A")
                    profile_following = profile_page_data.get("following_count", "N/A")
                    profile_followers = profile_page_data.get("followers_count", "N/A")
                    profile_likes = profile_page_data.get("likes_count", "N/A")

                    if bio_text and bio_text != "N/A":
                        emails_found = extract_emails_from_text(bio_text)
                        if emails_found:
                            print(f"Emails found for {username}: {', '.join(emails_found)}")
                        else:
                            print(f"No emails found in bio for {username}.")
                    else:
                        print(f"No bio text retrieved for {username}.")
                else:
                    print(f"Could not retrieve any profile page data for {username}.")
                
                all_collected_data.append({
                    'keyword_searched': keyword,
                    'username': username,
                    'profile_url': profile_url,
                    'source_video_url': user_info.get('related_video_url', 'N/A'),
                    'source_video_likes': user_info.get('related_video_likes', 'N/A'), # This is "like count (from video search)"
                    'bio_text': bio_text,
                    'emails_found': ', '.join(emails_found) if emails_found else "N/A", # This is "bioda mail varsa mail"
                    'profile_following_count': profile_following, # This is "takip edilen"
                    'profile_followers_count': profile_followers, # This is "takipçi"
                    'profile_likes_count': profile_likes # This is "beğeni sayısı (profile likes)"
                })
            
            print(f"Finished processing users derived from videos for keyword '{keyword}'.")

        if all_collected_data:
            output_filename = "tiktok_harvester/output/tiktok_user_data.csv" # Renamed for clarity
            headers = [
                'keyword_searched', 'username', 'profile_url',
                'source_video_url', 'source_video_likes',
                'bio_text', 'emails_found',
                'profile_following_count', 'profile_followers_count', 'profile_likes_count'
            ]
            write_to_csv(all_collected_data, filename=output_filename, headers=headers)
            print(f"\nAll processing complete. Data saved to {output_filename}")
        else:
            print("\nNo data collected from any keywords.")

    except KeyboardInterrupt:
        print("\nProcess interrupted by user (Ctrl+C).")
    except Exception as e:
        print(f"An unexpected error occurred in the main process: {e}")
    finally:
        if driver:
            print("Closing WebDriver...")
            close_driver(driver)
        print("TikTok Email Harvester finished.")

if __name__ == '__main__':
    main()