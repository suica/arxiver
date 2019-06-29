import requests


class Resource():
    def __init__(self, entrance, header):
        assert len(entrance) > 0
        if entrance.endswith('/'):
            entrance = entrance[:-1]
        self.entrance = entrance
        self.headers = header
        self.r = None

    def _chain(self):
        return self

    def status(self, code):
        assert self.r is not None, 'do request first'
        assert self.r.status_code == code, 'Expected {} , got {}. Content is {}.'.format(code, self.r.status_code,self.r.content)
        return self._chain()

    def attr(self, attr_s, value):
        assert self.r.__getattribute__(attr_s) == value
        return self._chain()

    def get(self, para={}):
        self.r = requests.get(self.entrance, params=para, headers=self.headers)
        return self._chain()

    def post(self, para={}):
        assert isinstance(para, dict)
        self.r = requests.post(self.entrance, data=para, headers=self.headers)
        return self._chain()

    def put(self, para={}):
        assert isinstance(para, dict)
        self.r = requests.put(self.entrance,data=para, headers=self.headers)
        return self._chain()

    def delete(self):
        self.r = requests.delete(self.entrance, headers=self.headers)
        return self._chain()

    def toJson(self, key=[]):
        assert self.r is not None
        dic = self.r.json()
        for k in key:
            assert k in dic
        return dic

    def identify(self, s):
        return Resource(self.entrance + '/{}'.format(s), self.headers)

    def toResUrl(self):
        return self.entrance

    def toRequestUrl(self):
        self.haveReq()
        return self.r.url

    def toHeaders(self):
        return self.headers

    def haveReq(self):
        assert self.r is not None


class Domain():

    def __init__(self, domain):
        assert len(domain) > 0
        if domain[-1] == '/':
            domain = domain[:-1]

        self.domain = domain
        self.resources = []

    def get_resource_url(self, s):
        assert not (s.startswith('/') or s.endswith('/'))
        return self.domain + '/' + s

    def add_resources(self, lis):
        assert isinstance(lis, list)
        for res in lis:
            url = self.get_resource_url(res)
            self.resources.append(res)

    def res(self, res, token=''):
        # assert res in self.resources
        if len(token) == 0:
            return Resource(self.get_resource_url(res), {})
        else:
            return Resource(self.get_resource_url(res), {
                'authorization': "Bearer " + token
            })
