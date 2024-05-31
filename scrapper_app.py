import requests,os,time
from bs4 import BeautifulSoup

def scrape_page(url, max_retries=3):
    retries = 0
    while retries < max_retries:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            page_text = soup.get_text(separator=' ', strip=True)
            output_file = os.path.join("data",'data.txt')
            with open(output_file, "a") as file:
                file.write(f"{page_text}\n\n\n")
            print(f"Text content appended to {output_file.split('/')[-1]}")
            return  # Success, no need to retry
        else:
            print(f"Failed to retrieve the page. Status code: {response.status_code}")
            retries += 1
            print(f"Retrying ({retries}/{max_retries})...")
            time.sleep(2)  # Wait for 2 seconds before retrying
    print("Maximum retries exceeded. Failed to retrieve the page.")

def scrape_website(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        links = soup.find_all('a')
        for link in (links):
            href = link.get('href')
            scrape_page(href)
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")

# url = 'http://punjablaws.gov.pk/chron.php'
# scrape_website(url)