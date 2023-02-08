# Page objects construidos para abstraer los objetos.

#from unittest import result
from common import config
import requests
import bs4

# Clase padre que heredan la página principal y las páginas de cada noticia.
class NewsPage:
    def __init__(self, news_site_uid, url):
        # Selecciona uno de los portales de noticias.
        self._config = config()['news_sites'][news_site_uid]
        # Selecciona los atributos para encontrar los links, título y cuerpo del sitio.
        self._queries = self._config['queries']
        self._html = None
        self._visit(url)

    # Devuelve la búsqueda en el archivo .html como cadena de texto.
    def _select(self, query_string):
        # El método select busca en el archivo .html la cadena 'query_string'.
        return self._html.select(query_string)

    def _visit(self, url):
        # Hace la petición al sitio web 'url'.
        response = requests.get(url)
        response.encoding = 'utf-8'
        # Protección en caso de que la página no permita el acceso (aquí se muestra
        # el error 403 de algunos sitios).
        response.raise_for_status()

        # Guarda en el atributo _html el archivo .html en texto plano del sitio.
        self._html = bs4.BeautifulSoup(response.text, 'html.parser')


class HomePage(NewsPage):
    def __init__(self, news_site_uid, url):
        super().__init__(news_site_uid, url)

    # Las funciones propiedad restringen el acceso directo/público a los atributos 
    # de la clase.
    @property
    def article_links(self):
        # Lista donde se guardan todos los links de la página principal.
        link_list = []
        # Para cada link que coincida con la forma especificada:
        # self._select devuelve todas las coincidencias con 
        # self._queries['homepage_article_links'] en el .html de texto plano.
        for link in self._select(self._queries['homepage_article_links']):
            # Si el objeto tiene un atributo 'href' se guarda en la lista de links.
            if link and link.has_attr('href'):
                link_list.append(link)
        # Crea un conjunto (eliminación de repetidos) con el valor del atributo 'href'
        # de cada link.
        return set(link['href'] for link in link_list)



class ArticlePage(NewsPage):
    def __init__(self, news_site_uid, url):
        super().__init__(news_site_uid, url)
        self._url = url

    @property
    def headline(self):
        result = self._select(self._queries['article_title'])
        return result[0].text if len(result) else ''

    @property
    def text(self):
        result = self._select(self._queries['article_body'])
        # _select provee una lista. Devuelve el texto del primer elemento 
        # (que debe ser el único) sólo si hay resultados en la lista; si no, 
        # devuelve una cadena vacía.
        return result[0].text if len(result) else ''

    @property
    def url(self):
        return self._url