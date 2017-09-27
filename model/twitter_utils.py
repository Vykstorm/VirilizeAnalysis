
from model.twitter_api_pool import TwitterAPIPool
from tweepy import Cursor

class Twitter:
    '''
    Clase que usa la API de twitter para realizar consultas.
    Es un singleton. Todas las instancias apuntan al singleton.
    '''

    class _Twitter:
        def __init__(self):
            self.api = TwitterAPIPool()

        def _process_tweet(self, status):
            '''
            Procesa un tweet.
            :param status: Es un objeto tweepy.Status de donde se extaerá la información del tweet.
            :return: Devuelve el tweet procesado, una instancia de la clase Tweet, o None si hubo
            un error al procesar la información del tweet.
            '''
            try:
                # ID del tweet.
                id = status.id_str
                # Cuerpo del tweet
                text = status.text
                # Es un retweet ?
                is_retweet = hasattr(status, 'retweeted_status')
                # Es una reply ?
                is_reply = hasattr(status, 'in_reply_to_status_id') and not status.in_reply_to_status_id is None
                post_type = 'retweet' if is_retweet else ('reply' if is_reply else 'original')
                # Número de retweets
                num_retweets = status.retweet_count
                # Timestamp UNIX
                timestamp = status.created_at.strftime('%s')
                # ID del tweet retweeteado.
                retweet_id = status.retweeted_status if is_retweet else None
                # ID del tweet respondido.
                reply_id = status.in_reply_to_status_id if is_reply else None

                # Info del usuario.
                user_status = status.user
                author = self._process_user(user_status)
                if author is None:
                    raise Exception()

                tweet = Tweet(author, id, text, post_type, num_retweets, timestamp, retweet_id, reply_id)

                return tweet
            except:
                pass
            return None

        def _process_user(self, user_status):
            '''
            Procesa un usuario de twitter.
            :param user_status: Es una instancia de la clase tweepy.User cuyos datos se procesarán.
            :return: Devuelve una instancia de la clase TweetUser con información sobre el perfil
            del usuario, o None si hubo un error al procesar la información.
            '''
            try:
                # Nombre del usuario
                screen_name = user_status.screen_name
                # Número de seguidores
                num_followers = user_status.followers_count
                # Número de amigos.
                num_friends = user_status.friends_count

                user = TwitterUser(screen_name, num_followers, num_friends)
                return user
            except:
                pass
            return None

        def _search_tweet_by_id(self, id):
            '''
            Busca un tweet por ID
            :param id: Es la ID del tweet
            :return: Devuelve el tweet cuya ID es la indicada, o None si no hay ningún tweet
            con esa ID.
            '''
            status = self.api.execute('get_status', id)
            return self._process_tweet(status)


        def _search_by_terms(self, terms, count):
            '''
            Busca tweets en los que se menciona alguno de los términos que se indican como parámetro.
            :param term: String con los términos a buscar
            :param count: Parámetro opcional que limita el número de tweets a devolver.
            :return Devuelve una lista de tweets que encajan con alguno de los términos indicados
            de tamaño "count", o una lista vacía en caso contrario.
            '''

            # Dividimos la búsqueda en distintos frames, indicando el parámetro since_id en cada
            # frame
            def search(count, since_id = None):
                def request(api):
                    # Invocamos a la API de tweepy, el método "search", usando el objeto API
                    # proporcionado por twitter_api_pool
                    statuses = list(Cursor(api.search, q = terms, since_id = since_id).items(count))
                    return statuses
                # Ejecutamos la request.
                statuses = self.api.execute(request)

                # Procesamos los tweets, descartamos tweets no válidos.
                tweets = []
                for status in statuses:
                    tweet = self._process_tweet(status)
                    if not tweet is None:
                        tweets.append(tweet)

                if since_id is None:
                    since_id = min([int(tweet.get_id()) for tweet in tweets]) - 1

                return tweets, since_id

            # Número de tweets a consultar en cada request
            step_count = 100

            tweets, since_id = search(min(step_count, count))

            if count < step_count:
                return tweets
            count -= step_count
            since_id -= step_count

            while count > 0: # Necesitamos "count" tweets
                _tweets, since_id = search(min(step_count, count), since_id)
                tweets.extend(_tweets)
                since_id -= step_count
                count -= step_count

            return tweets


        def _search_user_by_id(self, id):
            '''
            Busca un perfil de usuario por ID
            :param id: Es la ID del usuario a consultar
            :return: Devuelve un objeto de la clase TweetUser con la info del usuario, o None
            si no hay ningún usuario con la ID indicada.
            '''
            user_status = self.api.execute('get_user', user_id = id)
            return self._process_user(user_status)

        def _search_user_by_name(self, name):
            '''
            Igual que el método anterior, solo que la búsqueda se realiza por nombre (ScreenName)
            en lugar de su ID
            :param name:
            :return:
            '''
            user_status = self.api.execute('get_user', screen_name = name)
            return self._process_user(user_status)


    instance = None

    def __init__(self):
        if Twitter.instance is None:
            Twitter.instance = self._Twitter()

    def __getattr__(self, item):
        return getattr(Twitter.instance, item)

from model.tweet import Tweet
from model.user import TwitterUser