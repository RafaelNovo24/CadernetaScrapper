import streamlit as st
from playwright.sync_api import sync_playwright
import os

CADERNETA_SITE = r"https://www.predialonline.pt/PredialOnline/FRM005RPOLCP_input.action"
BUILDING_CODE = "PA-3267-07514-131728-007612"

st.set_page_config(page_title="Document Scraper", page_icon="📂")

st.title("📂 Automated Document Downloader")
st.write("Enter the building code below to fetch the document.")

# 1. User Input
building_code = st.text_input(
    "Building Code (codigoCertidao):", placeholder="e.g., 12345678", value=BUILDING_CODE)

# 2. Execution Trigger
if st.button("Download Document"):
    if not building_code:
        st.warning("Please enter a valid code first.")
    else:
        # Use a status container to show progress
        with st.status("Initializing Scraper...", expanded=True) as status:
            try:
                with sync_playwright() as p:
                    # Headless=True is mandatory for hosting
                    browser = p.chromium.launch(
                        headless=True,
                        args=[
                            "--no-sandbox",
                            "--disable-dev-shm-usage",  # Mandatory for Docker
                            "--disable-gpu",           # Saves memory
                            "--disable-extensions",    # Saves memory
                            "--single-process"         # Optional: keeps memory usage in one thread
                        ]
                    )
                    context = browser.new_context()
                    page = context.new_page()

                    st.write("🌐 Accessing website...")
                    page.goto(CADERNETA_SITE)

                    st.write("📝 Entering code...")
                    page.fill("input[name='codigoCertidao']", building_code)

                    # --- Step 1: Validation ---
                    st.write("🔍 Validating...")
                    with page.expect_navigation(wait_until="networkidle"):
                        page.click("a[title='Validar Código']", force=True)

                    # --- Step 2: Continue ---
                    btn_continuar = page.locator("a[title='Continuar']")
                    if btn_continuar.is_visible():
                        st.write("⏩ Moving to next page...")
                        with page.expect_navigation(wait_until="networkidle"):
                            btn_continuar.click(force=True)

                        # --- Step 3: Final Download ---
                        btn_download = page.locator(
                            "a[title='Efetuar Download']")
                        if btn_download.is_visible():
                            st.write("⬇️ Generating PDF...")
                            with page.expect_download(timeout=20000) as dwn_inf:
                                btn_download.click(force=True)

                            download = dwn_inf.value
                            temp_path = f"./{download.suggested_filename}"
                            download.save_as(temp_path)

                            status.update(label="✅ Success!", state="complete")

                            # 3. Provide file to the user
                            with open(temp_path, "rb") as f:
                                st.download_button(
                                    label="💾 Save Document to My Computer",
                                    data=f,
                                    file_name=download.suggested_filename,
                                    mime="application/pdf"
                                )

                            # Clean up file from server memory
                            os.remove(temp_path)
                        else:
                            st.error(
                                "❌ The download link did not appear. Is the session valid?")
                    else:
                        st.error(
                            "❌ Validation failed. The code might be incorrect or the site is busy.")

                    browser.close()
            except Exception as e:
                st.error(f"🚨 Error: {str(e)}")

st.divider()
st.write("Made with ❤️ by Catarina & Rafael")
