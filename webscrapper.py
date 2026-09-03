from playwright.sync_api import sync_playwright
CADERNETA_SITE = r"https://www.predialonline.pt/PredialOnline/FRM005RPOLCP_input.action"
BUILDING_CODE = "PP-3487-09722-131713-007612"
#   pyinstaller --onefile --windowed --add-data "env/Lib/site-packages/playwright/driver:playwright/driver" webscrapper.py


def get_certificate():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        page.goto(CADERNETA_SITE)

        page.fill("input[name='codigoCertidao']", BUILDING_CODE)

        with page.expect_navigation(wait_until="networkidle"):
            page.click("a[title='Validar Código']", force=True)

        with page.expect_navigation(wait_until="networkidle"):
            page.click("a[title='Continuar']", force=True)

        btn_download = page.locator("a[title='Efetuar Download']")
        if btn_download.is_visible():
            print("Final page reached. Starting download...")
            try:
                with page.expect_download(timeout=15000) as download_info:
                    # Trigger the JS submit for the download
                    btn_download.click(force=True)

                download = download_info.value
                path = "./caderneta.pdf"
                download.save_as(path)
                print(f"Success! File saved as: {path}")
            except Exception as e:
                print(f"Error during file download: {e}")
        else:
            print("Download link not found on the final page.")
        browser.close()



if __name__ == "__main__":
    get_certificate()
