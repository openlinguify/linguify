"""
Utilitaires pour l'extraction de texte depuis différents formats de documents
(PDF, images avec OCR, fichiers texte)
"""

import tempfile
from pathlib import Path
from typing import Tuple, Optional


def extract_text_from_file(filepath: str, mime_type: str) -> Tuple[str, str]:
    """
    Extrait le texte d'un fichier selon son type MIME

    Args:
        filepath: Chemin vers le fichier
        mime_type: Type MIME du fichier

    Returns:
        Tuple (texte extrait, méthode d'extraction utilisée)
    """
    if "pdf" in mime_type.lower():
        return extract_text_from_pdf(filepath)
    elif "image" in mime_type.lower():
        return extract_text_from_image(filepath)
    elif "text" in mime_type.lower() or mime_type == "application/octet-stream":
        return extract_text_from_text_file(filepath)
    else:
        return "", "unsupported"


def extract_text_from_pdf(filepath: str) -> Tuple[str, str]:
    """
    Extrait le texte d'un fichier PDF en utilisant PyMuPDF (fitz)

    Args:
        filepath: Chemin vers le fichier PDF

    Returns:
        Tuple (texte extrait, "PyMuPDF")
    """
    try:
        import fitz  # PyMuPDF

        text_parts = []
        with fitz.open(filepath) as doc:
            for page_num, page in enumerate(doc, 1):
                page_text = page.get_text()
                if page_text.strip():
                    text_parts.append(f"--- Page {page_num} ---\n{page_text}")

        full_text = "\n\n".join(text_parts)

        # Si le PDF ne contient pas de texte (PDF scanné), essayer l'OCR
        if not full_text.strip():
            return extract_text_from_scanned_pdf(filepath)

        return full_text, "PyMuPDF"

    except ImportError:
        raise ImportError(
            "PyMuPDF (fitz) n'est pas installé. "
            "Installez-le avec: pip install PyMuPDF"
        )
    except Exception as e:
        raise Exception(f"Erreur lors de l'extraction du PDF: {str(e)}")


def extract_text_from_scanned_pdf(filepath: str) -> Tuple[str, str]:
    """
    Extrait le texte d'un PDF scanné en utilisant OCR (pytesseract)

    Args:
        filepath: Chemin vers le fichier PDF scanné

    Returns:
        Tuple (texte extrait, "OCR-PDF")
    """
    try:
        import fitz  # PyMuPDF
        from PIL import Image
        import pytesseract
        import io

        text_parts = []
        with fitz.open(filepath) as doc:
            for page_num, page in enumerate(doc, 1):
                # Convertir la page en image
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # Zoom x2 pour meilleure qualité
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))

                # Appliquer l'OCR
                page_text = pytesseract.image_to_string(img, lang='fra+eng')
                if page_text.strip():
                    text_parts.append(f"--- Page {page_num} (OCR) ---\n{page_text}")

        return "\n\n".join(text_parts), "OCR-PDF"

    except ImportError as e:
        if "pytesseract" in str(e):
            raise ImportError(
                "pytesseract n'est pas installé. "
                "Installez-le avec: pip install pytesseract\n"
                "Et installez Tesseract-OCR sur votre système."
            )
        raise
    except Exception as e:
        raise Exception(f"Erreur lors de l'OCR du PDF: {str(e)}")


def extract_text_from_image(filepath: str) -> Tuple[str, str]:
    """
    Extrait le texte d'une image en utilisant OCR (pytesseract)

    Args:
        filepath: Chemin vers le fichier image

    Returns:
        Tuple (texte extrait, "OCR")
    """
    try:
        from PIL import Image
        import pytesseract

        # Ouvrir et prétraiter l'image
        img = Image.open(filepath)

        # Convertir en RGB si nécessaire
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Appliquer l'OCR (français et anglais)
        text = pytesseract.image_to_string(img, lang='fra+eng')

        return text, "OCR"

    except ImportError:
        raise ImportError(
            "pytesseract ou Pillow n'est pas installé. "
            "Installez-les avec: pip install pytesseract Pillow\n"
            "Et installez Tesseract-OCR sur votre système."
        )
    except Exception as e:
        raise Exception(f"Erreur lors de l'OCR de l'image: {str(e)}")


def extract_text_from_text_file(filepath: str) -> Tuple[str, str]:
    """
    Lit le contenu d'un fichier texte

    Args:
        filepath: Chemin vers le fichier texte

    Returns:
        Tuple (contenu du fichier, "text")
    """
    try:
        # Essayer différents encodages
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']

        for encoding in encodings:
            try:
                with open(filepath, 'r', encoding=encoding) as f:
                    content = f.read()
                return content, f"text-{encoding}"
            except UnicodeDecodeError:
                continue

        # Si aucun encodage ne fonctionne, ignorer les erreurs
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        return content, "text-utf8-ignore"

    except Exception as e:
        raise Exception(f"Erreur lors de la lecture du fichier texte: {str(e)}")


def preprocess_text_for_flashcards(text: str, max_length: int = 4000) -> str:
    """
    Prétraite le texte extrait pour optimiser la génération de flashcards

    Args:
        text: Texte brut extrait
        max_length: Longueur maximale du texte à retourner

    Returns:
        Texte nettoyé et tronqué
    """
    # Supprimer les espaces multiples
    text = " ".join(text.split())

    # Supprimer les sauts de ligne multiples
    text = "\n".join(line for line in text.split("\n") if line.strip())

    # Tronquer si trop long (pour éviter de dépasser les limites de l'API)
    if len(text) > max_length:
        text = text[:max_length] + "\n\n[... texte tronqué ...]"

    return text


def detect_document_language(text: str) -> Optional[str]:
    """
    Détecte la langue principale du document

    Args:
        text: Texte à analyser

    Returns:
        Code de langue (ex: 'fr', 'en') ou None
    """
    try:
        from langdetect import detect

        # Prendre un échantillon du texte pour la détection
        sample = text[:1000] if len(text) > 1000 else text

        if sample.strip():
            return detect(sample)
        return None

    except ImportError:
        # langdetect n'est pas installé, retourner None
        return None
    except Exception:
        # Erreur de détection
        return None
