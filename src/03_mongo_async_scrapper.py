import asyncio
from curl_cffi.requests import AsyncSession
import logging
from rich.logging import RichHandler
import time
from motor.motor_asyncio import AsyncIOMotorClient
import geopandas as gpd
from datetime import datetime

MONGO_LINK = "mongodb://root:example@localhost:27017/?authSource=admin"
MONDB_NAME = "SCRAPED_SEA"
MONCOL_NAME = f"proyects_{int(time.time())}"

client = AsyncIOMotorClient(MONGO_LINK)
db = client[MONDB_NAME]
collection = db[MONCOL_NAME]

start_time = time.time()

logging.basicConfig(
    format="{asctime} [{levelname}] {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
    handlers=[RichHandler()],
)

log = logging.getLogger("rich")

proyects = gpd.read_file("./DATA/proyectos_cleaned.gpkg")
urls = proyects["constructed_link"].tolist()

CONCURRENT_REQUESTS = 100
RETRY_LIMIT = 3

semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)
failed_urls = []


async def fetch(session, url):
    for attempt in range(RETRY_LIMIT):
        try:
            async with semaphore:
                response = await session.get(url, timeout=10)
                response.raise_for_status()
                return response
        except Exception as e:
            log.error(f"Error fetching {url}: {e}")
            if attempt < RETRY_LIMIT - 1:
                log.info(f"Retrying {url} (attempt {attempt + 1})")
                await asyncio.sleep(2**attempt)
            else:
                log.error(f"Failed to fetch {url} after {RETRY_LIMIT} attempts")
                failed_urls.append(url)
                return None


async def save_to_db(response):
    if response and response.status_code == 200:
        document = {
            "url": response.url,
            "date": datetime.now(),
            "content": response.text,
        }
        await collection.insert_one(document)
        log.info(f"Inserted document for {response.url}")


async def process_urls(urls):
    async with AsyncSession() as session:
        tasks = [fetch(session, url) for url in urls]
        for task in asyncio.as_completed(tasks):
            response = await task
            await save_to_db(response)


async def retry_failed_urls():
    if failed_urls:
        log.info(f"Retrying {len(failed_urls)} failed URLs")
        await process_urls(failed_urls)


async def run():
    await process_urls(urls)
    await retry_failed_urls()


if __name__ == "__main__":
    asyncio.run(run())
    log.info(f"Completed in {time.time() - start_time} seconds")
