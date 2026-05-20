# 🕵️ OSINT Bot — Investigación de Personas

Bot de Telegram para **OSINT** (Open Source Intelligence) enfocado en **investigación de personas**. Recopila información pública de emails, teléfonos, usuarios, IPs, sitios web y más. 100% gratuito, modular y async.

---

## ¿Cómo funciona el bot?

Cuando ejecutas el bot y hablas con él en Telegram:

1. **Registro obligatorio** — Cualquier comando OSINT requiere que primero te registres con `/register`. Sin registro no puedes investigar nada.
2. **Menú inline** — Envía `/start` y verás un menú con botones. Cada botón te explica cómo usar ese comando.
3. **Usas el comando** — Por ejemplo: `/email usuario@ejemplo.com`
4. **Elbot investiga** — Busca en fuentes públicas y te devuelve los resultados.
5. **Historial guardado** — Todas tus búsquedas se guardan automáticamente. Ve tu historial con `/historial`.

---

## 🚀 Comandos disponibles

### Investigación de contactos

| Comando | Qué hace | Ejemplo |
|---------|----------|---------|
| `/email <correo>` | Analiza un email: verifica servidores MX, busca perfil Gravatar, detecta si es desechable y busca filtraciones públicas | `/email usuario@ejemplo.com` |
| `/domain <dominio>` | Busca emails asociados a un dominio usando Hunter.io | `/domain ejemplo.com` |
| `/phone <número>` | Obtiene país, operador, tipo de línea, zona horaria y ubicación de un número | `/phone +521234567890` |
| `/spam <número>` | Verifica si un número ha sido reportado como spam en Tellows y SpamCalls | `/spam +34612345678` |

### Redes sociales y personas

| Comando | Qué hace | Ejemplo |
|---------|----------|---------|
| `/user <username>` | Busca un nombre de usuario en 30+ plataformas (GitHub, Instagram, TikTok, Reddit, etc.) | `/user midudev` |
| `/person <nombre>` | Busca información de una persona: Wikipedia, DuckDuckGo, Google Dorks y enlaces a redes | `/person Lionel Messi` |
| `/fbi <nombre>` | Busca en la base de datos del FBI Most Wanted. Usa `/fbi top` para ver los 10 más buscados | `/fbi Donald` |

### Red e infraestructura

| Comando | Qué hace | Ejemplo |
|---------|----------|---------|
| `/ip [dirección]` | Geolocalización de IP: país, ISP, coordenadas, mapa. Además detecta si es VPN, Proxy, Tor o Hosting, y muestra datos de abuso | `/ip 8.8.8.8` |
| `/web <url>` | Escanea un sitio web: cabeceras HTTP, DNS, SSL, tecnologías, seguridad, subdominios, Wayback Machine y VirusTotal | `/web https://ejemplo.com` |
| `/whois <dominio>` | Consulta WHOIS de un dominio: registrador, fechas de creación/expiración, nameservers | `/whois google.com` |

### Geolocalización

| Comando | Qué hace | Ejemplo |
|---------|----------|---------|
| `/geo <lat,lng>` | Convierte coordenadas GPS en dirección completa con calle, ciudad, país y enlaces a mapas | `/geo 40.4168, -3.7038` |
| `/geo <+teléfono>` | Obtiene ubicación aproximada de un número telefónico (país, operador, zona horaria) | `/geo +34612345678` |

### Archivos y utilidades

| Comando | Qué hace | Ejemplo |
|---------|----------|---------|
| `/exif` | Extrae metadatos EXIF de una foto (cámara, GPS, fecha). Responde a una foto con este comando | Envía una foto y responde con /exif |
| `/hash <texto>` | Genera hashes MD5, SHA1, SHA256, SHA512 de cualquier texto | `/hash Hola Mundo` |
| `/qr <texto>` | Genera un código QR con el texto o URL que quieras | `/qr https://t.me/mibot` |

### Seguridad y filtraciones

| Comando | Qué hace | Ejemplo |
|---------|----------|---------|
| `/breach <email>` | Busca si un email o usuario aparece en filtraciones públicas (Leak-Check, Pastebin, IntelX) | `/breach usuario@ejemplo.com` |

### Tracker de visitas (captura IP)

| Comando | Qué hace | Ejemplo |
|---------|----------|---------|
| `/track new <nombre>` | Crea un link de rastreo. Cuando alguien lo abre, captura su IP, ubicación, ISP y navegador | `/track new enlace1` |
| `/track list` | Muestra todos los links que has creado | `/track list` |
| `/track view <nombre>` | Muestra todas las visitas registradas en ese link con IP, ubicación, fecha, etc. | `/track view enlace1` |

**¿Cómo funciona el tracker?**
1. Creas un link con `/track new prueba`
2. El bot responde al instante con un link: `https://tudominio.com/track.php?c=abc123`
3. Compartes ese link con la persona (por Telegram, SMS, email, etc.)
4. Cuando la persona abre el link, se registra automáticamente su IP, país, ISP, navegador y hora
5. Días después ejecutas `/track view prueba` y ves todas las IPs que cayeron
6. La persona solo ve una página **404** falsa, no sabe que fue rastreada

Requisito: tener un hosting con PHP para subir `tracker/track.php`.

### Asistente IA

| Comando | Qué hace | Ejemplo |
|---------|----------|---------|
| `/ai <pregunta>` | Pregunta cualquier cosa a la IA de Google Gemini. Ideal para analizar resultados OSINT | `/ai analiza esta IP: 8.8.8.8` |

### Cuenta y administración

| Comando | Quién usa | Qué hace |
|---------|-----------|----------|
| `/register` | Todos | Registrarse en el bot (obligatorio para usar comandos OSINT) |
| `/perfil` | Todos | Ver tu información de registro |
| `/historial` | Todos | Ver tus últimas 10 búsquedas |
| `/usuarios` | Owner | Lista de usuarios registrados |
| `/estadisticas` | Owner | Estadísticas del bot |
| `/aprobar <id>` | Owner | Activar un usuario manualmente |
| `/ban <id>` | Owner | Banear un usuario |

---

## 📦 Instalación

### PC / VPS (Linux, Windows, Mac)

#### 1. Obtener el código

```bash
git clone https://github.com/hackcrist/osint-crist.git
cd osint-crist
```

#### 2. (Opcional) Crear entorno virtual

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

#### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

#### 4. Configurar variables de entorno

```bash
cp .env.example .env
```

Abre `.env` con cualquier editor y completa al menos:

| Variable | Obligatorio | Dónde conseguirla |
|----------|-------------|-------------------|
| `BOT_TOKEN` | ✅ Sí | [@BotFather](https://t.me/BotFather) en Telegram |
| `OWNER_ID` | ✅ Sí | Tu ID numérico de Telegram ([@userinfobot](https://t.me/userinfobot)) |
| `GEMINI_KEY` | ❌ Opcional | [Google AI Studio](https://aistudio.google.com/) (gratis) |
| `HUNTER_KEY` | ❌ Opcional | [Hunter.io](https://hunter.io/) (25 req/mes gratis) |
| `VTOTAL_KEY` | ❌ Opcional | [VirusTotal](https://www.virustotal.com/) (500 req/día gratis) |
| `IPLOCATE_KEY` | ❌ Opcional | [IPLocate.io](https://www.iplocate.io/) (1,000 req/día gratis) |

> **Importante:** El archivo `.env` contiene tus claves personales. **NUNCA** se sube a GitHub porque está en `.gitignore`.

#### 5. Iniciar el bot

```bash
python bot.py
```

Si todo está bien, verás: `Bot conectado: @tuBot (ID: 123456)`.

---

### 📱 Termux (Android)

#### 1. Instalar Termux

Descarga Termux desde **[F-Droid](https://f-droid.org/packages/com.termux/)**. NO uses Google Play (está desactualizado).

#### 2. Instalar Python y git

```bash
pkg update && pkg upgrade -y
pkg install python git -y
```

#### 3. Clonar e instalar

```bash
git clone https://github.com/hackcrist/osint-crist.git
cd osint-crist
pip install -r requirements.txt
```

Si hay errores con `dnspython` o `Pillow`, instala dependencias adicionales:

```bash
pkg install libffi libsodium openblas -y
```

#### 4. Configurar .env

```bash
cp .env.example .env
nano .env
```

Pon tu `BOT_TOKEN` y `OWNER_ID`.

#### 5. Ejecutar

```bash
python bot.py
```

Para mantenerlo corriendo en segundo plano:

```bash
pkg install tmux -y
tmux
python bot.py
# Ctrl+B, luego D para salir de tmux
# El bot sigue corriendo
```

---

## 📡 Tracker (captura de IPs)

El tracker es la función más potente del bot para OSINT. Te permite saber **quién, desde dónde y con qué dispositivo** abre un link que tú compartes.

### Cómo configurarlo

Necesitas un hosting con PHP (Hostinger, 000WebHost, etc.):

1. Sube el archivo `tracker/track.php` a la raíz de tu hosting (carpeta `public_html`)
2. El link de rastreo quedará: `https://tudominio.com/track.php?c=ID`
3. Los logs se guardan automáticamente **fuera** de `public_html` por seguridad

### Cómo usarlo en el bot

```
/track new prueba        → Crea el link
/track list              → Lista todos tus links
/track view prueba       → Muestra las visitas (IP, ubicación, navegador, fecha)
```

### Datos que captura por cada visita

- Dirección IP (IPv4 e IPv6)
- País y ciudad aproximada
- Proveedor de Internet (ISP)
- Navegador y sistema operativo
- Fecha y hora exacta
- Idioma del navegador
- Desde dónde llegó (referer)

---

## 🔒 Seguridad y privacidad

| Qué | Dónde está | ¿Se sube a GitHub? |
|-----|------------|-------------------|
| Token del bot | `.env` | ❌ No (`.gitignore`) |
| Claves API | `.env` | ❌ No |
| Historial de búsquedas | `database/bot.db` | ❌ No |
| IPs capturadas | `tracker/logs/` | ❌ No |
| IDs de tracker | `tracker/links.json` | ❌ No |
| Código fuente | `.py` | ✅ Sí |
| Plantilla `.env` | `.env.example` | ✅ Sí (sin claves) |

---

## 📁 Estructura del proyecto

```
osint-crist/
├── bot.py                  # Punto de entrada – inicia el bot
├── config.py               # Lee las variables del .env
├── .env                    # 🔴 Tus claves (NO se sube a GitHub)
├── .env.example            # Plantilla para configurar
├── requirements.txt        # Dependencias Python
├── LICENSE                 # Licencia MIT
│
├── core/
│   ├── logger.py           # Registro de eventos (logs)
│   └── security.py         # Utilidades de seguridad
│
├── database/
│   └── db.py               # Base de datos SQLite (async)
│
├── handlers/
│   ├── commands.py         # Menú inline, /start, /help, /historial
│   ├── osint_handlers.py   # Todos los comandos OSINT
│   └── auth.py             # /register, /perfil, admin
│
├── modules/                # Lógica de cada investigación
│   ├── email_lookup.py     # Email: MX, Gravatar, desechable, Hunter
│   ├── phone_lookup.py     # Teléfono: país, operador, zona horaria
│   ├── username_search.py  # Usuario en 30+ plataformas
│   ├── person_search.py    # Persona: Wikipedia, DuckDuckGo, dorks
│   ├── web_recon.py        # Web: DNS, SSL, subdominios, VirusTotal
│   ├── ip_lookup.py        # IP: geolocalización + detección VPN
│   ├── whois_module.py     # WHOIS de dominios
│   ├── exif_module.py      # Metadatos EXIF de imágenes
│   ├── breach_check.py     # Filtraciones en bases públicas
│   ├── geo_lookup.py       # Geocodificación inversa (OSM)
│   ├── spam_check.py       # Reputación de números spam
│   ├── fbi_wanted.py       # FBI Most Wanted API
│   ├── ai_assistant.py     # Asistente Google Gemini
│   ├── utils_module.py     # Hashes y QR
│   └── tracker.py          # Cliente del tracker PHP
│
├── utils/
│   ├── formatting.py       # Formato HTML para Telegram
│   └── validators.py       # Validación de emails, queries
│
└── tracker/
    ├── track.php           # PHP para hosting (captura visitas)
    ├── links.json          # 🔴 IDs de tus links (NO se sube)
    └── logs/               # 🔴 IPs capturadas (NO se sube)
```

---

## 🛠️ APIs integradas

| API | Para qué sirve | Límite gratis | ¿Necesita key? |
|-----|---------------|---------------|----------------|
| ip-api.com | Geolocalización de IPs | Ilimitado | ❌ No |
| IPLocate.io | Detección VPN/Proxy/Tor + abuso | 1,000/día | ✅ Opcional |
| Hunter.io | Verificar emails y buscar por dominio | 25/mes | ✅ Opcional |
| VirusTotal | Escanear URLs en busca de malware | 500/día | ✅ Opcional |
| Google Gemini | Asistente IA para análisis | 60/min | ✅ Opcional |
| FBI API | Consulta de más buscados | Ilimitado | ❌ No |
| OpenStreetMap | Convertir coordenadas a dirección | Ilimitado | ❌ No |
| Tellows | Reputación de números spam | Ilimitado | ❌ No |
| SpamCalls | Reportes de spam telefónico | Ilimitado | ❌ No |
| crt.sh | Descubrimiento de subdominios | Ilimitado | ❌ No |
| Wayback Machine | Historial de versiones de sitios web | Ilimitado | ❌ No |

Las APIs sin key funcionan **sin configuración**. Las que requieren key son opcionales y mejoran los resultados.

---

## 📄 Licencia

MIT — Uso educativo e investigación. Cada quien es responsable del uso que le dé a esta herramienta.
