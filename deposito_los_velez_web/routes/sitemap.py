from flask import Blueprint, Response

sitemap_bp = Blueprint('sitemap', __name__)

@sitemap_bp.route('/robots.txt')
def robots():
    content = """User-agent: *
Allow: /
Allow: /productos
Allow: /contacto
Disallow: /admin
Disallow: /admin/
Disallow: /static/
Sitemap: https://velezdepositos.com.co/sitemap.xml"""
    return Response(content, mimetype='text/plain')

@sitemap_bp.route('/sitemap.xml')
def sitemap():
    xml = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://velezdepositos.com.co/</loc>
        <priority>1.0</priority>
    </url>
    <url>
        <loc>https://velezdepositos.com.co/productos</loc>
        <priority>0.9</priority>
    </url>
    <url>
        <loc>https://velezdepositos.com.co/contacto</loc>
        <priority>0.8</priority>
    </url>
</urlset>'''
    return Response(xml, mimetype='application/xml')
