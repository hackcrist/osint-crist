import re
import json
import aiohttp
from utils.formatting import bold, code

async def verify_email(email: str) -> bool:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.mailcheck.ai/email/{email}",
                timeout=aiohttp.ClientTimeout(total=5),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return not data.get("disposable", True) and data.get("mx", False)
    except:
        pass
    return False

PATTERNS = [
    "{first}.{last}",
    "{first}{last}",
    "{f}.{last}",
    "{last}.{first}",
    "{first}.{l}",
    "{first}{l}",
    "{f}{last}",
    "{f}.{l}",
    "{fl}",
    "{first}.{last2}",
    "{first}{last2}",
    "{first}_{last}",
    "{first}-{last}",
    "{f}_{last}",
    "{f}-{last}",
]

def normalize(name: str) -> str:
    name = re.sub(r'[^\w\sáéíóúüñÁÉÍÓÚÜÑ]', '', name)
    name = name.strip().lower()
    replacements = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'ü': 'u', 'ñ': 'n', 'Á': 'a', 'É': 'e', 'Í': 'i',
        'Ó': 'o', 'Ú': 'u', 'Ü': 'u', 'Ñ': 'n',
    }
    for old, new in replacements.items():
        name = name.replace(old, new)
    return name

def parse_name(full_name: str) -> tuple:
    parts = normalize(full_name).split()
    if not parts:
        return None, None, None, None
    first = parts[0]
    last = parts[-1]
    last2 = " ".join(parts[1:]) if len(parts) > 1 else last
    f = first[0]
    l = last[0]
    fl = f + l
    return first, last, last2, f, l, fl

def generate_emails(name: str, domain: str = "gmail.com") -> list:
    parts = normalize(name).split()
    if not parts:
        return []

    first = parts[0]
    last = parts[-1]
    last2 = " ".join(parts[1:]) if len(parts) > 1 else last
    f = first[0]
    l = last[0]
    fl = f + l

    emails = []
    seen = set()

    for pattern in PATTERNS:
        email = pattern.format(
            first=first, last=last, last2=last2,
            f=f, l=l, fl=fl
        )
        full = f"{email}@{domain}"
        if full not in seen:
            seen.add(full)
            emails.append(full)

    return emails

async def gen_emails(args: str) -> str:
    parts = args.strip().split()
    if len(parts) < 2:
        name = args
        domain = "gmail.com"
    else:
        possible_domain = parts[-1]
        if "." in possible_domain and not possible_domain.startswith("@"):
            if possible_domain.startswith("@"):
                possible_domain = possible_domain[1:]
            domain = possible_domain
            name = " ".join(parts[:-1])
        else:
            name = args
            domain = "gmail.com"

    emails = generate_emails(name, domain)
    if not emails:
        return "❌ No se pudo procesar el nombre."

    lines = [
        f"📧 {bold('GENERADOR DE EMAILS')}\n",
        f"Nombre: {code(name)}",
        f"Dominio: {code('@' + domain)}",
        f"Total: {len(emails)}\n",
        f"{bold('Posibles emails')}:",
    ]
    for i, email in enumerate(emails, 1):
        lines.append(f"  {i:2d}. {email}")

    more_domains = [
        "hotmail.com", "outlook.com", "yahoo.com",
        "icloud.com", "proton.me", "live.com",
    ]
    lines.append(f"\n{bold('Otros dominios comunes')}:")
    for d in more_domains:
        alt = f"{emails[0].split('@')[0]}@{d}"
        lines.append(f"  • {alt}")

    return "\n".join(lines)