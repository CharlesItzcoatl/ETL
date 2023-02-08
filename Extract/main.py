import argparse
import logging
import news_page_objects as news
import re
import datetime
import csv

from requests.exceptions import HTTPError
from urllib3.exceptions import MaxRetryError

logging.basicConfig(level=logging.INFO)

from common import config

logger = logging.getLogger(__name__)
# RegEx
is_well_formed_link = re.compile(r'^https?://.+/.+$') # https://example.com/hello
is_root_path = re.compile(r'^/.+$') # /some-text

# Núcleo del proceso de scraping.
def _news_scraper(news_site_uid):
    articles = []
    # El host guarda la url dentro de la llave news_site_uid (corresponde a los 
    # periódicos) que se encuentra en la llave 'news_site'.
    host = config()['news_sites'][news_site_uid]['url']
    # Muestra en pantalla el mensaje indicado.
    logging.info('Launching scraper for {}'.format(host))
    # homepage es un objeto tipo HomePage, que recibe el nombre del sitio y su url.
    homepage = news.HomePage(news_site_uid, host)

    for link in homepage.article_links:
        #print(link)
        article = _fetch_article(news_site_uid, host, link)

        # Si se guardó un cuerpo, se guarda en la lista articles.
        if article:
            logger.info('Article fetched!!!')
            articles.append(article)
            #break
            #print(article.title)

    #print(len(articles))
    _save_articles(news_site_uid, articles)


# Guardar en un .csv todos los artículos de un sitio.
def _save_articles(news_site_uid, articles):
    # Guarda la fecha de este momento en 'now' con el formato dd-mm-aa.
    now = datetime.datetime.now().strftime('%d-%m-%Y')
    # Crea el archivo con el formato 'sitio_fecha_articles.csv'.
    out_file_name = '{news_site_uid}_{datetime}_articles.csv'.format(news_site_uid = news_site_uid, datetime = now)
    # Crea una lista que serán las cabeceras de columnas en el .csv.
    # Filtra los métodos (aplicables a articles, función dir())y mantiene los que no 
    # empiezan con '_', es decir title y body. El iterador se convierte a lista con list().
    csv_headers = list(filter(lambda property: not property.startswith('_'), dir(articles[0])))
    # Crea el archivo con nombre 'out_file_name', con función de escritura que permite
    # edición (+).
    with open(out_file_name, mode = 'w+') as f:
        # Editor de .csv. Recibe como parámetro el archivo.
        writer = csv.writer(f)
        # Agrega las cabeceras (body y title)
        writer.writerow(csv_headers)

        # Agrega una fila para cada artículo
        for article in articles:
            # Obtiene el atributo para cada title y body (prop in csv_headers) y lo
            # convierte en cadena de texto.
            row = [str(getattr(article, prop)) for prop in csv_headers]
            # Escribe a fuego la fila equivalente a noticia, título y cuerpo.
            writer.writerow(row)


# Función para extraer título y cuerpo de cada artículo.
def _fetch_article(news_site_uid, host, link):
    logger.info('Start fetching article at {}'.format(link))

    article = None
    # try y except para hacer el intento de ingresar al sitio de cada noticia.
    try:
        # Intenta crear un objeto tipo ArticlePage 
        article = news.ArticlePage(news_site_uid, _build_link(host, link))
    # HTTPError por si el link lleva a un sitio inexistente.
    # MaxRetryError evita intentos infinitos de acceder.
    except (HTTPError, MaxRetryError) as e:
        logger.warning('Error while fetching the article', exc_info = False)
    # Si existe el artículo, pero no tiene cuerpo, se notifica y se desecha.
    if article and not article.text:
        logger.warning('Invalid article. There is no body')
        return None

    return article


# Usa expresiones regulares para construir el link de la noticia.
def _build_link(host, link):
    # Si ya tiene la estructura completa correcta, sólo devuelve el link:
    if is_well_formed_link.match(link):
        return link
    # Si el link tiene formato sin url: 
    # (Ej. /notas/2022/04/05/deportes/gris-empate-de-milan-ante-bolonia/)
    elif is_root_path.match(link):
        # Combina el host con el enlace.
        return '{}{}'.format(host, link)
    # Cualquier otro caso (por ejemplo, que no cuente con un '/'  o
    # https al principio.)
    else:
        # Combina host y link poniendo un '/' entre ellos.
        return '{host}/{uri}'.format(host = host, uri = link)


if __name__ == '__main__':
    # Parseador de argumentos. Crea un objeto tipo ArgumentParser.
    parser = argparse.ArgumentParser()
    # Devuelve los valores de la primera llave ('news_sites'), es decir, los nombres de
    # los periódicos. El iterador se convierte en lista con la función list.
    news_site_choices = list(config()['news_sites'].keys())
    # 'news_site' indica el sitio a scrapear. Es la entrada o parámetro que da el usuario.
    # El parámetro help sólo provee información.
    # El parámetro type indica el tipo de variable que debe ser la entrada del usuario.
    # choices indica las opciones, lajornada, elpais y milenio.
    # El método add_argument sirve para especificar cómo debe ser el argumento que 
    # acompaña a la ejecución del programa.
    parser.add_argument('news_site', help = 'The news site to be scraped', type = str, choices = news_site_choices)

    # Devuelve un objeto con el atributo news_site.
    args = parser.parse_args()
    _news_scraper(args.news_site)