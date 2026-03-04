"""
Plugin Name: Search
Description: Adds a client-side search function using the generated `search_index.json`.
"""

from core.i18n import _
import os
import json

# --- Plugin-Metadaten ---
name = "Search"
description = "Adds a client-side search function."
# --------------------------

def handle(content, args, context, env):
    """
    Plugin Name: Search

    Description: Adds a client-side search function. The plugin renders a search input and the necessary JavaScript to search the website.

    Syntax:
    [[search]]
    [[search placeholder="Suchen..." show_excerpt="true" excerpt_length="150" show_filter="false" paginate="false" per_page="10" pagination_window="2"]]


    Parameters:    
    
    - placeholder (optional): The placeholder text for the search input. Default: "Search..."
    - show_excerpt (optional): "true" or "false", whether to show a short excerpt of the content. Default: "true"
    - excerpt_length (optional): The length of the excerpt in characters. Default: 150
    - show_filter (optional): "true" or "false", whether to show a dropdown menu for the search scope (Title, Tags, Content). Default: "false"
    - paginate (optional): "true" or "false", whether to paginate results. Default: "false"
    - per_page (optional): Number of results per page if pagination is active. Default: 10
    - pagination_window (optional): Number of page links shown around the current page. Default: 2
        

    Example:
        [[search placeholder="Search site..." show_excerpt="false"]]  
        
    """
    
    # Argumente mit Standardwerten verarbeiten
    placeholder = args.get('placeholder', _('Search...'))
    show_excerpt = args.get('show_excerpt', 'true').lower() == 'true'
    excerpt_length = int(args.get('excerpt_length', 150))
    show_filter = args.get('show_filter', 'false').lower() == 'true'
    paginate = args.get('paginate', 'false').lower() == 'true'
    per_page = int(args.get('per_page', 10))
    pagination_window = int(args.get('pagination_window', 2))
    
    # Eindeutige IDs für HTML-Elemente generieren, um mehrere Suchen auf einer Seite zu ermöglichen
    import random
    import string
    rand_id = ''.join(random.choices(string.ascii_lowercase, k=6))
    search_input_id = f"search-input-{rand_id}"
    search_scope_id = f"search-scope-{rand_id}"
    search_results_id = f"search-results-{rand_id}"

    # relativen Pfad zum Root-Verzeichnis ermitteln
    relative_prefix = context.get('relative_prefix', './')

    # HTML-Struktur für das Suchformular
    filter_html = ""
    if show_filter:
        filter_html = f"""
        <select id="{search_scope_id}" class="search-scope">
            <option value="all">{_("All")}</option>
            <option value="title">{_("Title")}</option>
            <option value="tags">{_("Tags")}</option>
            <option value="content">{_("Content")}</option>
        </select>
        """

    html = f"""
<div class="search-container">
    <div class="search-bar">
        <input type="text" id="{search_input_id}" placeholder="{placeholder}" autocomplete="off">
        {filter_html}
    </div>
    <div id="{search_results_id}" class="search-results"></div>
</div>
    """

    # Determine how to load the index
    is_preview = context.get('is_preview', False)
    project_root = context.get('project_root')
    
    load_index_js = ""
    
    if is_preview and project_root:
        # In preview mode, inject JSON directly to avoid CORS/Fetch errors
        index_path = os.path.join(project_root, 'site_output', 'search_index.json')
        if os.path.exists(index_path):
            try:
                with open(index_path, 'r', encoding='utf-8') as f:
                    index_data = json.load(f)
                    load_index_js = f"searchIndex = {json.dumps(index_data)};"
            except Exception as e:
                load_index_js = f"console.error('Error loading search index for preview: {str(e)}');"
        else:
            load_index_js = "console.warn('Search index not found. Please render the site (Ctrl+R) to generate it.');"
    else:
        load_index_js = """
    fetch(relativePrefix + 'search_index.json')
        .then(response => response.json())
        .then(data => { searchIndex = data; })
        .catch(error => console.error('Error loading search index:', error));
        """

    # JavaScript für die Suchlogik
    js = f"""
<script>
document.addEventListener('DOMContentLoaded', function() {{
    const searchInput = document.getElementById('{search_input_id}');
    const searchScope = document.getElementById('{search_scope_id}');
    const searchResults = document.getElementById('{search_results_id}');
    const relativePrefix = '{relative_prefix}';
    let searchIndex = [];
    
    let currentPage = 1;
    const resultsPerPage = {per_page};
    const enablePagination = {'true' if paginate else 'false'};
    const paginationWindow = {pagination_window};
    let currentQuery = '';
    let allResults = [];

    {load_index_js}

    function slugify(text) {{
        return text.toString().toLowerCase()
            .normalize('NFKD').replace(/[\\u0300-\\u036f]/g, '')
            .replace(/[^\\w\\s-]/g, '')
            .trim()
            .replace(/[-\s]+/g, '-');
    }}

    function performSearch() {{
        currentQuery = searchInput.value.toLowerCase().trim();
        const scope = searchScope ? searchScope.value : 'all';

        if (currentQuery.length < 3) {{
            searchResults.innerHTML = '';
            allResults = [];
            return;
        }}

        allResults = searchIndex.filter(page => {{
            const titleMatch = page.title && page.title.toLowerCase().includes(currentQuery);
            const contentMatch = page.content && page.content.toLowerCase().includes(currentQuery);
            const tagsMatch = page.tags && page.tags.some(tag => tag.toLowerCase().includes(currentQuery));

            if (scope === 'title') return titleMatch;
            if (scope === 'content') return contentMatch;
            if (scope === 'tags') return tagsMatch;
            
            return titleMatch || contentMatch || tagsMatch;
        }});
        
        currentPage = 1; // Reset to first page for new search
        displayResults();
    }}

    searchInput.addEventListener('input', performSearch);
    if (searchScope) {{
        searchScope.addEventListener('change', performSearch);
    }}

    function displayResults() {{
        if (allResults.length === 0) {{
            searchResults.innerHTML = '<p>{_("No results found.")}</p>';
            return;
        }}

        let resultsToShow = allResults;
        if (enablePagination) {{
            const startIndex = (currentPage - 1) * resultsPerPage;
            const endIndex = startIndex + resultsPerPage;
            resultsToShow = allResults.slice(startIndex, endIndex);
        }}

        let html = '<ul class="search-results-list">';
        resultsToShow.forEach(page => {{
            const pageUrl = relativePrefix + page.path.substring(1);
            const content = page.content || '';
            let excerpt = {'true' if show_excerpt else 'false'} ? ('...' + content.substring(Math.max(0, content.toLowerCase().indexOf(currentQuery) - 50), content.toLowerCase().indexOf(currentQuery) + {excerpt_length}).replace(new RegExp(currentQuery, 'gi'), match => `<span class="highlight">${{match}}</span>`) + '...') : '';
            
            let tagsHtml = '';
            if (page.tags && page.tags.length > 0) {{
                tagsHtml = '<div class="search-tags">';
                page.tags.forEach(tag => {{
                    const slug = slugify(tag);
                    tagsHtml += `<a href="${{relativePrefix}}tags/${{slug}}.html" class="search-tag">${{tag}}</a>`;
                }});
                tagsHtml += '</div>';
            }}
            
            html += `<li><a href="${{pageUrl}}"><h3>${{page.title}}</h3></a>${{tagsHtml}}<div class="excerpt">${{excerpt}}</div></li>`;
        }});
        html += '</ul>';

        if (enablePagination) {{
            html += renderPaginationControls();
        }}

        searchResults.innerHTML = html;

        // Re-add event listeners for pagination buttons
        if (enablePagination) {{
            document.querySelectorAll('.pagination-button').forEach(button => {{
                button.addEventListener('click', (e) => {{
                    e.preventDefault();
                    currentPage = parseInt(e.target.dataset.page, 10);
                    displayResults();
                }});
            }});
        }}
    }}

    function renderPaginationControls() {{
        const totalPages = Math.ceil(allResults.length / resultsPerPage);
        if (totalPages <= 1) {{
            return '';
        }}

        let paginationHtml = '<div class="search-pagination">';
        
        // Previous button
        if (currentPage > 1) {{
            paginationHtml += `<button class="pagination-button prev" data-page="${{currentPage - 1}}">&laquo; {_("Previous")}</button>`;
        }} else {{
            paginationHtml += `<span class="pagination-button disabled">&laquo; {_("Previous")}</span>`;
        }}

        // Page numbers
        paginationHtml += '<div class="page-numbers">';
        let lastPagePrinted = 0;

        for (let i = 1; i <= totalPages; i++) {{
            const isFirstPage = i === 1;
            const isLastPage = i === totalPages;
            const isInWindow = i >= currentPage - paginationWindow && i <= currentPage + paginationWindow;

            if (isFirstPage || isLastPage || isInWindow) {{
                if (i > lastPagePrinted + 1) {{
                    paginationHtml += '<span class="pagination-ellipsis">...</span>';
                }}
                
                const activeClass = i === currentPage ? ' active' : '';
                paginationHtml += `<button class="pagination-button page-number${{activeClass}}" data-page="${{i}}">${{i}}</button>`;
                lastPagePrinted = i;
            }}
        }}
        paginationHtml += '</div>';

        // Next button
        if (currentPage < totalPages) {{
            paginationHtml += `<button class="pagination-button next" data-page="${{currentPage + 1}}">{_("Next")} &raquo;</button>`;
        }} else {{
            paginationHtml += `<span class="pagination-button disabled">{_("Next")} &raquo;</span>`;
        }}

        paginationHtml += '</div>';
        return paginationHtml;
    }}
}});
</script>
    """

    return html + js