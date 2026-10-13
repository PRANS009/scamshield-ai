import ipaddress
import re
from typing import Optional
from urllib.parse import urlsplit, urlunsplit


def normalize_url(value: str) -> str:
    value = value.strip()
    if not value or len(value) > 2048 or re.search(r'[\s\\\x00-\x1f]', value):
        raise ValueError('Enter a valid public HTTP(S) URL without spaces.')
    if '://' not in value:
        value = 'https://' + value
    try:
        parsed = urlsplit(value)
        host = (parsed.hostname or '').rstrip('.').encode('idna').decode().lower()
        if parsed.scheme not in ('http', 'https') or not host or parsed.username or parsed.password:
            raise ValueError()
        if parsed.port not in (None, 80, 443):
            raise ValueError()
        if host == 'localhost' or host.endswith(('.localhost', '.local', '.internal', '.test', '.invalid')) or '.' not in host:
            raise ValueError()
        try:
            address = ipaddress.ip_address(host)
        except ValueError:
            if re.fullmatch(r'[0-9.]+', host) or not re.fullmatch(r'(?=.{1,253}$)[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?', host):
                raise ValueError()
            if any(not label or len(label)>63 or label.startswith('-') or label.endswith('-') for label in host.split('.')):
                raise ValueError()
        else:
            if not address.is_global:
                raise ValueError()
        return urlunsplit((parsed.scheme, host, parsed.path or '/', parsed.query, ''))
    except (ValueError, UnicodeError):
        raise ValueError('Only public HTTP(S) addresses on standard ports are accepted; credentials and internal addresses are blocked.') from None


def safe_link(value: str) -> Optional[str]:
    try:
        return normalize_url(value)
    except ValueError:
        return None


def domain(value: str) -> str:
    return urlsplit(normalize_url(value)).hostname or ''


def redact(text: str) -> str:
    text = re.sub(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', '[email redacted]', text)
    text = re.sub(r'(?<!\w)(?:\+?\d[\d -]{8,}\d)(?!\w)', lambda m: '[number redacted]' if len(re.sub(r'\D', '', m.group())) >= 10 else m.group(), text)
    text = re.sub(r'(?i)(otp|password|pin)\s*[:=]\s*\S+', r'\1: [redacted]', text)
    return text


def public_term(text: str) -> str:
    return re.sub(r'[^\w .+/-]', ' ', redact(text))[:120].strip()


def redact_payload(value):
    if isinstance(value, dict):
        return {k: v if k in ('id','report_id','created_at','retrieved_at','url','urls','deadline') else redact_payload(v) for k,v in value.items()}
    if isinstance(value, list):
        return [redact_payload(v) for v in value]
    return redact(value) if isinstance(value,str) else value
