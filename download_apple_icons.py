import requests

from bs4 import BeautifulSoup

def fetch_apple_apps() -> list:
    iphone_specs_url = f"https://www.apple.com/iphone-15/specs/"
    print(f"Fetching apps for {iphone_specs_url}...")
    iphone_specs_response = requests.get(iphone_specs_url)
    print("Apps fetched with status code: " + str(iphone_specs_response.status_code))
    iphone_specs_soup = BeautifulSoup(iphone_specs_response.text, 'html.parser')
    app_name_components = iphone_specs_soup.find_all('figcaption', {'class': 'techspecs-appgrid-app-label'})
    app_names = [name_component.text.replace(u'\xa0', u' ') for name_component in app_name_components]
    print(app_names)
    return app_names

def search_app_by_name(app_name: str) -> dict:
    lookup_url = 'https://itunes.apple.com/search'
    params = {
        'term': app_name,
        'entity': 'software',
        'limit': 1
    }
    response = requests.get(lookup_url, params=params)
    if response.status_code == 200:
        results = response.json().get('results')
        if results and len(results) > 0:
            return results[0]
    return None

# function to download icon for app using result from search_app_by_name and save icon to apple_icons folder as <bundleId>.png
def download_icon_for_app(result: dict) -> str:
    print(f"Downloading icon for {result.get('bundleId')}...")
    icon_url = result.get('artworkUrl100')
    if icon_url:
        print(f"Icon URL: {icon_url}")
        icon_response = requests.get(icon_url)
        print("Icon downloaded with status code: " + str(icon_response.status_code))
        if icon_response.status_code == 200:
            file_name = f'{result.get("bundleId")}.png'
            with open(f'apple_icons/{file_name}', 'wb') as f:
                f.write(icon_response.content)
            print(f"Icon saved to apple_icons/{result.get('bundleId')}.png" + '\n')
            return file_name
    return None

def main():
    app_names = fetch_apple_apps()
    for app_name in app_names:
        result = search_app_by_name(app_name)
        if result:
            download_icon_for_app(result)

main()