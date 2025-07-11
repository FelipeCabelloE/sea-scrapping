import duckdb
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bs4 import BeautifulSoup
import logging
from rich.logging import RichHandler

# Setup logging
logging.basicConfig(
    format="{asctime} [{levelname}] {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
    handlers=[RichHandler()],
)

log = logging.getLogger("rich")

MONGO_LINK = "mongodb://root:example@localhost:27017/?authSource=admin"
MONDB_NAME = "SCRAPED_SEA"
MONCOL_NAME = "proyects_1738092411"  # Replace <timestamp> with the actual timestamp used in 03_mongo_async_scrapper.py

client = AsyncIOMotorClient(MONGO_LINK)
db = client[MONDB_NAME]
collection = db[MONCOL_NAME]


async def fetch_documents():
    documents = []
    async for document in collection.find():
        documents.append(document)
    return documents

def parse_document(document):
    soup = BeautifulSoup(document["content"], "html.parser")
    project_name = soup.find("td", string="Proyecto").find_next_sibling("td").text.strip()
    project_type = soup.find("td", string="Tipo de Proyecto").find_next_sibling("td").text.strip()
    investment_amount = soup.find("td", string="Monto de Inversión").find_next_sibling("td").text.strip()
    current_status = soup.find("td", string="Estado Actual").find_next_sibling("td").text.strip()
    description = soup.find("td", string="Descripción del Proyecto").find_next_sibling("td").text.strip()

    # Extract <h2> elements that start with "Forma de Presentaci"
    forma_presentacion = [
        h2.get_text(strip=True) for h2 in soup.find_all("h2") if h2.get_text(strip=True).startswith("Forma de Presentaci")
    ]

    return {
        "url": document["url"],
        "project_name": project_name,
        "project_type": project_type,
        "investment_amount": investment_amount,
        "current_status": current_status,
        "description": description,
        "forma_presentacion": forma_presentacion,
    }

async def parse_documents(documents):
    loop = asyncio.get_event_loop()
    tasks = [loop.run_in_executor(None, parse_document, doc) for doc in documents]
    return await asyncio.gather(*tasks)

async def main():
    log.info("Starting to fetch documents from MongoDB")
    documents = await fetch_documents()
    log.info(f"Fetched {len(documents)} documents")

    parsed_data = await parse_documents(documents)

    db_file = 'projects.duckdb'
    conn = duckdb.connect(db_file)
    log.info(f"Connected to DuckDB database at {db_file}")

    conn.execute('''
        CREATE TABLE projects (
            url VARCHAR,
            project_name VARCHAR,
            project_type VARCHAR,
            investment_amount VARCHAR,
            current_status VARCHAR,
            description VARCHAR,
            forma_presentacion VARCHAR
        )
    ''')
    log.info("Created table 'projects' in DuckDB")

    for data in parsed_data:
        try:
            conn.execute('''
                INSERT INTO projects (url, project_name, project_type, investment_amount, current_status, description, forma_presentacion)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                str(data['url']),
                str(data['project_name']),
                str(data['project_type']),
                str(data['investment_amount']),
                str(data['current_status']),
                str(data['description']),
                str(data['forma_presentacion'])
            ))
        except Exception as e:
            log.error(f"Error inserting data: {data}")
            log.error(f"Exception: {e}")

    log.info("Inserted parsed data into DuckDB")
    conn.close()
    log.info("Closed DuckDB connection")

if __name__ == "__main__":
    try:
        asyncio.run(main())
        log.info("Completed successfully")
    except Exception as e:
        log.error(f"An error occurred: {e}")
