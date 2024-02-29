import requests
import time
import os
import re

from bs4 import BeautifulSoup

def read_country_codes() -> list:
    print("Reading country codes...")
    if os.path.exists('countries.json'):
        with open('countries.json', 'r') as f:
            country_codes = [entry['alpha_2'] for entry in eval(f.read())]
        print("Country codes read.")
        print("Total number of country codes: " + str(len(country_codes)))
        print(country_codes)
        return country_codes
    else:
        print("No country codes found.")
        return []
    
def fetch_app_ids_for_country(country_code: str) -> list:
    apps_url = f"https://apps.apple.com/{country_code}/charts/iphone/top-free-apps/36"
    print(f"Fetching apps for {country_code}...")
    apps_response = requests.get(apps_url)
    print("Apps fetched with status code: " + str(apps_response.status_code))
    apps_soup = BeautifulSoup(apps_response.text, 'html.parser')
    app_links = apps_soup.find_all('a', {'class': 'we-lockup targeted-link'}, href=True)
    app_ids = [re.search(r'/id(\d+)', link['href']).group(1) for link in app_links]
    print("Number of apps: " + str(len(app_ids)) + '\n')
    print(app_ids)
    return app_ids

def fetch_app_ids() -> list:
    country_codes = read_country_codes()
    app_ids = []
    for country_code in country_codes:
        app_ids.extend(fetch_app_ids_for_country(country_code))
    app_ids = list(set(app_ids))
    with open('app_ids.txt', 'w') as f:
        f.write('\n'.join(app_ids))
    return app_ids

def read_app_ids() -> list:
        if os.path.exists('app_ids.txt'):
            with open('app_ids.txt', 'r') as f:
                app_ids = f.read().splitlines()
            return app_ids
        else:
            return []

def fetch_app_info_for_app_id(app_id: str, trial_count: int) -> dict:
    lookup_url = 'https://itunes.apple.com/lookup'
    print(f"Fetching app info for {app_id}...")
    time.sleep(3)
    lookup_response = requests.get(lookup_url, params={'id': app_id})
    print("App info fetched with status code: " + str(lookup_response.status_code))
    if lookup_response.status_code == 200:
        results = lookup_response.json().get('results')
        if len(results) > 0:
            result = results[0]
            return result
        else:
            print("App not found.")
            return None
    else:
        if trial_count > 0:
            time.sleep(5)
            return fetch_app_info_for_app_id(app_id, trial_count - 1)
        else:
            return None

def download_icon_for_app(app_info: dict) -> str:
    print(f"Downloading icon for {app_info.get('bundleId')}...")
    icon_url = app_info.get('artworkUrl60')
    if icon_url:
        print(f"Icon URL: {icon_url}")
        icon_response = requests.get(icon_url)
        print("Icon downloaded with status code: " + str(icon_response.status_code))
        if icon_response.status_code == 200:
            file_name = f'{app_info.get("bundleId")}.png'
            with open(f'app_store_icons/{file_name}', 'wb') as f:
                f.write(icon_response.content)
            print(f"Icon saved to app_store_icons/{app_info.get('bundleId')}.png" + '\n')
            return file_name

def fetch_icon_for_app_id(app_id: str) -> str:
    app_info = fetch_app_info_for_app_id(app_id, 5)
    if app_info:
        return download_icon_for_app(app_info)
    else:
        print("App info not found.")
        return None
    
FETCH_ICONS_MODES = [
    'ALL_APP_IDS',
    'NEW_APP_IDS',
    'NOT_DOWNLOADED_APP_IDS'
]

def main():
    need_to_fetch_app_ids = True
    fetch_icons_mode = 'ALL_APP_IDS'

    saved_app_ids = read_app_ids()

    if need_to_fetch_app_ids:
        app_ids = fetch_app_ids()
    else:
        app_ids = saved_app_ids

    print("Total number of app ids: " + str(len(app_ids)))
    print('Total number of saved app ids: ' + str(len(saved_app_ids)))

    if os.path.exists('downloaded_app_ids.txt'):
        with open('downloaded_app_ids.txt', 'r') as f:
            downloaded_app_ids = f.read().splitlines()
    else:
        downloaded_app_ids = []

    print("Total number of downloaded app ids: " + str(len(downloaded_app_ids)))

    for app_id in app_ids:
        if fetch_icons_mode == 'ALL_APP_IDS' \
            or (app_id in saved_app_ids and fetch_icons_mode == 'NEW_APP_IDS')\
            or (app_id not in downloaded_app_ids and fetch_icons_mode == 'NOT_DOWNLOADED_APP_IDS'):
            file_name = fetch_icon_for_app_id(app_id)
            if file_name:
                downloaded_app_ids.append(app_id)
                with open('downloaded_app_ids.txt', 'w') as f:
                    f.write('\n'.join(downloaded_app_ids))

    print("Total number of downloaded icons: " + str(len(downloaded_app_ids)))
    print(downloaded_app_ids)

    not_downloaded_app_ids = set(app_ids) - set(downloaded_app_ids)
    print("Total number of not downloaded icons: " + str(len(app_ids) - len(downloaded_app_ids)))
    print(not_downloaded_app_ids)

    with open('not_downloaded_app_ids.txt', 'w') as f:
        for app_id in not_downloaded_app_ids:
            f.write(app_id + '\n')

main()