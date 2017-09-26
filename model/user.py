


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


    def __str__(self):
        return self.get_name()
    