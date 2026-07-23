import os
import frontmatter

'''
Metadaten für den Project Launcher / Worker
name: Name des Workers, wird im Menü angezeigt
description: Kurze Beschreibung, was der Worker macht
category: Kategorie, z.B. "project", "content", "utility" (kann für spätere Filterung genutzt werden)
hidden: Wenn True, wird der Worker nicht im Menü angezeigt, aber er kann intern von anderen Workern aufgerufen werden

'''

name = "Tag Collector"
# Versteckt im Menü (wird intern genutzt)
hidden = True 

def run(context):
    content_dir = context.get('content_dir', 'content')
    tags = set()
    
    for root, _, files in os.walk(content_dir):
        for file in files:
            if file.endswith(('.md', '.markdown')):
                try:
                    post = frontmatter.load(os.path.join(root, file))
                    if post.metadata.get('tags'):
                        t = post.metadata['tags']
                        if isinstance(t, list):
                            tags.update(t)
                        elif isinstance(t, str):
                            tags.add(t)
                except:
                    pass
    return sorted(list(tags))

