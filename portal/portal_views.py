"""
Simple views for Linguify Portal
"""
from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings

def home(request):
    """Homepage showing product selection"""
    
    # Products configuration
    products = []
    for key, product in settings.LINGUIFY_PRODUCTS.items():
        product_data = product.copy()
        product_data['key'] = key
        # Use dev or prod URL
        product_data['url'] = product['dev_url'] if settings.DEBUG else product['prod_url']
        products.append(product_data)
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Linguify Portal</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            body {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }}
            .hero-section {{
                min-height: 100vh;
                display: flex;
                align-items: center;
                text-align: center;
                color: white;
            }}
            .product-card {{
                background: rgba(255,255,255,0.1);
                border-radius: 20px;
                padding: 2rem;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.2);
                transition: transform 0.3s, box-shadow 0.3s;
                height: 100%;
            }}
            .product-card:hover {{
                transform: translateY(-10px);
                box-shadow: 0 20px 40px rgba(0,0,0,0.2);
            }}
            .btn-product {{
                padding: 12px 30px;
                border-radius: 25px;
                text-decoration: none;
                transition: all 0.3s;
                display: inline-block;
                margin-top: 1rem;
            }}
            .btn-primary-product {{
                background: white;
                color: #667eea;
                border: 2px solid white;
            }}
            .btn-primary-product:hover {{
                background: transparent;
                color: white;
            }}
            .btn-secondary-product {{
                background: transparent;
                color: white;
                border: 2px solid white;
            }}
            .btn-secondary-product:hover {{
                background: white;
                color: #667eea;
            }}
        </style>
    </head>
    <body>
        <section class="hero-section">
            <div class="container">
                <div class="row justify-content-center">
                    <div class="col-lg-10">
                        <h1 class="display-4 fw-bold mb-4">🌐 Linguify Portal</h1>
                        <p class="lead mb-5">Choisissez votre produit Linguify</p>
                        
                        <div class="row g-4">
    """
    
    for product in products:
        is_primary = product['key'] == 'backend'
        btn_class = 'btn-primary-product' if is_primary else 'btn-secondary-product'
        target = '' if product['key'] == 'backend' else 'target="_blank"'
        
        html_content += f"""
                            <div class="col-md-6">
                                <div class="product-card">
                                    <i class="{product['icon']} fa-3x mb-3"></i>
                                    <h3 class="h4 mb-3">{product['name']}</h3>
                                    <p class="mb-4">{product['description']}</p>
                                    <a href="{product['url']}" class="btn-product {btn_class}" {target}>
                                        {'Commencer' if product['key'] == 'backend' else 'Découvrir'}
                                        <i class="fas fa-arrow-right ms-2"></i>
                                    </a>
                                </div>
                            </div>
        """
    
    html_content += """
                        </div>
                        
                        <div class="mt-5">
                            <p class="text-white-50">
                                <small>🚀 Ports recommandés - Backend: 8000 | LMS: 8001 | Portal: 8080</small>
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    </body>
    </html>
    """
    
    return HttpResponse(html_content)