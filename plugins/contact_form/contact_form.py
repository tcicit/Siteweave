def handle(content, args, context, env):
    """
    Generiert ein Kontaktformular (Standard: Formspree).
    
    Syntax: [[contact_form email="DEINE_FORMSPREE_ID"]]
    
    Optionale Parameter:
    - label_email: Beschriftung für das E-Mail Feld
    - label_message: Beschriftung für das Textfeld
    - label_button: Beschriftung für den Senden-Button
    """
    # Das 'email' Argument wird als Formspree-ID interpretiert
    form_id = args.get('email')
    
    if not form_id:
        return '<div style="color: red; border: 1px solid red; padding: 10px;">Error: contact_form plugin requires "email" (Formspree ID).</div>'

    # Texte für Labels (mit Standards)
    label_email = args.get('label_email', 'Deine E-Mail:')
    label_message = args.get('label_message', 'Deine Nachricht:')
    label_button = args.get('label_button', 'Senden')

    # HTML generieren
    html = f"""
    <form action="https://formspree.io/f/{form_id}" method="POST" class="contact-form">
      <label>
        {label_email}
        <input type="email" name="email" required>
      </label>
      
      <label>
        {label_message}
        <textarea name="message" rows="5" required></textarea>
      </label>
      
      <button type="submit">{label_button}</button>
    </form>
    """
    return html