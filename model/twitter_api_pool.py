'''
Este script tiene como objetivo facilitar el acceso a la API de twiteer mediante
la creación de varias claves (API keys). De esta forma, se pueden realizar consultas
con mayor frecuencia (debido a los limit rates)
'''

import tweepy
import json
from tweepy import OAuthHandler
from time import sleep


class TwitterAPIPool:
    # Fichero con las claves usar de la API de twitter
    twitter_api_keys_file = '../data/tweet_keys.json'

    '''
    Esta clase representa un conjunto de objetos de la clase tweepy.API que pueden usarse
    para lanzar consultas a la API de tweeter.
    Usa el patrón singleton.
    '''
    def __init__(self):
        self.apis = []
        # Leemos las claves de la API de twitter disponibles.
        with open(self.twitter_api_keys_file, 'r') as twitter_api_keys_file_handler:
            keys = [json.loads(line) for line in twitter_api_keys_file_handler.read().splitlines()]
        for key in keys:
            try:
                # Creamos un objeto API con cada clave
                auth = OAuthHandler(key['consumer_key'], key['consumer_secret'])
                auth.set_access_token(key['access_token'], key['access_token_secret'])
                api = tweepy.API(auth_handler=auth)
                self.apis.append(api)
            except:
                # Descartamos aquellas claves incorrectas o inválidas.
                pass
        if len(self.apis) > 0:
            self.last_api_selected_index = None


    def get_api(self):
        '''
        Selecciona una API. Las APIs se seleccionan usando un sistema de turnos RoundRobin.
        :return: Devuelve un objeto de la clase tweepy.API correctamente autenticado. Devuelve
        None si no hay ninguna API disponible.
        '''
        if len(self.apis) == 0:
            return None

        # Seleccionamos el siguiente objeto API
        api_index = self.last_api_selected_index + 1 if not self.last_api_selected_index is None else 0
        if api_index == len(self.apis):
            api_index = 0
        api = self.apis[api_index]
        self.last_api_selected_index = api_index

        return api


    def execute(self, f, *args, **kwargs):
        '''
        Este método ejecuta una acción dada sobre las APIs de tweeter.
        Se pasa como parámetro el nombre de un método de la API de twitter
        y los argumentos que se le quieran pasar.
        func también puede ser un callback. En tal caso, se invocará el callback
        pasandole como parámetro, el objeto api de twitter con el que se podrá realizar las
        queries, junto con los parámetros adicionales que se hayan especificado.

        e.g: Este método devuelve los seguidores de un usuario.
        followers = Twitter().execute('followers', user_id = 1)
        print(followers)
        También puede hacerse de la siguiente forma...
        def request(api, user_id):
            return api.followers(user_id)
        followers = Tweeter().execute(request, user_id = 1)

        '''

        # El método es bloqueante, hasta que no se obtiene una respuesta correcta
        # con algún objeto API (sin que lanze excepciones del tipo, RateLimitError o
        # TweepError), el método no finalizará.
        while True:
            # Probamos con cada objeto API
            for index in range(0, len(self.apis)):
                api = self.get_api()
                try:
                    # Invocamos el método API con el objeto seleccionado
                    if callable(f):
                        func = f
                        result = func(api, *args, **kwargs)
                    else:
                        func = getattr(api, f)
                        result = func(*args, **kwargs)
                    # El método ha finalizado correctamente, devolvemos el resultaod.
                    return result
                except tweepy.RateLimitError:
                    pass
                except tweepy.TweepError:
                    pass
            sleep(15)


if __name__ == '__main__':
    pool = TwitterAPIPool()
    print(pool.execute('followers', user_id = '25073877'))