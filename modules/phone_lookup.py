import phonenumbers
from phonenumbers import carrier, geocoder, timezone

def _region_to_flag(region: str) -> str:
    if not region or len(region) != 2:
        return ""
    return chr(ord(region[0]) + 127397) + chr(ord(region[1]) + 127397)

def lookup_phone(number: str, default_region: str = None) -> dict:
    try:
        parsed = phonenumbers.parse(number, default_region)
        if not phonenumbers.is_valid_number(parsed):
            return {"error": "Número inválido"}

        national = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)
        international = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        e164 = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)

        country_code = parsed.country_code
        national_num = parsed.national_number
        region_code = phonenumbers.region_code_for_number(parsed)
        flag = _region_to_flag(region_code)
        location = geocoder.description_for_number(parsed, "es") or geocoder.description_for_number(parsed, "en")
        carrier_name = carrier.name_for_number(parsed, "es") or carrier.name_for_number(parsed, "en")
        timezones = timezone.time_zones_for_number(parsed)
        line_type = _get_line_type(parsed)

        return {
            "valid": True,
            "nacional": national,
            "internacional": international,
            "e164": e164,
            "codigo_pais": f"+{country_code}",
            "bandera": flag,
            "pais_region": region_code,
            "numero_nacional": str(national_num),
            "operador": carrier_name or "Desconocido",
            "ubicacion": location or "Desconocida",
            "zona_horaria": ", ".join(timezones) if timezones else "Desconocida",
            "tipo_linea": line_type,
        }
    except Exception as e:
        return {"error": str(e)}

def _get_line_type(parsed) -> str:
    num_type = phonenumbers.number_type(parsed)
    types = {
        phonenumbers.PhoneNumberType.MOBILE: "Móvil",
        phonenumbers.PhoneNumberType.FIXED_LINE: "Fijo",
        phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE: "Fijo o Móvil",
        phonenumbers.PhoneNumberType.TOLL_FREE: "Gratuito (Toll-Free)",
        phonenumbers.PhoneNumberType.PREMIUM_RATE: "Tarifa Premium",
        phonenumbers.PhoneNumberType.SHARED_COST: "Coste Compartido",
        phonenumbers.PhoneNumberType.VOIP: "VoIP",
        phonenumbers.PhoneNumberType.PAGER: "Localizador",
        phonenumbers.PhoneNumberType.UAN: "UAN",
        phonenumbers.PhoneNumberType.VOICEMAIL: "Buzón de Voz",
        phonenumbers.PhoneNumberType.UNKNOWN: "Desconocido",
    }
    return types.get(num_type, "Desconocido")
