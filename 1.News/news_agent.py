import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google import genai
from google.genai import types

# ── Config ───────────────────────────────────────────────
RECIPIENT_EMAIL = os.environ["GMAIL_USER"]
TOPICS = [
    "IA y Machine Learning",
    "Espacio y astronomía",
    "Gadgets y hardware",
    "Programación y software",
    "Biología y medicina",
    "Física y matemáticas",
]

# ── Llamada a Gemini con Google Search ───────────────────
def get_news() -> str:
    client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
    today = datetime.now().strftime("%d de %B de %Y")
    topics_str = ", ".join(TOPICS)

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=f"""Hoy es {today}. Busca las 10 noticias más importantes, virales 
y novedosas de las últimas 24 horas en estos temas: {topics_str}.

Responde ÚNICAMENTE en este formato HTML, sin texto adicional ni explicaciones:

<ul>
  <li><a href="URL_REAL">Titular de la noticia</a> — Fuente</li>
</ul>

Reglas:
- Solo noticias de las últimas 24 horas
- URLs reales y verificadas
- Prioriza fuentes reconocidas (The Verge, Nature, Wired, ArsTechnica, MIT Tech Review, etc.)
- Titulares en español
- Sin markdown, solo HTML limpio""",
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())],
            temperature=0.3,
        )
    )

    return response.text or "<p>No se pudieron obtener noticias hoy.</p>"


# ── Construir el email HTML ───────────────────────────────
def build_email(news_html: str) -> str:
    today = datetime.now().strftime("%A, %d de %B de %Y")
    return f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{ font-family: -apple-system, sans-serif; max-width: 600px;
            margin: 0 auto; padding: 20px; color: #1a1a1a; }}
    h1   {{ font-size: 20px; font-weight: 600; margin-bottom: 4px; }}
    p.date {{ color: #666; font-size: 13px; margin-bottom: 24px; }}
    ul   {{ padding-left: 0; list-style: none; }}
    li   {{ padding: 10px 0; border-bottom: 1px solid #eee; font-size: 15px; }}
    li:last-child {{ border-bottom: none; }}
    a    {{ color: #0070f3; text-decoration: none; font-weight: 500; }}
    a:hover {{ text-decoration: underline; }}
  </style>
</head>
<body>
  <h1>🔭 Noticias de Ciencia y Tecnología</h1>
  <p class="date">{today}</p>
  {news_html}
  <p style="margin-top:32px; font-size:12px; color:#999;">
    Generado automáticamente con Gemini · GitHub Actions
  </p>
</body>
</html>
"""


# ── Enviar el email ───────────────────────────────────────
def send_email(html_content: str):
    gmail_user = os.environ["GMAIL_USER"]
    gmail_pass = os.environ["GMAIL_APP_PASSWORD"]
    today      = datetime.now().strftime("%d/%m/%Y")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🔭 Noticias Tech & Ciencia — {today}"
    msg["From"]    = gmail_user
    msg["To"]      = RECIPIENT_EMAIL
    msg.attach(MIMEText(html_content, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_user, gmail_pass)
        server.sendmail(gmail_user, RECIPIENT_EMAIL, msg.as_string())
    print(f"✓ Email enviado a {RECIPIENT_EMAIL}")


# ── Main ─────────────────────────────────────────────────
if __name__ == "__main__":
    print("Buscando noticias con Gemini...")
    news = get_news()
    print("Construyendo email...")
    html = build_email(news)
    print("Enviando...")
    send_email(html)