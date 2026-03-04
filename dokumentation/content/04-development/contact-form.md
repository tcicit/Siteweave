---
author: TCI
breadcrumbs: true
date: '2026-02-22'
draft: false
featured_image: ''
layout: doc
release_date: '2026-02-22'
tags:
- Anleitung
- HTML
- Dokumentation
- Entwicklung
title: Embed contact form
weight: 110
---


Since this project is a generator for static websites, there is no database and no PHP backend code that can process form data directly.

Nevertheless, it is very easy to integrate a contact form. The solution is to use external form services.

## How it works

Instead of sending the data to your own server, the form sends the data to an external service provider. This provider processes the entries and sends them to you by email.

Popular providers are:

* **Formspree** (very simple, free basic plan)
* **Netlify Forms** (if you host with Netlify)
* **Getform**

## Instructions (example with Formspree)

Here we show you how to set up a form with **Formspree**.

### 1. Create endpoint

Register at formspree.io and create a new form. You will receive a URL that looks like this: `https://formspree.io/f/deine-id`.

### 2. Insert form into Markdown

You can easily use HTML code in Markdown files. Copy the following code to the place where you want the form to appear and replace the URL in `action` with your own.

html
<form action="https://formspree.io/f/DEINE_FORMSPREE_ID" method="POST" class="contact-form">
  
  <label>
    Your email:
    <input type="email" name="email" required>
  </label>
  
  <label>
    Your message:
    <textarea name="message" required></textarea>
  </label>
  
  <button type="submit">Send</button>
</form>
```

### 3. Styling (Optional)

To make the form look good, you can add some CSS to your `assets/css/style.css` (or your own CSS file):

```css
.contact-form {
  display: flex;
  flex-direction: column;
  max-width: 500px;
  gap: 1rem;
}

.contact-form label {
  display: flex;
  flex-direction: column;
  font-weight: bold;
}

.contact-form input,
.contact-form textarea {
  padding: 0.5rem;
  margin-top: 0.25rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.contact-form button {
  background-color: #007bff;
  color: white;
  padding: 0.75rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.contact-form button:hover {
  background-color: #0056b3;
}
```

## Data protection (GDPR)

Since the data is sent to an external service provider (often in the US), you should mention this in your privacy policy. Many providers now also offer GDPR-compliant options or data processing agreements (DPA).

