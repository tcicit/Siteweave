import os
import re
import logging
from PIL import Image
from workers.logger_config import configure_logger

# --- Default configuration (fallback) ---
# Suffix for compressed files. An image 'bild.jpg' becomes 'bild-compressed.jpg'.
DEFAULT_COMPRESSED_SUFFIX = "-compressed"
# JPEG quality (0-100, higher is better quality but larger). 85 is a good compromise.
DEFAULT_JPEG_QUALITY = 85
# PNG compression level (0-9, higher means stronger compression but slower).
DEFAULT_PNG_COMPRESSION = 6
# File extensions to process.
DEFAULT_IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png')

# Regex to find Markdown image links
IMAGE_LINK_RE = re.compile(r'!\[(.*?)\]\((.*?)\)')

logger = logging.getLogger("compress_images")

def compress_images(content_dir, config=None):
    """
    Walks the content directory, finds all images and creates compressed versions.
    """
    logger.info(f"Phase 1: Suche und komprimiere Bilder in '{content_dir}'...")
    
    if config is None: config = {}
    img_config = config.get('image_compression', {})
    
    suffix = img_config.get('compressed_suffix', DEFAULT_COMPRESSED_SUFFIX)
    jpeg_quality = img_config.get('jpeg_quality', DEFAULT_JPEG_QUALITY)
    png_compression = img_config.get('png_compression', DEFAULT_PNG_COMPRESSION)
    extensions = tuple(img_config.get('extensions', DEFAULT_IMAGE_EXTENSIONS))

    compressed_count = 0
    skipped_count = 0

    for root, _, files in os.walk(content_dir):
        for filename in files:
            if not filename.lower().endswith(extensions):
                continue

            # Skip already compressed images
            if suffix in filename:
                continue
            
            original_path = os.path.join(root, filename)
            base, ext = os.path.splitext(filename)
            compressed_filename = f"{base}{suffix}{ext}"
            compressed_path = os.path.join(root, compressed_filename)

            # Skip if the compressed version already exists
            if os.path.exists(compressed_path):
                skipped_count += 1
                continue

            try:
                with Image.open(original_path) as img:
                    original_size = os.path.getsize(original_path)
                    rel_path = os.path.relpath(original_path, content_dir)
                    
                    if ext.lower() in ['.jpg', '.jpeg']:
                        # Strip metadata to further reduce file size
                        img.save(compressed_path, 'jpeg', quality=jpeg_quality, optimize=True, progressive=True)
                    elif ext.lower() == '.png':
                        # Convert to a mode that supports better compression
                        img = img.convert("P", palette=Image.ADAPTIVE, colors=256)
                        img.save(compressed_path, 'png', optimize=True, compression_level=png_compression)
                    
                    compressed_size = os.path.getsize(compressed_path)
                    reduction = (original_size - compressed_size) / original_size * 100
                    logger.info(f"  - Compressed: {rel_path} -> Size: {original_size/1024:.1f} KB -> {compressed_size/1024:.1f} KB ({reduction:.1f}% reduced)")
                    compressed_count += 1

            except Exception as e:
                logger.error(f"Could not process image '{original_path}': {e}")

    if compressed_count == 0 and skipped_count == 0:
        logger.info("  -> No new images found to compress.")
    elif compressed_count == 0 and skipped_count > 0:
        logger.info(f"  -> No new images found to compress. {skipped_count} compressed versions already existed.")
    else:
        logger.info(f"Compression complete. {compressed_count} images compressed, {skipped_count} skipped.")


def update_markdown_links(content_dir, config=None):
    """
    Walk through all Markdown files and update image links
    so they point to the compressed versions.
    """
    logger.info("Phase 2: Updating links in Markdown files...")
    
    if config is None: config = {}
    img_config = config.get('image_compression', {})
    suffix = img_config.get('compressed_suffix', DEFAULT_COMPRESSED_SUFFIX)
    extensions = tuple(img_config.get('extensions', DEFAULT_IMAGE_EXTENSIONS))

    updated_files_count = 0
    
    for root, _, files in os.walk(content_dir):
        for filename in files:
            if not filename.endswith(('.md', '.markdown')):
                continue

            file_path = os.path.join(root, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content

                def replacer(match):
                    alt_text, link_path = match.groups()
                    is_local_image = link_path.lower().endswith(extensions) and not link_path.startswith(('http', '/'))
                    is_not_compressed = suffix not in link_path

                    if not (is_local_image and is_not_compressed):
                        return match.group(0)

                    base, ext = os.path.splitext(link_path)
                    compressed_link_path = f"{base}{suffix}{ext}"
                    compressed_file_abs_path = os.path.abspath(os.path.join(os.path.dirname(file_path), compressed_link_path))

                    if os.path.exists(compressed_file_abs_path):
                        return f"![{alt_text}]({compressed_link_path})"
                    return match.group(0)

                new_content = IMAGE_LINK_RE.sub(replacer, content)

                if new_content != original_content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    logger.info(f"  - Updated: {os.path.relpath(file_path, content_dir)}")
                    updated_files_count += 1
            except Exception as e:
                logger.warning(f"Could not process file: '{file_path}': {e}")

    if updated_files_count > 0:
        logger.info(f"Link update complete. {updated_files_count} files modified.")
    else:
        logger.info("  -> No links found to update.")

def run(context):
    content_dir = context.get('content_dir', 'content')
    project_root = context.get('project_root', '.')
    config = context.get('config', {})
    configure_logger("compress_images", project_root)
    
    compress_images(content_dir, config)
    update_markdown_links(content_dir, config)
    return "Bilder-Komprimierung abgeschlossen."