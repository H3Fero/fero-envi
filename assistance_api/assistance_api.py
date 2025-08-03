from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from fastapi.middleware.cors import CORSMiddleware
import pymysql
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration email (via variables d'environnement pour la sécurité)
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "h3fero@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "yehq kekk jxnc lhmg")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "assistance@envi-fero.h3fero.com")
SMTP_TO_EMAIL = os.getenv("SMTP_TO_EMAIL", "h3fero@gmail.com")

# Attendre que MySQL soit prêt
time.sleep(5)

# Connexion MySQL
try:
    db = pymysql.connect(
        host="mysql",
        user="root",
        password="password",
        database="eurostar",
        cursorclass=pymysql.cursors.DictCursor
    )
except Exception as e:
    print(f"Erreur connexion MySQL: {e}")
    db = None

class AssistanceForm(BaseModel):
    nom: str
    prenom: str
    genre: str
    age: int
    email: EmailStr
    handicap: str
    autre_handicap: str = None

def generate_ticket_number():
    """Génère un numéro de billet unique basé sur la date et l'heure"""
    now = datetime.now()
    return f"{now.strftime('%Y%m%d')}{now.strftime('%H%M%S')}"

def send_assistance_email(data: AssistanceForm, ticket_number: str):
    """Envoie un email d'assistance avec le format professionnel demandé"""
    
    # Sujet de l'email
    subject = f"Demande Assistance - {data.nom.upper()} {data.prenom.capitalize()}"
    
    # Corps de l'email (format HTML pour un meilleur rendu)
    html_body = f"""
    <html>
    <head></head>
    <body>
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #1e3a8a; border-bottom: 2px solid #1e3a8a; padding-bottom: 10px;">
                Demande Assistance - {data.nom.upper()} {data.prenom.capitalize()}
            </h2>
            
            <div style="background-color: #f8fafc; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3 style="color: #374151; margin-top: 0;">Assistance FERO-ENVIE</h3>
                <p><strong>À :</strong> Service Assistance</p>
            </div>
            
            <div style="margin: 20px 0;">
                <p>Bonjour,</p>
                <p><strong>{data.nom.upper()} {data.prenom.capitalize()}</strong> au billet <strong>{ticket_number}</strong>, demande votre assistance.</p>
                
                <div style="background-color: #f3f4f6; padding: 15px; border-radius: 5px; margin: 15px 0;">
                    <h4 style="margin-top: 0; color: #374151;">Détails de la demande :</h4>
                    <ul style="margin: 10px 0;">
                        <li><strong>Nom :</strong> {data.nom.upper()}</li>
                        <li><strong>Prénom :</strong> {data.prenom.capitalize()}</li>
                        <li><strong>Genre :</strong> {data.genre}</li>
                        <li><strong>Email :</strong> {data.email}</li>
                        <li><strong>Type d'assistance :</strong> {data.handicap}</li>
                        {f'<li><strong>Précisions :</strong> {data.autre_handicap}</li>' if data.autre_handicap else ''}
                    </ul>
                </div>
                
                <p>Cordialement,<br/>
                <em>Système automatisé FERO-ENVIE</em></p>
            </div>
            
            <div style="border-top: 1px solid #e5e7eb; padding-top: 15px; margin-top: 30px;">
                <p style="font-size: 12px; color: #6b7280;">
                    Cet email a été généré automatiquement le {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}<br/>
                    Ne pas répondre à cette adresse.
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Version texte simple (fallback)
    text_body = f"""
Demande Assistance - {data.nom.upper()} {data.prenom.capitalize()}

Assistance FERO-ENVIE

Bonjour,

{data.nom.upper()} {data.prenom.capitalize()} au billet {ticket_number}, demande votre assistance.

Détails de la demande :
- Nom : {data.nom.upper()}
- Prénom : {data.prenom.capitalize()}
- Genre : {data.genre}
- Email : {data.email}
- Type d'assistance : {data.handicap}
{f'- Précisions : {data.autre_handicap}' if data.autre_handicap else ''}

Cordialement,
Système automatisé FERO-ENVIE
    """
    
    try:
        # Création du message multipart (HTML + texte)
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = SMTP_FROM_EMAIL
        msg['To'] = SMTP_TO_EMAIL
        
        # Ajouter les versions texte et HTML
        part1 = MIMEText(text_body, 'plain', 'utf-8')
        part2 = MIMEText(html_body, 'html', 'utf-8')
        
        msg.attach(part1)
        msg.attach(part2)
        
        # Envoi via Gmail (avec TLS)
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Activer le chiffrement TLS
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
            
        print(f" Email envoyé avec succès pour {data.nom} {data.prenom} (billet {ticket_number})")
        return True
        
    except Exception as e:
        print(f" Erreur lors de l'envoi de l'email: {e}")
        return False

@app.get("/")
async def root():
    return {"message": "API Assistance Eurostar - Service de demandes d'assistance"}

@app.get("/health")
async def health():
    """Endpoint de santé pour vérifier le service"""
    mysql_status = "OK" if db else "ERROR"
    return {
        "status": "healthy",
        "service": "assistance-api",
        "mysql": mysql_status,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/assistance")
async def assistance(data: AssistanceForm):
    """Enregistre une demande d'assistance et envoie un email de notification"""
    
    if not db:
        raise HTTPException(status_code=500, detail="Erreur de connexion à la base de données")
    
    # Génération d'un numéro de billet unique
    ticket_number = generate_ticket_number()
    
    try:
        # Insertion en base de données
        with db.cursor() as cursor:
            sql = """
                INSERT INTO assistance (nom, prenom, genre, age, email, handicap, autre_handicap, ticket_number, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                data.nom, 
                data.prenom, 
                data.genre, 
                data.age, 
                data.email, 
                data.handicap, 
                data.autre_handicap,
                ticket_number,
                datetime.now()
            ))
        db.commit()
        
        # Tentative d'envoi d'email
        email_sent = send_assistance_email(data, ticket_number)
        
        response = {
            "message": "Demande d'assistance enregistrée avec succès",
            "ticket_number": ticket_number,
            "nom_complet": f"{data.prenom.capitalize()} {data.nom.upper()}",
            "email_notification": "envoyé" if email_sent else "échec (demande tout de même enregistrée)"
        }
        
        if not email_sent:
            response["warning"] = "L'email de notification n'a pas pu être envoyé, mais votre demande est bien enregistrée"
        
        return response
        
    except Exception as e:
        db.rollback()
        print(f"Erreur lors de l'enregistrement: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de l'enregistrement de la demande")

@app.get("/assistance/list")
async def list_assistance():
    """Liste toutes les demandes d'assistance (pour admin/debug)"""
    
    if not db:
        raise HTTPException(status_code=500, detail="Erreur de connexion à la base de données")
    
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM assistance ORDER BY created_at DESC LIMIT 50")
            results = cursor.fetchall()
        
        return {
            "total": len(results),
            "demandes": results
        }
        
    except Exception as e:
        print(f"Erreur lors de la récupération: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des demandes")