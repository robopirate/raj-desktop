"""email_validator.py — syntax + MX validation for imported leads."""
import re
import dns.resolver
from functools import lru_cache

SYNTAX = re.compile(r'^[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}$')


@lru_cache(maxsize=2048)
def _domain_has_mx(domain: str) -> bool:
    try:
        answers = dns.resolver.resolve(domain, 'MX', lifetime=4.0)
        return len(answers) > 0
    except Exception:
        # Fall back to A record — some domains receive mail without MX
        try:
            dns.resolver.resolve(domain, 'A', lifetime=4.0)
            return True
        except Exception:
            return False


def validate_email(addr: str) -> tuple[bool, str]:
    """Return (ok, reason). reason is '' when ok."""
    addr = (addr or '').strip()
    if not addr or not SYNTAX.match(addr):
        return False, 'bad-syntax'
    domain = addr.rsplit('@', 1)[1].lower()
    if not _domain_has_mx(domain):
        return False, 'no-mx'
    return True, ''
