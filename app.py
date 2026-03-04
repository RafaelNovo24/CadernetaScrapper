import base64

import streamlit as st
from playwright.sync_api import sync_playwright
import subprocess
import sys
import os

CADERNETA_SITE = r"https://www.predialonline.pt/PredialOnline/FRM005RPOLCP_input.action"
BUILDING_CODE = "PA-3267-07514-131728-007612"


@st.cache_resource
def install_playwright():
    """Installs the Chromium browser for Playwright on first boot."""
    subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"])


install_playwright()

st.set_page_config(
    page_title="Download Automático da Caderneta Predial",
    page_icon="asset/logo.png")


st.title("Download Automático da Caderneta Predial")
st.write("Insira o código da caderneta predial para baixar o documento em PDF diretamente do site oficial.")

# User input for the building code
building_code = st.text_input(
    "Código da Caderneta Predial:", placeholder="e.g., 12345678", value=BUILDING_CODE)

# Button to trigger the download process
if st.button("Download Documento"):
    if not building_code:
        st.warning("Por favor, insira um código válido primeiro.")
    else:
        # Use a status container to show progress
        with st.status("Inicializando o Scraper...", expanded=True) as status:
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

                    st.write("🌐 Acessando o site...")
                    page.goto(CADERNETA_SITE)

                    st.write("📝 Inserindo código...")
                    page.fill("input[name='codigoCertidao']", building_code)

                    # Validate code and navigate to the next page
                    st.write("🔍 A validar código...")
                    with page.expect_navigation(wait_until="networkidle"):
                        page.click("a[title='Validar Código']", force=True)

                    # Moving to download
                    btn_continuar = page.locator("a[title='Continuar']")
                    if btn_continuar.is_visible():
                        st.write("⏩ A avançar para a página de download...")
                        with page.expect_navigation(wait_until="networkidle"):
                            btn_continuar.click(force=True)

                        # Download the PDF
                        btn_download = page.locator(
                            "a[title='Efetuar Download']")
                        if btn_download.is_visible():
                            st.write("⬇️ A fazer download do PDF...")
                            with page.expect_download(timeout=20000) as dwn_inf:
                                btn_download.click(force=True)

                            download = dwn_inf.value
                            temp_path = f"./{download.suggested_filename}"
                            download.save_as(temp_path)

                            status.update(label="✅ Sucesso!",
                                          state="complete", expanded=True)

                            # 3. Provide file to the user
                            with open(temp_path, "rb") as f:
                                st.download_button(
                                    label="💾 Guardar documento localmente",
                                    data=f,
                                    file_name=download.suggested_filename,
                                    mime="application/pdf"
                                )

                            # Clean up file from server memory
                            os.remove(temp_path)
                        else:
                            st.error(
                                "❌ O link de download não apareceu. A sessão é válida?")
                    else:
                        st.error(
                            "❌ A validação falhou. O código pode estar incorreto ou o site está ocupado.")

                    browser.close()
            except Exception as e:
                st.error(f"🚨 Erro: {str(e)}")


st.divider()
# st.write("© 2026 Rafael Novo. All rights reserved.")

# Footnote with RN logo
st.markdown(
    '''<div style="text-align:center; margin-top:24px;">
                <span style="font-size:0.9em; color:#888;">Powered by</span><br>
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500" width="60" height="60">
                    <defs>
                        <linearGradient id="logo-grad" x1="120" y1="100" x2="380" y2="400" gradientUnits="userSpaceOnUse">
                            <stop offset="0%" stop-color="#0A3663" />
                            <stop offset="100%" stop-color="#1D978C" />
                        </linearGradient>
                    </defs>
                    <rect x="120" y="100" width="50" height="300" fill="url(#logo-grad)" />
                    <rect x="330" y="160" width="50" height="240" fill="url(#logo-grad)" />
                    <path d="M 170 100 H 260 C 330 100 380 135 380 195 C 380 255 330 290 260 290 H 170 V 240 H 260 C 310 240 330 220 330 195 C 330 170 310 150 260 150 H 170 Z" fill="url(#logo-grad)" />
                    <polygon points="170,240 220,240 380,400 330,400" fill="url(#logo-grad)" />
                    <path d="M 215 160 C 205 160 200 165 200 175 V 185 C 200 190 195 195 185 195 C 195 195 200 200 200 205 V 215 C 200 225 205 230 215 230" fill="none" stroke="url(#logo-grad)" stroke-width="10" stroke-linecap="round" stroke-linejoin="round" />
                    <path d="M 240 160 L 275 195 L 240 230" fill="none" stroke="url(#logo-grad)" stroke-width="10" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
                <div style="font-size:0.8em; color:#888;">RN</div>
        </div>''', unsafe_allow_html=True)
