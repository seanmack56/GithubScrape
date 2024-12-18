import requests
import json
import time
import csv

def search_repos(query, topic, language_searched, max_results=1000, filename="repo_info.csv", start_page=1, sort_by="stars", order="desc"):

    url = "https://api.github.com/search/repositories"
    headers = {"Authorization": f"token YOUR_TOKEN_HERE"}
    params = {"q": query, "per_page": 100, "page": start_page}

    with open(filename, 'a', newline='', encoding="utf-8") as csvfile:
        fieldnames = ['Repository', 'Description', 'URL', 'Stars', 'Forks', 'Topic', 'Language', 'SearchedBy', 'Order']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Only write the header if the file is empty
        if csvfile.tell() == 0:
            writer.writeheader() 


        page = start_page - 1  # Adjust for 1-based indexing in the API
        while True:
            page += 1
            params['page'] = page

            try:
                response = requests.get(url, headers=headers, params=params)
                response.raise_for_status()
                repos = response.json()["items"]

                if not repos:
                    break

                for repo in repos:
                    writer.writerow({
                        'Repository': repo['full_name'],
                        'Description': repo['description'],
                        'URL': repo['html_url'],
                        'Stars': repo['stargazers_count'],
                        'Forks': repo['forks_count'],
                        'Topic': topic,
                        'Language': language_searched,
                        'SearchedBy':  sort_by,
                        'Order': order
                    })

                if len(repos) < 100 or page * 100 >= max_results:
                    break

            except requests.exceptions.RequestException as e:
                print(f"Error fetching page {page}: {e}")
                if hasattr(e.response, 'status_code') and e.response.status_code == 422:
                        print(f"Unprocessable Entity error for page {page}. Skipping...")
                        continue  # Skip to the next page
                else:
                    # Implement exponential backoff with a maximum of 5 retries
                    max_retries = 5
                    retry_count = 0
                    if e.response.status_code == 403:
                        print("Authentication error. Check your PAT.")
                    while retry_count < max_retries:
                        delay = 30  # Adjust delay as needed
                        print(f"Retrying page {page} after {delay} seconds...")
                        time.sleep(delay)
                        try:
                            response = requests.get(url, headers=headers, params=params)
                            response.raise_for_status()
                            # Process the response as before
                            break
                        except requests.exceptions.RequestException as e:
                            print(f"Retry failed: {e}")
                            retry_count += 1
                    else:
                        print(f"Maximum retries reached for page {page}. Skipping...")
                        continue  # Skip to the next page

# Example usage:
topic = "YOUR TOPIC HERE"
language_searched = "python"
query = "language:python topic:YOUR_TOPIC_HERE"
start_page = 00  # Start from page 1
search_repos(query, topic, language_searched, max_results=1000, start_page=start_page)


"""
Topics Used for search
python - done by stars (desc + asc) and most recently updated (updated desc)
ai - done by stars (desc + asc) and most recently updated (updated desc)
scraper- done by stars (desc + asc) and most recently updated (updated desc)
crawler-done by stars (desc + asc) and most recently updated (updated desc)
web- done by stars (desc+asc) and most recently updated (updated desc)
framework - done by stars(desc+asc) and most recently updated (updated desc)


"""
