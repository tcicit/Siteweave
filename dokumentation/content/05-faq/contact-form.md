---
author: TCI
breadcrumbs: true
date: '2026-03-08'
draft: false
featured_image: ''
layout: doc
release_date: '2026-03-08'
tags:
- FAQ
- HTML
- Documentation
title: Embed a Contact Form
weight: 30
---

[[toc min_headers="3" title="Contents"]]

Since Siteweave generates **static** websites, there is no database or server-side backend to process form data directly. Nevertheless, adding a contact form is straightforward using external form services.

## How It Works

Instead of sending data to your own server, the form submits to an external service provider. The provider processes the entries and forwards them to you by email.

For static sites, open-source contact form solutions or backend-less form providers are ideal. Popular options include self-hosted solutions like Formgate or FormEasy, which process form data via API. Services like Static Forms also allow seamless integration via HTML POST requests to deliver emails without server code.

### Recommended Options for Contact Forms

- **Formgate**: A self-hosted open-source solution that can serve as a single backend instance for multiple static websites.
- **FormEasy**: An open-source library that simplifies receiving form submissions from static pages.
- **Static Forms**: Provides a simple API endpoint for sending emails directly from standard HTML forms.
- **Formspree / form.taxi**: Widely used hosted form services offering free tiers and easy integration.

#### Key Benefits
- **No Backend Required**: Handled completely externally without requiring PHP or Python on your static host.
- **Built-in Security**: Many services include spam protection such as reCAPTCHA or honeypot fields.
- **Simple Integration**: Requires only a standard HTML `<form>` element pointing to the target service URL.

---

## Alternative: Direct Mailto Links

If a dedicated form is not required, you can create a contact page with a direct `mailto:` link or button. Clicking the button opens the visitor's default email client pre-filled with your recipient address and subject line:

```html
<a href="mailto:info@example.com?subject=Inquiry%20via%20Website" class="button">Send Inquiry</a>
```

---

## Alternative: Custom PHP Script

If your web server supports PHP, you can host your own PHP script (such as using [PHPMailer](https://github.com/PHPMailer/PHPMailer)) to handle form submissions directly.

---

## Step-by-Step Guide (Example with Formspree)

### 1. Create an Endpoint

Register at [formspree.io](https://formspree.io) and create a new form. You will receive a URL like: `https://formspree.io/f/YOUR_FORMSPREE_ID`.

### 2. Insert Form into Markdown

You can embed raw HTML directly inside your Siteweave Markdown content:

```html
<form action="https://formspree.io/f/YOUR_FORMSPREE_ID" method="POST" class="contact-form">

  <label>
    Your name:
    <input type="text" name="name" required>
  </label>

  <label>
    Your email:
    <input type="email" name="email" required>
  </label>

  <label>
    Your message:
    <textarea name="message" rows="5" required></textarea>
  </label>

  <button type="submit">Send Message</button>

</form>
```

### 3. Styling (Optional)

Add CSS rules to your project's `assets/css/style.css`:

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
    font-size: 1rem;
}

.contact-form button {
    background-color: #007bff;
    color: white;
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1rem;
}

.contact-form button:hover {
    background-color: #0056b3;
}
```

## Data Protection (GDPR)

[[infobox type="warning" title="GDPR Note"]]
Since form data is sent to an external service provider, ensure this is clearly documented in your **privacy policy**. Check your provider's GDPR compliance and Data Processing Agreements (DPA).
[[/infobox]]