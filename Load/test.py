import argparse
import logging
logging.basicConfig(level = logging.INFO)

import pandas as pd

from article import Article
from base import Base, Engine, Session

logger = logging.getLogger(__name__)

def main(filename):
    Base.metadata.create_all(Engine)
    session = Session()
    articles = pd.read_csv(filename)

    for index, row in articles.iterrows():
        logger.info('Loading article uid {} into DB...'.format(row['uid']))
        article = Article(row['uid'], 
                    row['headline'], 
                    row['text'], row['url'], 
                    row['newspaper_uid'], 
                    row['host'], 
                    row['headline_tokens'], 
                    row['text_tokens'])

        session.add(article)

    session.commit()
    session.close()



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help = 'File to be uploaded into DB.', type = str)
    args = parser.parse_args()

    main(args.filename)
