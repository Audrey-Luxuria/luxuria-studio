import email
import email.header
import email.utils
from langdetect import detect, LangDetectException

def decode_header_value(header_value):
    """Decodage securise dun en-tete email."""
    if not header_value:
        return "(champ vide)"
    try:
        decoded_parts = email.header.decode_header(header_value)
        fragments = []
        for part, charset in decoded_parts:
            if isinstance(part, bytes):
                try:
                    fragments.append(part.decode(charset or "utf-8", errors="replace"))
                except (UnicodeDecodeError, LookupError):
                    fragments.append(part.decode("utf-8", errors="replace"))
            else:
                fragments.append(str(part))
        return ''.join(fragments)
    except (TypeError, ValueError):
        return "(objet illisible)"

def extract_body(msg):
    """Extraction du corps texte brut dun email."""
    if not msg:
        return "(message vide)"
    try:
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_dispo = str(part.get("Content-Disposition"))
                if content_type == "text/plain" and "attachment" not in content_dispo:
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset() or "utf-8"
                        try:
                            return payload.decode(charset, errors="replace")
                        except (UnicodeDecodeError, LookupError):
                            return payload.decode("utf-8", errors="replace")
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                charset = msg.get_content_charset() or "utf-8"
                try:
                    return payload.decode(charset, errors="replace")
                except (UnicodeDecodeError, LookupError):
                    return payload.decode("utf-8", errors="replace")
    except (AttributeError, TypeError):
        pass
    return "(corps illisible)"

def detect_language(text):
    """Detection de la langue du contenu."""
    try:
        return detect(text)
    except LangDetectException:
        return "und"  # undefined

def process_email(msg):
    """Traitement complet dun message email avec detection de langue."""
    subject_raw = msg.get('Subject', '')
    from_raw = msg.get('From', '')
    date_raw = msg.get('Date', '')

    subject = decode_header_value(subject_raw)
    sender = decode_header_value(from_raw)
    try:
        date = email.utils.parsedate_to_datetime(date_raw)
    except (TypeError, ValueError, IndexError):
        date = None

    body = extract_body(msg)
    language = detect_language(body)

    return {
        "subject": subject,
        "from": sender,
        "date": date,
        "body": body,
        "language": language
    }
