import random

def encode_entities(text):
    """
    Verschleiert Text durch Umwandlung in HTML-Entities (Mix aus Hex und Dezimal).
    Dies macht den Text für einfache Bots unlesbar, wird aber vom Browser korrekt angezeigt.
    """
    if not text:
        return ""
    encoded = ""
    for char in text:
        # Zufällige Entscheidung zwischen dezimaler und hexadezimaler Kodierung
        if random.choice([True, False]):
            encoded += f"&#{ord(char)};"
        else:
            encoded += f"&#x{ord(char):x};"
    return encoded

def handle(content, args, context, env):
    """
    Plugin Name: Obfuscate
    Description: Obfuscates sensitive data like emails, phone numbers, and addresses to protect against bots.
    Syntax: 
      [[obfuscate email="info@example.com"]]
      [[obfuscate phone="+49 123 456"]]
      [[obfuscate address="Sample Street 1"]]
      [[obfuscate]]Any text[[/obfuscate]]

    Parameters:
      - email: Email address (creates a mailto link).
      - phone: Phone number (creates a tel link).
      - address: Address or text (only encoded).
      - text: Alias for address.
      - label: Optional link text (for email/phone).
      - subject: Optional subject (for email).
      
    Examples:
      [[obfuscate email="info@example.com"]]
      [[obfuscate phone="+49 123 456"]]
      [[obfuscate address="Sample Street 1"]]
      [[obfuscate]]This is some sensitive text.[[/obfuscate]]
         Obfuscates the provided email, phone number, address, or any text between the tags to make it less accessible to bots.  

    Result:
        HTML entities encoded string or link.
    """
    
    email = args.get('email')
    phone = args.get('phone')
    text = args.get('address') or args.get('text')
    label = args.get('label')
    subject = args.get('subject')
    
    # Inhalt zwischen den Tags hat Vorrang als Label (bei Links) oder Text
    if content:
        content = content.strip()
        if email or phone:
            if not label:
                label = content
        else:
            text = content

    if email:
        encoded_email = encode_entities(email)
        display_text = encode_entities(label) if label else encoded_email
        
        href = f"mailto:{email}"
        if subject:
            href += f"?subject={subject}"
        
        encoded_href = encode_entities(href)
        return f'<a href="{encoded_href}">{display_text}</a>'

    elif phone:
        # Bereinige Nummer für das href-Attribut (nur Ziffern und +)
        clean_phone = "".join(c for c in phone if c.isdigit() or c == '+')
        encoded_href = encode_entities(f"tel:{clean_phone}")
        
        display_text = encode_entities(label) if label else encode_entities(phone)
        
        return f'<a href="{encoded_href}">{display_text}</a>'

    elif text:
        return encode_entities(text)
    
    return ""