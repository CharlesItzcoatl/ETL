import logging
logging.basicConfig(level = logging.INFO)
# La librería subprocess permite manipular archivos de terminal directamente.
# Como tener la terminal directamente en Python.
import subprocess

# Referencia a logger.
logger = logging.getLogger(__name__)

# Se especifican los sitios disponibles para scrapear.
news_sites_uids = ['lajornada', 'milenio', 'sdpnoticias', 'unotv', 'elfinanciero']

def main():
    logging.info('Launching ETL...')
    _extract()
    _transform()
    _load()


def _extract():
    logging.info('Starting extraction process...')
    # Para cada sitio de noticias:
    for news_site_uid in news_sites_uids:
        # Ejecuta el comando 'python main.py lajornada/milenio/...'.
        # El parámetro cwd (current working directory) indica que la 
        # operación se ejecute en la carpeta ./Extract.
        subprocess.run(['python', 'main.py', news_site_uid], cwd = './Extract')
        # Ejecuta el comando 'find . -name lajornada/milenio/...'. El punto indica
        # que se comience a partir de este directorio (Extract/) y el parámetro
        # -name indica que se busque con el siguiente patrón; en este caso, los nombres
        # de los periódicos.
        # La siguiente línea ejecuta la operación '-exec mv lajornada/milenio/... 
        # ../Transform/lajornada_.csv'. -exec ejecuta un comando, que es mv, mover, 
        # el archivo con el nombre lajornada/milenio/... a la carpeta Transform con un
        # '_.csv' al final. find pide que termine en ';'
        subprocess.run(['find', '.', '-name', '{}*'.format(news_site_uid),
                        '-exec', 'mv', '{}', '../Transform/{}_.csv'.format(news_site_uid), ';'], cwd = './Extract')


def _transform():
    logging.info('Starting transform process...')
    for news_site_uid in news_sites_uids:
        dirty_data_filename = '{}_.csv'.format(news_site_uid)
        clean_data_filename = 'clean_{}'.format(dirty_data_filename)
        # Se ejecuta el comando 'python newspaper_recipe.py lajornada/milenio..._.csv'
        # en la carpeta ./Transform.
        subprocess.run(['python', 'newspaper_recipe.py', dirty_data_filename], cwd = './Transform')
        # Se ejecuta el comando 'rm lajornada/milenio_.csv' en la carpeta ./Transform.
        # Se elimina el archivo primigenio.
        subprocess.run(['rm', dirty_data_filename], cwd = './Transform')
        # Se ejecuta el comando 'mv clean_lajornada/milenio/..._.csv ../Load/
        # lajornada/milenio/.csv' en la carpeta Transform. Se mueve el archivo creado 
        # a la carpeta Load ya con el nombre definitivo. Ej: Load/lajornada.csv
        subprocess.run(['mv', clean_data_filename, '../Load/{}.csv'.format(news_site_uid)], cwd = './Transform')


def _load():
    logger.info('Starting load process...')
    for news_site_uid in news_sites_uids:
        clean_data_filename = '{}.csv'.format(news_site_uid)
        # Se ejecuta el comando 'python test.py lajornada.csv' en la carpeta Load.
        # Se carga el archivo en la base de datos y somos felices.
        subprocess.run(['python', 'test.py', clean_data_filename], cwd = './Load')
        # Se ejecuta el comando 'rm lajornada.csv' en la carpeta Load.
        # Se elimina el archivo .csv de todos los sitios de noticias.
        #subprocess.run(['rm', clean_data_filename], cwd = './Load')


if __name__ == '__main__':
    main()
