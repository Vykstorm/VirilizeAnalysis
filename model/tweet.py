

import requests
from re import findall, match

class Tweet(dict):
    '''
    Representa un post de un usuario en tweeter.
    '''
    def __init__(self, author, id, text, post_type, num_retweets, timestamp, retweet_id = None, reply_id = None):
        '''
        Inicializa la instancia.
        :param author:  Es el autor del tweet
        :param id: Es la id del tweet.
        :param text: Es el cuerpo del mensaje
        :param post_type: El tipo de tweet (retweet, original o reply)
        :param num_retweets: Número de retweets de este post.
        :param timestamp: Timestamp UNIX de  la publicación de este mensaje
        :param retweet_id: Si post_type == 'retweet', debe indicar la id del tweet retweeteado.
        :param reply_id: Si post_type == 'reply', debe indicar la id del tweet respondido.
        '''
        super().__init__()

        self['author'] = author
        self['id'] = id
        self['text'] = text
        self['post_type'] = post_type
        self['num_retweets'] = num_retweets
        self['retweet_id'] = retweet_id
        self['reply_id'] = reply_id
        self['timestamp'] = timestamp



    def get_author(self):
        '''

        :return: Devuelve el autor del tweet
        '''
        return self['author']

    def get_id(self):
        '''

        :return: Devuelve la ID del tweet
        '''
        return self['id']

    def get_text(self):
        '''

        :return: Devuelve el cuerpo del mensaje del tweet
        '''
        return self['text']


    def get_type(self):
        '''

        :return: Devuelve el tipo de tweet: 'retweet', 'original' o 'reply'
        '''
        return self['post_type']

    def is_retweet(self):
        '''

        :return: Devuelve un valor booleano indicando si el tweet es un retweet o no.
        '''
        return self.get_type() == 'retweet'

    def is_reply(self):
        '''

        :return: Devuelve un valor booleano indicando si el tweet es una reply o no.
        '''
        return self.get_type() == 'reply'

    def get_num_retweets(self):
        '''

        :return: Devuelve el número de retweets
        '''
        return self['num_retweets']

    def get_timestamp(self):
        '''

        :return: Devuelve el timestamp de la publicación del tweet, una instancia de la clase
        datetime.datetime
        '''
        return self['timestamp']

    def get_retweet_id(self):
        '''

        :return: Si get_type() == 'retweet', este método devuelve la ID del tweet retweeteado.
        '''
        return self['retweet_id']

    def get_reply_id(self):
        return self['reply_id']



    def get_info_sources(self, follow_redirects=True, request_timeout=10):
        '''
        Obtiene los dominios de las fuentes externas mencionadas (hosts de las urls que aparecen
        en el mensaje)
        :param follow_redirects: Es un valor booleano. En caso de que se establezca a True,
        se tendrá en cuenta si la url es una redirección HTTP a otra o no. Se intentará encontrar
        en este caso, la dirección final.
        :param request_timeout: Esta variable se usará cuando follow_redirects está a True. Indica
        que si transcurre la cantidad de tiempo indicada después de haber realizado una cadena
        de requests http a la dirección que indica la url y las urls subsiguientes como
        consecuencia de las redirecciones HTTP, y no se ha obtenido la dirección final, dicha url
        se descarta.
        :return: Devuelve una lista de hosts de fuentes externas en el tweet.
        '''

        def follow_link(link):
            result = requests.get(link, timeout=request_timeout)
            return result.url

        text = self.get_text()
        links = [full_url for full_url, path_and_query in
                 findall('(https?\:\/\/[^\/]+(\/[^ ]+)?)', text)]
        source_links = []
        for link in links:
            try:
                source_links.append(follow_link(link) if follow_redirects else link)
            except Exception:
                pass

        # Ahora extraemos el host de la dirección
        hosts = [match('^https?\:\/\/(www\.)?([^\/]+)(\/.*)?$', source_link).group(2) for source_link in source_links]

        # Eliminamos hosts repetidos y tambien twitter.com y t.co
        hosts = list(set(hosts) - set(['twitter.com', 't.co']))

        return hosts



    def __str__(self):
        s = 'Mensaje publicado por {} en la fecha {}:\n'.format(self.get_author(), self.get_timestamp())
        s += '-------\n'
        s += self.get_text() + ' \n'
        s += '-------\n'
        if self.get_type() != 'original':
            s += 'Es un retweet\n' if self.get_type() == 'retweet' else 'Es una respuesta a otro tweet\n'
        s += 'Fue retweeteado {} veces'.format(self.get_num_retweets())
        return s
