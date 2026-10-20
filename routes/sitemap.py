from xml.sax.saxutils import escape
from flask import Blueprint, Response
from models import Producto, slugify

sitemap_bp = Blueprint('sitemap', __name__)

SITIO = "https://velezdepositos.com.co"


@sitemap_bp.route('/robots.txt')
def robots():
    content = f"""User-agent: *
Allow: /
Disallow: /admin
Disallow: /admin/
Sitemap: {SITIO}/sitemap.xml"""
    return Response(content, mimetype='text/plain')


@sitemap_bp.route('/sitemap.xml')
def sitemap():
    urls = [
        ("/", "1.0"),
        ("/productos", "0.9"),
        ("/contacto", "0.8"),
        ("/preguntas-frecuentes", "0.6"),
        ("/privacidad", "0.3"),
    ]
    productos = Producto.query.order_by(Producto.id).all()
    categorias = sorted({p.categoria for p in productos})
    urls += [(f"/categoria/{slugify(c)}", "0.8") for c in categorias]

    vistos = set()
    for p in productos:
        if p.slug not in vistos:
            vistos.add(p.slug)
            urls.append((f"/producto/{p.slug}", "0.7"))

    cuerpo = "\n".join(
        f"    <url>\n        <loc>{escape(SITIO + ruta)}</loc>\n        <priority>{prioridad}</priority>\n    </url>"
        for ruta, prioridad in urls
    )
    xml = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{cuerpo}\n</urlset>'
    return Response(xml, mimetype='application/xml')
