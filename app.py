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


# install_playwright()
st.set_page_config(page_title="Download Automático da Caderneta Predial", page_icon="📂")

st.title("Download Automático da Caderneta Predial")
st.write("Insira o código da caderneta predial para baixar o documento em PDF diretamente do site oficial.")

# 1. User Input
building_code = st.text_input(
    "Código da Caderneta Predial:", placeholder="e.g., 12345678", value=BUILDING_CODE)

# 2. Execution Trigger
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

                    # --- Step 1: Validation ---
                    st.write("🔍 Validando...")
                    with page.expect_navigation(wait_until="networkidle"):
                        page.click("a[title='Validar Código']", force=True)

                    # --- Step 2: Continue ---
                    btn_continuar = page.locator("a[title='Continuar']")
                    if btn_continuar.is_visible():
                        st.write("⏩ Avançando para a próxima página...")
                        with page.expect_navigation(wait_until="networkidle"):
                            btn_continuar.click(force=True)

                        # --- Step 3: Final Download ---
                        btn_download = page.locator(
                            "a[title='Efetuar Download']")
                        if btn_download.is_visible():
                            st.write("⬇️ Gerando PDF...")
                            with page.expect_download(timeout=20000) as dwn_inf:
                                btn_download.click(force=True)

                            download = dwn_inf.value
                            temp_path = f"./{download.suggested_filename}"
                            download.save_as(temp_path)

                            status.update(label="✅ Sucesso!", state="complete")

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
st.write("Feito por Catarina & Rafael")
