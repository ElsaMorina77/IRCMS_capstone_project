import json
import re
from pathlib import Path
from typing import Tuple

import yaml


class IntakeAgent:
    """
    Agent A - Intake.

    Reads the scenario bundle, validates required files, creates context_packet.json
    and evidence_index.json. Supports plain text files by default and optional OCR
    for image/PDF regulation files.
    """

    TEXT_EXTENSIONS = {".txt", ".md"}
    IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}
    PDF_EXTENSIONS = {".pdf"}

    def __init__(self, bundle_dir: Path, run_dir: Path, audit):
        self.bundle_dir = bundle_dir
        self.run_dir = run_dir
        self.audit = audit

    def run(self) -> dict:
        self.audit.log("Agent A Intake started.")

        manifest = self.load_manifest()
        self.validate_required_files(manifest)

        regulation_file = manifest["regulation_file"]
        regulation_text, intake_metadata = self.read_regulation_source(regulation_file)

        context_packet = self.create_context_packet(manifest, intake_metadata)
        evidence_index = self.create_evidence_index(
            regulation_text=regulation_text,
            regulation_file=regulation_file,
            intake_metadata=intake_metadata,
        )

        self.write_json("context_packet.json", context_packet)
        self.write_json("evidence_index.json", {"evidence": evidence_index})

        self.audit.log("Agent A created context_packet.json.")
        self.audit.log("Agent A created evidence_index.json.")
        self.audit.log(
            f"Agent A Intake completed. Source type: {intake_metadata['source_type']}. OCR used: {intake_metadata['ocr_used']}."
        )

        return context_packet

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

            file_path = self.bundle_dir / manifest[key]

            if not file_path.exists():
                raise FileNotFoundError(f"Missing required bundle file: {file_path}")

    def read_regulation_source(self, filename: str) -> Tuple[str, dict]:
        file_path = self.bundle_dir / filename
        extension = file_path.suffix.lower()

        metadata = {
            "source_file": filename,
            "source_extension": extension,
            "source_type": "text",
            "ocr_used": False,
            "ocr_engine": None,
        }

        if extension in self.TEXT_EXTENSIONS:
            return self.read_text_file(filename), metadata

        if extension in self.IMAGE_EXTENSIONS:
            metadata.update({"source_type": "image", "ocr_used": True, "ocr_engine": "tesseract"})
            return self.ocr_image_file(file_path), metadata

        if extension in self.PDF_EXTENSIONS:
            text = self.extract_pdf_text(file_path)
            if text.strip():
                metadata.update({"source_type": "pdf_text", "ocr_used": False, "ocr_engine": None})
                return text, metadata

            metadata.update({"source_type": "pdf_ocr", "ocr_used": True, "ocr_engine": "tesseract"})
            return self.ocr_pdf_file(file_path), metadata

        raise ValueError(
            f"Unsupported regulation file type '{extension}'. Supported: .txt, .md, .pdf, .png, .jpg, .jpeg, .tif, .tiff, .bmp"
        )

    def read_text_file(self, filename: str) -> str:
        file_path = self.bundle_dir / filename
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()

    def extract_pdf_text(self, file_path: Path) -> str:
        try:
            from pypdf import PdfReader
        except ImportError:
            self.audit.log("Agent A warning: pypdf is not installed. Trying OCR fallback for PDF.")
            return ""

        try:
            reader = PdfReader(str(file_path))
            pages = []
            for page in reader.pages:
                pages.append(page.extract_text() or "")
            return "\n\n".join(page.strip() for page in pages if page.strip())
        except Exception as error:
            self.audit.log(f"Agent A warning: PDF text extraction failed: {error}. Trying OCR fallback.")
            return ""

    def ocr_image_file(self, file_path: Path) -> str:
        try:
            from PIL import Image
            import pytesseract
        except ImportError as error:
            raise ImportError(
                "OCR image support requires Pillow and pytesseract. Install with: python -m pip install pillow pytesseract"
            ) from error

        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
        except Exception as error:
            raise RuntimeError(
                "OCR failed. Make sure Tesseract OCR is installed and available in PATH."
            ) from error

        if not text.strip():
            raise ValueError(f"OCR produced no readable text for {file_path}")

        return text

    def ocr_pdf_file(self, file_path: Path) -> str:
        try:
            from pdf2image import convert_from_path
        except ImportError as error:
            raise ImportError(
                "Scanned PDF OCR requires pdf2image plus pytesseract/Pillow. Install with: python -m pip install pdf2image pillow pytesseract"
            ) from error

        try:
            images = convert_from_path(str(file_path))
        except Exception as error:
            raise RuntimeError(
                "Could not convert PDF pages to images. On Windows, install Poppler and add it to PATH, or use image files instead."
            ) from error

        page_texts = []
        for index, image in enumerate(images, start=1):
            try:
                import pytesseract
                text = pytesseract.image_to_string(image)
                if text.strip():
                    page_texts.append(text.strip())
            except Exception as error:
                raise RuntimeError(f"OCR failed on PDF page {index}.") from error

        combined_text = "\n\n".join(page_texts)
        if not combined_text.strip():
            raise ValueError(f"OCR produced no readable text for {file_path}")

        return combined_text

    def create_context_packet(self, manifest: dict, intake_metadata: dict) -> dict:
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
            "intake_metadata": intake_metadata,
        }

    def create_evidence_index(self, regulation_text: str, regulation_file: str, intake_metadata: dict) -> list:
        paragraphs = self.split_into_evidence_paragraphs(regulation_text)

        evidence_items = []

        for index, paragraph in enumerate(paragraphs, start=1):
            evidence_items.append(
                {
                    "evidence_id": f"EV-{index:03}",
                    "source_file": regulation_file,
                    "source_type": intake_metadata["source_type"],
                    "ocr_used": intake_metadata["ocr_used"],
                    "paragraph_number": index,
                    "text": paragraph,
                }
            )

        if not evidence_items:
            raise ValueError("Agent A could not create evidence items because the regulation text is empty.")

        return evidence_items

    def split_into_evidence_paragraphs(self, text: str) -> list:
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = text.strip()

        if not text:
            return []

        paragraphs = [part.strip() for part in re.split(r"\n\s*\n|\n", text) if part.strip()]

        if len(paragraphs) <= 1 and len(text) > 300:
            paragraphs = [part.strip() for part in re.split(r"(?<=[.!?])\s+(?=[A-Z])", text) if part.strip()]

        return paragraphs

    def write_json(self, filename: str, data) -> None:
        output_path = self.run_dir / filename

        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
