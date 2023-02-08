import argparse
# Usamos logging para mostrar mensajes en  la consola.
import logging
logging.basicConfig(level = logging.INFO)
# Permite identificar elementos en una url.
from urllib.parse import urlparse
import pandas as pd
import hashlib

# La librería nltk se usa para identificar palabras clave.
import nltk
from nltk.corpus import stopwords

logger = logging.getLogger(__name__)


def main(filename):
    logger.info('Starting cleaning process...')

    #Se lee desde archivo .csv
    df = _read_data(filename)
    # Extraer el uid del periódico, es decir, el nombre del periódico.
    newspaper_uid = _extract_newspaper_uid(filename)
    # Añade una columna para el uid del periódico.
    df = _add_newspaper_uid_column(df, newspaper_uid)
    # Se extrae el host.
    df = _extract_host(df)
    # Rellena los valores de la columna 'headline' que sean NaN.
    df = _fill_missing_titles(df)
    # Genera un UID para cada noticia scrapeada.
    df = _uids_generator(df)
    # Eliminar saltos de línea y basura.
    df = _remove_new_lines(df)
    # Genera los tokens para 'headline' y 'text'.
    df = _tokenized_items(df, 'headline')
    df = _tokenized_items(df, 'text')
    # Se eliminan los duplicados en los títulos de las noticias
    _remove_duplicates(df, 'headline')
    df = _drop_rows_with_missing_values(df)
    # Se guarda el DataFrame en disco. 
    _save_data(df, filename)

    return df


# Se guarda el DataFrame en disco.
def _save_data(df, filename):
    clean_filename = 'clean_{}'.format(filename)
    logger.info('Saving database at {}'.format(clean_filename))
    df.to_csv(clean_filename)


# Se eliminan los duplicados en los títulos de las noticias.
def _remove_duplicates(df, column_name):
    logger.info('Removing repeated entries...')
    #El parámetro keep = 'first' especifica que se mantenga el primer valor 
    # de estos repetidos. El parámetro inplace = True indica que se mantengan 
    # los cambios en el DataFrame original.
    df.drop_duplicates(subset = [column_name], keep = 'first', inplace = True)
    
    return


def _drop_rows_with_missing_values(df):
    logger.info('Dropping rows wuth missing values...')
    return df.dropna()


# Genera los tokens para 'headline' y 'text'.
def _tokenized_items(df, column_name):
    logger.info('Adding token count for {}...'.format(column_name))
    # Se declara que la lista de palabras clave son en español.
    stop_words = set(stopwords.words('spanish'))    

    # Se eliminan los valores nulos.
    # Se separa el texto por cada palabra.
    # Se filtran las palabras que no son alfanuméricas.
    # Se convierten las palabras clave en minúsculas.
    # Se filtran las palabras que no pertenecen al set stop_words.
    # Se obtiene la cantidad de palabras clave de la columna seleccionada. 
    n_tokens = (df.dropna()
                .apply(lambda row: nltk.word_tokenize(row[column_name]), axis = 1)
                .apply(lambda tokens: list(filter(lambda token: token.isalpha(), tokens)))
                .apply(lambda tokens: list(map(lambda token: token.lower(), tokens)))
                .apply(lambda word_list: list(filter(lambda word: word not in stop_words, word_list)))
                .apply(lambda valid_words: len(valid_words))
               )

    # Se crea la columna 'headline_tokens' y 'text_tokens' para cada caso, que contiene
    # el número de palabras claves en ambas.
    df[column_name + '_tokens'] = n_tokens

    return df

# Eliminar saltos de línea y basura.
def _remove_new_lines(df):
    logger.info('Removing newlines and thingys...')
    # Se obtienen los valores por fila, como se indica con axis = 1. Si no se 
    # especificara, se aplicaría el mismo valor a todos los elementos de la columna (?).
    # stripped_body es un objeto Series de Pandas.
    stripped_body = (df.apply(lambda row: row['text'], axis = 1)
                       .apply(lambda body: body.replace('\n', ''))
                       .apply(lambda body: body.replace('\r', ''))
                    )
    
    # A la columna 'text' del DataFrame se asigna la Series de Pandas 'stripped_body'
    df['text'] = stripped_body

    return df

# Genera un UID para cada noticia scrapeada.
def _uids_generator(df):
    logger.info('Generating UID\'s for each new')
    # Al DataFrame aplica la función que genera un hash a partir del url.
    # El método md5 de la clase hashlib recibe una lista de bytes, por lo que
    # se convierte el resultado de la transformación con la función bytes().
    # Se indica que se obtenga el valor del eje de las filas con axis = 1.
    # El objeto hash se convierte en una cadena hexadecimal de 16 dígitos.
    uids = (df.apply(lambda row: hashlib.md5(bytes(row['url'].encode())), axis = 1)
              .apply(lambda hash_object: hash_object.hexdigest())
           )
    # Se crea la columna uid y se les asignan los uids.
    df['uid'] = uids 
    
    # Se asigna como índice la columna 'uid'.
    return df.set_index('uid')


# Rellena los valores de la columna 'title' que sean NaN.
def _fill_missing_titles(df):
    logger.info('Filling missing titles')
    # Devuelve True para los valores en la columna 'headline' que sean NaN y False para los que sean distintos de NaN.
    missing_titles_mask = df['headline'].isna()

    # Para todos los elementos cuyo valor en 'headline' sea NaN, obtiene su valor en 'url'.
    # De la url, extrae la cadena que coincida con la RegEx "empieza con uno o más caracteres alfanuméricos, seguido(s)
    # de un guion '-', seguido de uno o más caracter cualesquiera".
    # Luego, divide por cada guion '-'.
    # Con la función join une el resultado por medio de espacio, se pone en mayúscula
    # la primera letra de la cadena y se reemplaza el posible slash '/' al final de la
    # dirección de la noticia. 
    # Esta columna se guarda en missing_titles, que es una Series de Pandas.
    missing_titles = (df[missing_titles_mask]['url']
                  .str.extract(r'(?P<missing_titles>[a-z]+-.+)$')
                  .applymap(lambda title: title.split('-'))
                  .applymap(lambda title_word_list: ' '.join(title_word_list))
                  .applymap(lambda title: title.capitalize())
                  .applymap(lambda title: title.replace('/',''))
                 )

    # Para todos los elementos del dataframe con valor en 'headline' igual a NaN,
    # asigna los elementos de la Series missing_titles de la columna 'missing_titles'.
    df.loc[missing_titles_mask, 'headline'] = missing_titles.loc[:, 'missing_titles']

    return df


# Extraer el uid del periódico, es decir, el nombre del periódico.
def _extract_newspaper_uid(filename):
    logger.info('Extracting newspaper uid...')
    # Del nombre del archivo, divide por '_' y elige el primer elemento, que siempre es el nombre del periódico.
    newspaper_uid = filename.split('_')[0]
    logger.info('Newspaper uid detected: {}'.format(newspaper_uid))
    
    return newspaper_uid


# Añade una columna para el uid del periódico.
def _add_newspaper_uid_column(df, newspaper_uid):
    logger.info('Filling newspaper uid column with {}'.format(newspaper_uid))
    # Se crea la columna y se añade a cada elemento el mismo uid.
    df['newspaper_uid'] = newspaper_uid

    return df


# Se extrae el host.
def _extract_host(df):
    logger.info('Extracting host from URL...')
    # Crea una columna 'host', a la cual se aplica la función lambda que extrae el host por medio del método urlparse()
    # y que se encuentra en el atributo .netloc.
    df['host'] = df['url'].apply(lambda x: urlparse(x).netloc)
    
    return df


#Se lee desde archivo .csv
def _read_data(filename):
    logger.info('Reading file {}'.format(filename))
    
    return pd.read_csv(filename)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # Se envía el nombre del archivo a ser limpiado. Ej: lajornada_07-04-2022_articles.csv
    # Se crea el argumento filename para que pueda ingresarse por el usuari.
    parser.add_argument('filename', help = 'The path to the dirty data', type = str)
    args = parser.parse_args()
    df = main(args.filename)
