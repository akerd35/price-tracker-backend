import asyncio
from curl_cffi.requests import AsyncSession
async def main():
    async with AsyncSession(impersonate='chrome110') as client:
        res = await client.get('https://www.vatanbilgisayar.com/hyperx-cloud-iii-s-kablosuz-kulak-ustu-oyuncu-kulakligi-kirmizi.html', timeout=30)
        with open('vatan_test.html', 'w', encoding='utf-8') as f:
            f.write(res.text)
        print('Vatan Length:', len(res.text))
asyncio.run(main())
