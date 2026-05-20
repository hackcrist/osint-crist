import hashlib
import io
import qrcode

def generate_hashes(text: str) -> dict:
    data = text.encode()
    return {
        "md5": hashlib.md5(data).hexdigest(),
        "sha1": hashlib.sha1(data).hexdigest(),
        "sha256": hashlib.sha256(data).hexdigest(),
        "sha512": hashlib.sha512(data).hexdigest(),
    }

def generate_qr(text: str) -> bytes:
    qr = qrcode.make(text, box_size=8, border=2)
    buf = io.BytesIO()
    qr.save(buf, format="PNG")
    return buf.getvalue()
