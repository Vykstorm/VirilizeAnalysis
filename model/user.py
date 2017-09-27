



class TwitterUser(dict):
    '''
    Esta clase representa a un usuario. Provee información relativa a su
    perfil.
    '''
    def __init__(self, screen_name, num_followers, num_friends):
        super().__init__()
        self['name'] = screen_name
        self['num_followers'] = num_followers
        self['num_friends'] = num_friends

    def get_num_followers(self):
        return self['num_followers']

    def get_num_friends(self):
        return self['num_friends']

    def get_name(self):
        return self['name']

    @staticmethod
    def search_by_id(id):
        '''
        Devuelve el usuario cuya ID es la que se especifica como parámetro, o None si no hay
        nadie que tenga esa ID.
        :param id:
        :return:
        '''
        return Twitter()._search_user_by_id(id)

    @staticmethod
    def search_by_name(name):
        '''
        Devuelve el usuario cuyo nombre (Screen Name) es el que se indica como parámetro, o None
        si no hay nadie con ese nombre.
        :param name:
        :return:
        '''
        return Twitter()._search_user_by_name(name)


    def __str__(self):
        return self.get_name()

    def __hash__(self):
        return hash(self.__repr__())

    def __eq__(self, other):
        return isinstance(other, TwitterUser) and self.get_name() == other.get_name()

from model.twitter_utils import Twitter