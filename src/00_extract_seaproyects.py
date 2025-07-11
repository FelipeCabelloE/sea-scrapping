import asyncio
import subprocess
from pathlib import Path

from playwright.async_api import (
    async_playwright,
)
from rich import print


async def main():
    print("Hello from sea-scrapping!")
    if not Path("./DATA").exists():
        Path.mkdir("./DATA")
    await get_and_convert_proyects()


async def get_and_convert_proyects():
    async with async_playwright() as playwright:
        chromium = playwright.chromium
        browser = await chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto("https://seia.sea.gob.cl/busqueda/buscarProyecto.php")
        boton_buscar = "div.centrar-boton > button.bot_70px"
        await page.wait_for_selector(boton_buscar)
        await page.click(boton_buscar)
        kmz_link = 'a[href="/mapa/generarKMZ.php?validado=0"]'
        await page.wait_for_selector(kmz_link)
        async with page.expect_download(timeout=0) as download_info:
            await page.click(kmz_link)
        download = await download_info.value
        await download.save_as(f"./DATA/{download.suggested_filename}")
        try:

            def transform_to_gpkg(args):
                options = ["/usr/bin/ogr2ogr"]
                options.extend(args)
                subprocess.check_call(options, stderr=subprocess.STDOUT)

            transform_to_gpkg(
                [
                    f"./DATA/{Path(download.suggested_filename).stem}.gpkg",
                    f"./DATA/{download.suggested_filename}",
                ]
            )
        except subprocess.CalledProcessError as e:
            print(str(e.output))


if __name__ == "__main__":
    asyncio.run(main())
