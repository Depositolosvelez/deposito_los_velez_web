from flask import Blueprint, Response

sitemap_bp = Blueprint("sitemap", __name__)

@sitemap_bp.route("/sitemap.xml")
def sitemap():
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://depositolosvelez.pythonanywhere.com/</loc>
        <priority>1.0</priority>
    </url>
    <url>
        <loc>https://depositolosvelez.pythonanywhere.com/productos</loc>
        <priority>0.9</priority>
    </url>
    <url>
        <loc>https://depositolosvelez.pythonanywhere.com/contacto</loc>
        <priority>0.8</priority>
    </url>
</urlset>"""
    return Response(xml, mimetype="application/xml")
