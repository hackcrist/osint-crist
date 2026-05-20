# 🕵️ OSINT Bot — Investigación de Personas

Bot de Telegram para OSINT (Open Source Intelligence) enfocado en investigación de personas. 100% gratuito, modular y async.

## 🚀 Comandos

| Comando | Descripción |
|---------|-------------|
| `/email <correo>` | Analiza email: MX, Gravatar, desechable, filtraciones |
| `/domain <dominio>` | Busca emails asociados a un dominio (Hunter.io) |
| `/phone <número>` | Información de número telefónico |
| `/user <username>` | Busca usuario en 30+ plataformas |
| `/person <nombre>` | Busca información de una persona |
| `/geo <lat,lng>` o `+teléfono` | Geolocalización inversa |
| `/ip [dirección]` | Geolocalización IP + detección VPN/Proxy/Tor |
| `/web <url>` | Escaneo completo de sitio web |
| `/whois <dominio>` | Consulta WHOIS |
| `/exif` | Metadatos EXIF de fotos |
| `/breach <email>` | Búsqueda de filtraciones |
| `/spam <número>` | Reputación de número spam |
| `/fbi <nombre>` o `top` | FBI Most Wanted |
| `/track new/list/view` | Tracker de visitas con captura de IP |
| `/hash <texto>` | Genera hashes MD5/SHA1/256/512 |
| `/qr <texto>` | Genera código QR |
| `/ai <pregunta>` | Asistente IA (Gemini) |
| `/register` | Registrarse en el bot |
| `/perfil` | Ver perfil propio |

## 📦 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/hackcrist/osint-crist.git
cd osint-crist
```

### 2. Crear entorno virtual (opcional pero recomendado)

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Copia el archivo de ejemplo y edítalo con tus claves:

```bash
cp .env.example .env
```

Edita `.env` y completa al menos:

| Variable | Obligatorio | Descripción |
|----------|-------------|-------------|
| `BOT_TOKEN` | ✅ Sí | Token de @BotFather |
| `OWNER_ID` | ✅ Sí | Tu ID de Telegram |
| `GEMINI_KEY` | ❌ Opcional | Google Gemini AI |
| `HUNTER_KEY` | ❌ Opcional | Hunter.io (email) |
| `VTOTAL_KEY` | ❌ Opcional | VirusTotal (web) |
| `IPLOCATE_KEY` | ❌ Opcional | IPLocate (IP) |

### 5. Iniciar el bot

```bash
python bot.py
```

## 📡 Tracker (captura de IPs)

El tracker requiere un hosting con PHP:

1. Sube `tracker/track.php` a la raíz de tu hosting
2. El link queda: `https://tudominio.com/track.php?c=ID`
3. Los comandos del bot: `/track new <nombre>`, `/track list`, `/track view <nombre>`

## 🔒 Seguridad

- **NUNCA** subas tu `.env` a GitHub (ya está en `.gitignore`)
- Las claves API están siempre en `.env`, nunca en el código
- El tracker guarda los logs **fuera** de `public_html`

## 📁 Estructura del proyecto

```
osint-crist/
├── bot.py                  # Entry point
├── config.py               # Variables de entorno
├── .env                    # 🔴 NO SUBIR A GITHUB
├── .env.example            # Plantilla de configuración
├── requirements.txt        # Dependencias
│
├── core/
│   ├── logger.py           # Logging
│   └── security.py         # Utilidades de seguridad
│
├── database/
│   └── db.py               # SQLite async
│
├── handlers/
│   ├── commands.py         # Menú, help, historial
│   ├── osint_handlers.py   # Comandos OSINT
│   └── auth.py             # Registro, perfil, admin
│
├── modules/                # Módulos de investigación
│   ├── email_lookup.py
│   ├── phone_lookup.py
│   ├── username_search.py
│   ├── person_search.py
│   ├── web_recon.py
│   ├── ip_lookup.py
│   ├── whois_module.py
│   ├── exif_module.py
│   ├── breach_check.py
│   ├── geo_lookup.py
│   ├── spam_check.py
│   ├── fbi_wanted.py
│   ├── ai_assistant.py
│   ├── utils_module.py
│   └── tracker.py
│
├── utils/
│   ├── formatting.py       # Formateo HTML
│   └── validators.py       # Validación de datos
│
└── tracker/
    ├── track.php           # PHP para hosting
    ├── links.json          # 🔴 NO SUBIR
    └── logs/               # 🔴 NO SUBIR
```

## 🛠️ APIs integradas

| API | Uso | Límite gratis |
|-----|-----|---------------|
| ip-api.com | Geolocalización IP | Ilimitado |
| IPLocate | VPN/Proxy/Tor + abuso | 1,000/día |
| Hunter.io | Verificación email y dominio | 25/mes |
| VirusTotal | Escaneo web | 500/día |
| Google Gemini | Asistente IA | 60/min |
| FBI API | Most Wanted | Ilimitado |
| OpenStreetMap | Geocoding inverso | Ilimitado |

## 📄 Licencia

MIT — Uso educativo e investigación.
