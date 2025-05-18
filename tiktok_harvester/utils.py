# Helper functions for the TikTok Harvester
# e.g., CSV writing, email extraction

import re
import csv
import os

def extract_emails_from_text(text):
    """
    Extracts email addresses from a given string using a regular expression.
    Returns a list of unique email addresses found.
    """
    if not text:
        return []
    # Regex to find most common email formats
    email_regex = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    emails = re.findall(email_regex, text)
    # Return unique emails, preserving order of first appearance
    unique_emails = []
    seen_emails = set()
    for email in emails:
        if email.lower() not in seen_emails:
            unique_emails.append(email)
            seen_emails.add(email.lower())
    return unique_emails

def write_to_csv(data_rows, filename="tiktok_harvester/output/tiktok_emails.csv", headers=None):
    """
    Writes a list of dictionaries (data_rows) to a CSV file.
    Each dictionary in data_rows should represent a row.
    If headers are not provided, the keys of the first dictionary in data_rows will be used.
    """
    if not data_rows:
        print("No data to write to CSV.")
        return

    if headers is None:
        headers = data_rows[0].keys()

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data_rows)
        print(f"Data successfully written to {filename}")
    except Exception as e:
        print(f"Error writing to CSV file {filename}: {e}")

if __name__ == '__main__':
    # Example usage for extract_emails_from_text
    sample_bio_text = """
    Hello, I am a content creator. Contact me at myemail@example.com for collabs.
    You can also reach out to business.email@company.co.uk or MyEmail@Example.com.
    Sometimes people write email at domain dot com or use (at) instead of @.
    Another one: test-email_123@sub.domain.info.
    Invalid: user@localhost, user@.com, @domain.com
    """
    found_emails = extract_emails_from_text(sample_bio_text)
    print(f"Emails found in sample bio: {found_emails}") # Expected: ['myemail@example.com', 'business.email@company.co.uk', 'test-email_123@sub.domain.info']

    # Example usage for write_to_csv
    sample_data = [
        {'username': 'user1', 'profile_url': 'url1', 'email': 'user1@example.com'},
        {'username': 'user2', 'profile_url': 'url2', 'email': 'user2@example.com, another@example.net'},
        {'username': 'user3', 'profile_url': 'url3', 'email': ''} # No email found
    ]
    output_dir = "tiktok_harvester/output/"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Test with default filename (will create output/tiktok_emails.csv relative to where script is run)
    # For this test, let's make it explicitly inside the project structure
    project_output_filename = os.path.join(os.path.dirname(__file__), "output/test_tiktok_emails.csv")
    
    # If running utils.py directly, __file__ is tiktok_harvester/utils.py
    # So, os.path.dirname(__file__) is tiktok_harvester
    # And project_output_filename becomes tiktok_harvester/output/test_tiktok_emails.csv
    
    write_to_csv(sample_data, filename=project_output_filename, headers=['username', 'profile_url', 'email'])
    print(f"Sample CSV written to {project_output_filename} (if successful).")

    # Test with no headers (infer from data)
    project_output_filename_inferred = os.path.join(os.path.dirname(__file__), "output/test_tiktok_emails_inferred.csv")
    write_to_csv(sample_data, filename=project_output_filename_inferred)
    print(f"Sample CSV with inferred headers written to {project_output_filename_inferred} (if successful).")