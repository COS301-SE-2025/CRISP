from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    """
    Homepage view for the CRISP application.
    """
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
