import smtplib,logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

log=logging.getLogger("helper")

def send_html_email(subject:str, html_body:str, to_addresses:str,from_box:str="neco@zlkl.tech",box_pwd="",host:str="mail.zlkl.tech",port:int=587)->bool:
    """Odešle mail

    Args:
        subject (str): Předmět
        html_body (str): Body
        to_addresses (str): mail adresa nebo seznam adres oddělených čárkou
    """
    
    # Vytvoření e-mailové zprávy
    msg = MIMEMultipart()
    msg['From'] = from_box
    msg['To'] = to_addresses
    msg['Subject'] = subject
    
    try:
        # Přidání HTML těla e-mailu
        msg.attach(MIMEText(html_body, 'html'))
        
        # Nastavení SMTP serveru - pro lokální Postfix použijte localhost
        server = smtplib.SMTP(host, port)
        server.starttls()
        server.login(from_box, box_pwd)
        
        text = msg.as_string()
        
        # vytvoř list a sannitizuj 
        to_addresses = [email.strip() for email in to_addresses.split(',')]
        server.sendmail(from_box, to_addresses, text)
        
        # Ukončení spojení
        server.quit()
        log.info(f"Email byl odeslán na adresy: {to_addresses}")
        return True
    except Exception as e:
        log.error(f"Chyba při odesílání emailu: {e}")
        return False
    