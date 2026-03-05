# Caderneta Predial Downloader

Automated tool to download the **Caderneta Predial** (Portuguese Property Tax Certificate) PDF directly from the official [Predial Online](https://www.predialonline.pt) government portal.

Two modes are available:
- **Web App** (`app.py`) — Streamlit-based browser UI where the user enters a property code and downloads the PDF through the browser.
- **CLI Binary** (`webscrapper`) — Standalone executable that opens a visible browser window and saves the PDF to disk automatically.

---

## Technologies

| Technology | Role |
|---|---|
| **Python 3** | Core language |
| **Playwright** | Headless/headed browser automation for navigating and downloading from the government portal |
| **Streamlit** | Web UI framework for the hosted app |
| **Docker** | Container packaging for server deployment |
| **PyInstaller** | Bundles the CLI scraper into a self-contained executable |

---

## How It Works

1. The tool navigates to the Predial Online certificate page.
2. It fills in the property code (`Código da Caderneta Predial`).
3. It clicks **Validar Código**, then **Continuar**, then **Efetuar Download**.
4. The PDF is saved — either served to the browser (web app) or written to disk (CLI binary).

---

## Web App (Streamlit)

### Run locally

```bash
pip install -r requirements.txt
playwright install chromium
streamlit run app.py
```

Open `http://localhost:8501`, enter the property code and click **Procurar Documento**.

---

## Docker Installation

### Build the image

```bash
docker build -t caderneta-predial .
```

### Run the container

```bash
docker run -p 8000:8000 caderneta-predial
```

Open `http://localhost:8000` in your browser.

The Docker image is based on `mcr.microsoft.com/playwright/python` (Jammy), which ships with all Playwright browser dependencies pre-installed. Only Chromium is installed to keep the image lightweight.

---

## CLI Binary Usage

The standalone binary (`webscrapper.exe` on Windows, `webscrapper` on Linux/macOS) requires **no Python installation**.

### Download / build

Pre-built binaries are found in the `dist/` folder after running PyInstaller (see below).

### Run

```bash
# Windows
dist\webscrapper.exe

# Linux / macOS
./dist/webscrapper
```

The binary opens a Chromium browser window, navigates to Predial Online using the hardcoded property code, and saves the downloaded PDF to the current working directory.

To change the target property code, edit the `BUILDING_CODE` constant in `webscrapper.py` before building.

---

## Building the Binary with PyInstaller

Requirements: Python virtual environment activated with dependencies installed.

```bash
pip install -r requirements.txt
pip install pyinstaller
```

Build using the provided spec file:

```bash
pyinstaller webscrapper.spec
```

Or build directly with the one-liner:

```bash
pyinstaller --onefile --windowed --add-data "env/Lib/site-packages/playwright/driver:playwright/driver" webscrapper.py
```

The output binary is placed in `dist/webscrapper` (or `dist\webscrapper.exe` on Windows).

> **Note:** The Playwright driver (`playwright/driver`) must be bundled with `--add-data` so the binary can launch Chromium without a separate Python/Playwright installation.

---

## Project Structure

```
.
├── app.py              # Streamlit web application
├── webscrapper.py      # Standalone CLI scraper (source for the binary)
├── webscrapper.spec    # PyInstaller build spec
├── requirements.txt    # Python dependencies
├── Dockerfile          # Docker image definition
├── setup.sh            # Helper script to install Playwright on Linux
└── asset/              # Static assets (logo, etc.)
```

