from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.templatetags.static import static
import os

def home(request):
    """
    Homepage view for the CRISP application.
    Serves the React frontend if available, otherwise shows a simple landing page.
    """
    # Try to serve React app
    react_index_path = os.path.join(settings.BASE_DIR, 'static', 'react', 'index.html')
    
    if os.path.exists(react_index_path):
        try:
            with open(react_index_path, 'r', encoding='utf-8') as f:
                react_html = f.read()
            
            # Update asset paths to work with Django static files
            react_html = react_html.replace('href="/assets/', 'href="/static/react/assets/')
            react_html = react_html.replace('src="/assets/', 'src="/static/react/assets/')
            react_html = react_html.replace('href="/vite.svg', 'href="/static/react/vite.svg')
            return HttpResponse(react_html)
        except Exception:
            pass
    
    # Fallback to simple landing page
    html_content = """
    <html>
        <head>
            <title>CRISP - Cyber Risk Information Sharing Platform</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 20px;
                    color: #333;
                }
                .container {
                    max-width: 1000px;
                    margin: 0 auto;
                    padding: 20px;
                }
                h1 {
                    color: #0056b3;
                }
                a {
                    color: #0056b3;
                    text-decoration: none;
                }
                a:hover {
                    text-decoration: underline;
                }
                .links {
                    margin-top: 30px;
                }
                .links a {
                    display: inline-block;
                    margin-right: 20px;
                    padding: 10px 15px;
                    background-color: #0056b3;
                    color: white;
                    border-radius: 4px;
                }
                .links a:hover {
                    background-color: #003d82;
                    text-decoration: none;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>CRISP - Cyber Risk Information Sharing Platform</h1>
                <p>Welcome to the CRISP system. This platform enables organizations to share cyber threat intelligence in a secure, standardized way.</p>
                
                <div class="links">
                    <a href="/admin/">Admin Interface</a>
                    <a href="/api/threat-feeds/">API: Threat Feeds</a>
                </div>
            </div>
        </body>
    </html>
    """
    return HttpResponse(html_content)
