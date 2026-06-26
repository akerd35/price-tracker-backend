import asyncio
from curl_cffi.requests import AsyncSession
from bs4 import BeautifulSoup

async def main():
    url = "https://www.vatanbilgisayar.com/hyperx-cloud-iii-s-kablosuz-kulak-ustu-oyuncu-kulakligi-kirmizi.html"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9,tr-TR;q=0.8,tr;q=0.7",
    }
    async with AsyncSession(impersonate='chrome110') as client:
        try:
            response = await client.get(url, headers=headers)
            print("Status:", response.status_code)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                title = soup.title.get_text() if soup.title else "No title"
                print("Title:", title)
                price = soup.find("meta", property="product:price:amount")
                print("Price:", price["content"] if price else "No price meta")
        except Exception as e:
            print("Error:", e)

asyncio.run(main())
