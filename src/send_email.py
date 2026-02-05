import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import os
from dotenv import load_dotenv
import base64

load_dotenv()

def send_email_report(html_content, charts_dict=None, subject="📊 Weekly Economic Report"):
    """Send HTML email via Gmail SMTP with inline images"""
    
    sender_email = os.getenv('EMAIL')
    sender_password = os.getenv('EMAIL_PASSWORD')
    recipient_email = sender_email  # Sending to yourself
    
    if not sender_email or not sender_password:
        print("✗ Email credentials not found in .env file")
        return False
    
    # Create message
    message = MIMEMultipart('related')
    message['Subject'] = subject
    message['From'] = sender_email
    message['To'] = recipient_email
    
    # Helper function to create clean CID
    def create_cid(name):
        return name.replace(' ', '_').replace('(', '').replace(')', '').replace('-', '_')
    
    # Replace base64 images with CID references
    if charts_dict:
        for chart_name, base64_data in charts_dict.items():
            cid = create_cid(chart_name)
            html_content = html_content.replace(
                f'data:image/png;base64,{base64_data}',
                f'cid:{cid}'
            )
    
    # Attach HTML content with UTF-8 encoding
    html_part = MIMEText(html_content, 'html', 'utf-8')
    message.attach(html_part)
    
    # Attach images as inline
    if charts_dict:
        for chart_name, base64_data in charts_dict.items():
            cid = create_cid(chart_name)
            image_data = base64.b64decode(base64_data)
            image = MIMEImage(image_data)
            image.add_header('Content-ID', f'<{cid}>')
            image.add_header('Content-Disposition', 'inline', filename=f'{cid}.png')
            message.attach(image)
    
    try:
        # Connect to Gmail SMTP server
        print("Connecting to Gmail SMTP server...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        
        # Login
        print("Logging in...")
        server.login(sender_email, sender_password)
        
        # Send email
        print(f"Sending email to {recipient_email}...")
        server.send_message(message)
        server.quit()
        
        print(f"✓ Email sent successfully to {recipient_email}!")
        return True
        
    except Exception as e:
        print(f"✗ Error sending email: {str(e)}")
        return False
    
if __name__ == '__main__':
    # Test email sending
    from fetch_data import EconomicDataFetcher
    from generate_report import generate_html_report
    
    print("Fetching data...")
    fetcher = EconomicDataFetcher(use_cache=True)
    data = fetcher.fetch_all_data()
    
    print("\nGenerating report...")
    html, charts = generate_html_report(data, include_charts=True)  # Unpack the tuple
    
    print("\nSending email...")
    send_email_report(html, charts_dict=charts)