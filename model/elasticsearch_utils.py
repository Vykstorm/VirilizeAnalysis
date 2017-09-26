
from datetime import datetime
from re import match

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionTimeout
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import Match, Term

from model.tweet import Tweet
from model.user import TwitterUser


class ElasticSearchCollector:
    '''
    Esta clase permite realizar consultas a la base de datos...
    '''
    def __init__(self):
        hosts = [
            {'host': 'localhost', 'port': '9220', 'use_ssl': False}
        ]
        self.client = Elasticsearch(hosts = hosts)

    def _search(self, query, first_doc = 0, num_docs = 10):
        '''
        Envía la request a elasticsearch.
        :param request: Es la request a envíar, una instancia preparada de la clase
        elasticsearch_dsl.Search
        :param first_doc Es un índice que indica el primer documento a devolver (sirve para páginar
        los resultados)
        :param num_docs Es el número de documentos a devolver
        :return: Si la request fue ejecutada con éxito, devuelve un listado de los documentos
        obtenidos con la query (con información y metainformación del documento en forma de
        diccionario)
        En caso contrario, si la request fallo, se genera una excepción

        Solo se buscarán documentos en el índice "shokesu" del tipo "posts"
        '''

        request = Search(index = 'shokesu', doc_type = 'posts')
        request = request[first_doc:first_doc+num_docs]
        while True:
            try:
                result = request.using(client = self.client).query(query).execute(ignore_cache = False)
                if not result.success():
                    raise Exception()
                break
            except ConnectionTimeout:
                pass

        data = result.to_dict()
        docs = data['hits']['hits']
        return docs


    def search_tweets(self, query, first_tweet = 0, num_tweets = 10):
        '''
        Es igual que el método anterior, solo que el resultado de la query es parseado
        (convierte cada documento en forma de diccionario, en instancias de la clase Tweet)
        Además, se refinará la busqueda sobre elasticsearch de modo que solo se busquen aquellos
        documentos cuyo proveedor es twitter.
        '''

        query &= Term(provider = 'twitter')
        docs = self._search(query, first_doc = first_tweet, num_docs = num_tweets)


        def parse(doc):
            source = doc['_source']

            # Comprobamos que el proveedor del documento es twitter
            provider = source['provider']
            if not provider == 'twitter':
                raise Exception()

            id = source['post_id']
            text = next(iter(source['body'].values()))
            is_retweet = source['is_retweet']
            is_reply  = source['is_reply']
            post_type = 'retweet' if is_retweet else ('reply' if is_reply else 'original')
            num_retweets = source['retweet_count']
            retweet_id = source['retweet_id'] if post_type == 'retweet' else None
            reply_id = source['retweet_id'] if post_type == 'reply' else None
            author = None

            result = match('^(\d{4})\-(\d{1,2})\-(\d{1,2})T(\d{1,2})\:(\d{1,2})\+.*$', source['published_at'])
            if not result:
                raise Exception()
            timestamp = datetime(*[int(strnum) for strnum in result.groups()]).strftime('%s')

            user_data = source['user']
            num_followers = user_data['followers_count']
            num_friends = user_data['friends_count']
            screen_name = user_data['screenname']
            author = TwitterUser(screen_name, num_followers, num_friends)

            tweet = Tweet(author, id, text, post_type, num_retweets, timestamp, retweet_id, reply_id)

            return tweet

        posts = []
        for doc in docs:
            try:
                post = parse(doc)
                posts.append(post)
            except:
                pass
        return posts


if __name__ == '__main__':
    query = Match(**{'body.es' : '@sanchezcastejon'})

    posts = ElasticSearchCollector().search_tweets(query)
    for post in posts:
        print(post)
