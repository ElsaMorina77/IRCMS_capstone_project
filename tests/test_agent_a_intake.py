import json
import re
import tempfile
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import yaml


TEXT_EXTENSIONS = {".txt", ".md"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"}
HTML_EXTENSIONS = {".html", ".htm"}
PDF_EXTENSIONS = {".pdf"}


class SimpleHTMLTextExtractor(HTMLParser):
    """
    Lightweight HTML text extractor using only Python standard library.

    It ignores common non-content tags and extracts visible text.
    This is not as powerful as BeautifulSoup/readability, but it is good
    enough for MVP-level HTML intake without adding heavy dependencies.
    """

    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip_tag_stack = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() in {"script", "style", "noscript", "svg", "nav", "footer"}:
            self.skip_tag_stack.append(tag.lower())

    def handle_endtag(self, tag):
        tag = tag.lower()
        if self.skip_tag_stack and self.skip_tag_stack[-1] == tag:
            self.skip_tag_stack.pop()

    def handle_data(self, data):
        if self.skip_tag_stack:
            return

        clean_data = data.strip()

        if clean_data:
            self.parts.append(clean_data)

    def get_text(self) -> str:
        return "\n".join(self.parts)


class IntakeAgent:
    """
    Agent A - Intake.

    Reads the scenario bundle, validates required files, creates:
    - context_packet.json
    - evidence_index.json

    Supported regulation inputs:
    - .txt / .md
    - .pdf text extraction through pypdf
    - scanned PDF OCR fallback through pdf2image + pytesseract
    - image OCR through pytesseract
    - local .html / .htm files
    - basic HTML URL scraping through urllib + HTMLParser

    The rest of the pipeline does not need to change because this agent
    always creates the same evidence_index.json structure.
    """

    def __init__(self, bundle_dir: Path, run_dir: Path, audit=None):
        self.bundle_dir = Path(bundle_dir)
        self.run_dir = Path(run_dir)
        self.audit = audit

    def run(self) -> dict:
        self.log("Agent A Intake started.")

        manifest = self.load_manifest()
        self.validate_required_files(manifest)

        regulation_source = manifest["regulation_file"]
        regulation_result = self.extract_regulation_text(regulation_source)

        if not regulation_result["text"].strip():
            raise ValueError(
                f"No regulation text could be extracted from: {regulation_source}"
            )

        context_packet = self.create_context_packet(
            manifest=manifest,
            regulation_result=regulation_result,
        )

        evidence_index = self.create_evidence_index(
            regulation_text=regulation_result["text"],
            source_file=regulation_source,
            source_type=regulation_result["source_type"],
            extraction_method=regulation_result["extraction_method"],
            ocr_used=regulation_result["ocr_used"],
        )

        self.write_json("context_packet.json", context_packet)
        self.write_json("evidence_index.json", {"evidence": evidence_index})

        self.log("Agent A created context_packet.json.")
        self.log("Agent A created evidence_index.json.")
        self.log("Agent A Intake completed.")

        return context_packet

    # ---------------------------------------------------------
    # Manifest and validation
    # ---------------------------------------------------------

    def load_manifest(self) -> dict:
        manifest_path = self.bundle_dir / "manifest.yaml"

        if not manifest_path.exists():
            raise FileNotFoundError(f"Missing manifest file: {manifest_path}")

        with open(manifest_path, "r", encoding="utf-8") as file:
            manifest = yaml.safe_load(file)

        if not manifest:
            raise ValueError("manifest.yaml is empty or invalid.")

        return manifest

    def validate_required_files(self, manifest: dict) -> None:
        required_keys = [
            "regulation_file",
            "current_policies_file",
            "control_inventory_file",
            "process_map_file",
        ]

        for key in required_keys:
            if key not in manifest:
                raise KeyError(f"Missing key in manifest.yaml: {key}")

        # Regulation can be a local file or a URL.
        regulation_source = manifest["regulation_file"]

        if not self.is_url(regulation_source):
            regulation_path = self.bundle_dir / regulation_source

            if not regulation_path.exists():
                raise FileNotFoundError(
                    f"Missing regulation file: {regulation_path}"
                )

        # These files are still local bundle files.
        local_required_keys = [
            "current_policies_file",
            "control_inventory_file",
            "process_map_file",
        ]

        for key in local_required_keys:
            file_path = self.bundle_dir / manifest[key]

            if not file_path.exists():
                raise FileNotFoundError(f"Missing required bundle file: {file_path}")

    # ---------------------------------------------------------
    # Regulation text extraction
    # ---------------------------------------------------------

    def extract_regulation_text(self, source: str) -> dict:
        """
        Extract text from the regulation source.

        Returns:
        {
            "text": "...",
            "source_type": "text/pdf/image/html/url",
            "extraction_method": "...",
            "ocr_used": true/false
        }
        """

        if self.is_url(source):
            return self.extract_from_url(source)

        file_path = self.bundle_dir / source
        extension = file_path.suffix.lower()

        if extension in TEXT_EXTENSIONS:
            return {
                "text": self.read_text_file(file_path),
                "source_type": "text",
                "extraction_method": "plain_text",
                "ocr_used": False,
            }

        if extension in HTML_EXTENSIONS:
            html = self.read_text_file(file_path)
            return {
                "text": self.extract_text_from_html(html),
                "source_type": "html",
                "extraction_method": "html_parser",
                "ocr_used": False,
            }

        if extension in PDF_EXTENSIONS:
            return self.extract_from_pdf(file_path)

        if extension in IMAGE_EXTENSIONS:
            return {
                "text": self.extract_text_from_image(file_path),
                "source_type": "image",
                "extraction_method": "image_ocr",
                "ocr_used": True,
            }

        raise ValueError(
            f"Unsupported regulation file type: {extension}. "
            f"Supported: txt, md, pdf, png, jpg, jpeg, webp, bmp, tiff, html, htm, URL"
        )

    def read_text_file(self, file_path: Path) -> str:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()

    # ---------------------------------------------------------
    # URL / HTML support
    # ---------------------------------------------------------

    def is_url(self, value: str) -> bool:
        parsed = urlparse(str(value))
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)

    def extract_from_url(self, url: str) -> dict:
        """
        Basic URL reader.

        Supports:
        - HTML pages
        - PDF URL download and extraction

        Does not support JavaScript-rendered pages. That is future work.
        """

        self.log(f"Agent A reading regulation from URL: {url}")

        parsed = urlparse(url)
        extension = Path(parsed.path).suffix.lower()

        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "IRCMS-MVP-AgentA/1.0"
            },
        )

        with urllib.request.urlopen(request, timeout=20) as response:
            content_type = response.headers.get("Content-Type", "").lower()
            raw_data = response.read()

        if extension == ".pdf" or "application/pdf" in content_type:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(raw_data)
                temp_pdf_path = Path(temp_file.name)

            try:
                pdf_result = self.extract_from_pdf(temp_pdf_path)
                pdf_result["source_type"] = "url_pdf"
                return pdf_result
            finally:
                try:
                    temp_pdf_path.unlink()
                except OSError:
                    pass

        html = raw_data.decode("utf-8", errors="ignore")

        return {
            "text": self.extract_text_from_html(html),
            "source_type": "url_html",
            "extraction_method": "url_html_parser",
            "ocr_used": False,
        }

    def extract_text_from_html(self, html: str) -> str:
        parser = SimpleHTMLTextExtractor()
        parser.feed(html)
        raw_text = parser.get_text()

        cleaned_lines = []

        for line in raw_text.splitlines():
            line = self.clean_whitespace(line)

            if not line:
                continue

            if self.is_likely_navigation_noise(line):
                continue

            cleaned_lines.append(line)

        return "\n\n".join(cleaned_lines)

    def is_likely_navigation_noise(self, text: str) -> bool:
        text_lower = text.lower().strip()

        noisy_exact = {
            "home",
            "menu",
            "search",
            "login",
            "sign in",
            "register",
            "privacy policy",
            "terms of use",
            "cookies",
            "contact",
        }

        if text_lower in noisy_exact:
            return True

        if len(text_lower) <= 2:
            return True

        return False

    # ---------------------------------------------------------
    # PDF support
    # ---------------------------------------------------------

    def extract_from_pdf(self, file_path: Path) -> dict:
        """
        PDF extraction strategy:
        1. Try digital PDF text extraction using pypdf.
        2. If little/no text is found, try OCR fallback using pdf2image + pytesseract.
        """

        self.log(f"Agent A extracting PDF text from: {file_path}")

        pdf_text = self.extract_text_from_digital_pdf(file_path)

        if self.has_enough_text(pdf_text):
            return {
                "text": pdf_text,
                "source_type": "pdf",
                "extraction_method": "pdf_text_extraction",
                "ocr_used": False,
            }

        self.log(
            "Agent A PDF text extraction produced little/no text. Trying OCR fallback."
        )

        ocr_text = self.extract_text_from_scanned_pdf(file_path)

        return {
            "text": ocr_text,
            "source_type": "pdf",
            "extraction_method": "pdf_ocr_fallback",
            "ocr_used": True,
        }

    def extract_text_from_digital_pdf(self, file_path: Path) -> str:
        try:
            from pypdf import PdfReader
        except ImportError as error:
            self.log("Agent A warning: pypdf is not installed.")
            return ""

        try:
            reader = PdfReader(str(file_path))
            pages_text = []

            for page in reader.pages:
                page_text = page.extract_text() or ""

                if page_text.strip():
                    pages_text.append(page_text)

            return "\n\n".join(pages_text)

        except Exception as error:
            self.log(f"Agent A warning: PDF text extraction failed: {error}")
            return ""

    def extract_text_from_scanned_pdf(self, file_path: Path) -> str:
        try:
            from pdf2image import convert_from_path
        except ImportError:
            raise ImportError(
                "pdf2image is required for scanned PDF OCR. "
                "Install it with: python -m pip install pdf2image"
            )

        try:
            import pytesseract
        except ImportError:
            raise ImportError(
                "pytesseract is required for OCR. "
                "Install it with: python -m pip install pytesseract"
            )

        try:
            pages = convert_from_path(str(file_path))
        except Exception as error:
            raise RuntimeError(
                "Could not convert PDF pages to images. "
                "For scanned PDF OCR, Poppler must be installed and available in PATH. "
                f"Original error: {error}"
            )

        extracted_pages = []

        for index, page in enumerate(pages, start=1):
            text = pytesseract.image_to_string(page)

            if text.strip():
                extracted_pages.append(text)

            self.log(f"Agent A OCR processed PDF page {index}.")

        return "\n\n".join(extracted_pages)

    # ---------------------------------------------------------
    # Image OCR support
    # ---------------------------------------------------------

    def extract_text_from_image(self, file_path: Path) -> str:
        try:
            from PIL import Image
        except ImportError:
            raise ImportError(
                "Pillow is required for image OCR. "
                "Install it with: python -m pip install pillow"
            )

        try:
            import pytesseract
        except ImportError:
            raise ImportError(
                "pytesseract is required for OCR. "
                "Install it with: python -m pip install pytesseract"
            )

        self.log(f"Agent A running OCR on image: {file_path}")

        try:
            image = Image.open(file_path)
            return pytesseract.image_to_string(image)
        except Exception as error:
            raise RuntimeError(f"Image OCR failed for {file_path}: {error}")

    # ---------------------------------------------------------
    # Evidence and output creation
    # ---------------------------------------------------------

    def create_context_packet(self, manifest: dict, regulation_result: dict) -> dict:
        return {
            "bundle_id": manifest.get("bundle_id"),
            "title": manifest.get("title"),
            "business_units": manifest.get("business_units", []),
            "expected_result": manifest.get("expected_result", []),
            "source_files": {
                "regulation": manifest["regulation_file"],
                "current_policies": manifest["current_policies_file"],
                "control_inventory": manifest["control_inventory_file"],
                "process_map": manifest["process_map_file"],
            },
            "intake_metadata": {
                "regulation_source_type": regulation_result["source_type"],
                "extraction_method": regulation_result["extraction_method"],
                "ocr_used": regulation_result["ocr_used"],
            },
        }

    def create_evidence_index(
        self,
        regulation_text: str,
        source_file: str,
        source_type: str,
        extraction_method: str,
        ocr_used: bool,
    ) -> list:
        paragraphs = self.split_into_paragraphs(regulation_text)

        evidence_items = []

        for index, paragraph in enumerate(paragraphs, start=1):
            evidence_items.append(
                {
                    "evidence_id": f"EV-{index:03}",
                    "source_file": source_file,
                    "source_type": source_type,
                    "extraction_method": extraction_method,
                    "ocr_used": ocr_used,
                    "paragraph_number": index,
                    "text": paragraph,
                }
            )

        return evidence_items

    def split_into_paragraphs(self, text: str) -> list:
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # First split by blank lines.
        paragraphs = [
            self.clean_whitespace(paragraph)
            for paragraph in re.split(r"\n\s*\n", text)
            if self.clean_whitespace(paragraph)
        ]

        # If OCR/PDF produced one huge block, fallback to sentence-like chunks.
        if len(paragraphs) <= 1:
            sentences = re.split(r"(?<=[.!?])\s+", text)
            paragraphs = [
                self.clean_whitespace(sentence)
                for sentence in sentences
                if len(self.clean_whitespace(sentence)) > 20
            ]

        return paragraphs

    def clean_whitespace(self, text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()

    def has_enough_text(self, text: str) -> bool:
        clean_text = self.clean_whitespace(text)
        return len(clean_text) >= 50

    def write_json(self, filename: str, data) -> None:
        output_path = self.run_dir / filename

        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def log(self, message: str) -> None:
        if self.audit:
            self.audit.log(message)