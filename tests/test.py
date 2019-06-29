import random
import time
import unittest
import uuid
from unittest import skip

from tests.restful_test_tools import Domain

domain_url = 'http://127.0.0.1:5000/api/v1'

dom = Domain(domain_url)

root_user = dict(
    username='root',
    password='passwd'
)


class TestRegister(unittest.TestCase):
    users = dom.res('users')

    def test_register(self):
        data = {
            'username': str(uuid.uuid4())[:10],
            'password': 'ajjcj898abCb',
        }
        r = self.users.post(data)
        r.status(200)
        dic = r.toJson(['id', 'username', 'email'])
        self.assertEqual(dic['username'], data['username'], 'should has username')
        self.assertNotIn('password', dic, 'should not contain password column')
        r = self.users.post(data)
        r.status(400)
        r.toJson(['error_msg'])

    def test_register_root(self):
        r = self.users.post(root_user)
        r.status(400)

    def test_weak_password_boundary(self):
        data = {
            'username': 'a'*20,
            'password': 'ahsd1jkaS'
        }
        self.users.post(data).status(200)

    def test_long_username_boundary(self):
        data = {
            'username': 'a'*21,
            'password': 'Pasj28'
        }
        self.users.post(data).status(400)

    def test_empty_username_boundary(self):
        data = {
            'username': '',
            'password': 'Pasj28'
        }
        self.users.post(data).status(400)


class TestAuth(unittest.TestCase):
    auth = None
    users = None
    token = ''

    def setUp(self):
        self.auth = dom.res('auth')
        r = self.auth.post(root_user).status(200)
        dic = r.toJson()
        self.assertTrue('\'' not in dic['token'])
        self.token = dic['token']
        self.users = dom.res('users', token=self.token)

    def test_auth(self):
        r = self.users.identify(1).get()
        r.status(200)
        dic = r.toJson()

    @skip
    def test_timeout_auth(self):
        time.sleep(1)
        r = self.users.identify(1).get()
        r.status(401)

    def test_auth_failed(self):
        self.auth = dom.res('auth')
        r = self.auth.post({'username': 'root', 'password': '????'})
        r.status(400)
        r = self.auth.post({'username': 'non_existent_user', 'password': '????'})
        r.status(400)

    def test_no_token_boundary(self):
        users = dom.res('users', token='not_a_token')
        r = users.identify(1).get()
        r.status(401)


class TestPaper(unittest.TestCase):
    auth = None
    users = None
    papers = None
    paper = None

    def setUp(self):
        auth = dom.res('auth')
        r = auth.post(root_user)
        r.status(200)
        dic = r.toJson()
        self.assertTrue('\'' not in dic['token'])
        token = dic['token']
        self.users = dom.res('users', token=token)
        self.papers = dom.res('papers', token=token)
        self.paper = dom.res('paper', token=token)

    def test_show_all(self):
        r = self.papers.get().status(200)
        result = r.toJson()['items']
        self.assertTrue(len(result) > 0)

    def test_show_one(self):
        self.papers.identify('akjshdkashd').get().status(400)
        all_papers = self.papers.get().status(200).toJson()['items']
        for paper in all_papers:
            result = self.papers.identify(paper['id']).get().status(200).toJson()
            assert len(result.keys()) >= 7


class TestPaperSubscription(unittest.TestCase):
    auth = None
    users = None
    papers = None
    my_papers = None

    def setUp(self):
        auth = dom.res('auth')
        r = auth.post(root_user)
        r.status(200)
        dic = r.toJson()
        self.assertTrue('\'' not in dic['token'])
        token = dic['token']
        # self.users = dom.res('users', token=token)
        self.papers = dom.res('papers', token=token)
        self.my_papers = dom.res('users/0/papers', token=token)
        self.some_user_papers = dom.res('users/3/papers', token=token)

    def test_subcribe_paper(self):
        # delete all subscribed papers
        r = self.my_papers.get()
        subscribed_papers = r.toJson()
        r.status(200)
        for paper in subscribed_papers['items']:
            paper_id = paper['paper']['id']
            r = self.my_papers.identify(paper_id).delete()
            r.status(200)

        # check all deleted
        r = self.my_papers.get().status(200)
        subscribed_papers = r.toJson()['items']
        assert len(subscribed_papers) == 0

        r = self.papers.get().status(200)
        all_papers = r.toJson()['items']
        random.shuffle(all_papers)

        # select some papers to subscribe
        selected_papers = all_papers[:-1]
        for paper in selected_papers:
            paper_id = paper['id']
            r = self.my_papers.post({
                'paper_id': paper_id
            }).status(200)

        # check selected papers are all subscribed
        r = self.my_papers.get()
        subscribed_papers = r.toJson()['items']
        assert set([paper['paper']['id'] for paper in subscribed_papers]) == set(
            [paper['id'] for paper in selected_papers])
        assert len(subscribed_papers) == len(selected_papers)
        assert len(subscribed_papers) == len(all_papers) - 1

        # select one to set finished
        assert subscribed_papers[0]['finished'] == False
        paper_id_to_finish = subscribed_papers[0]['paper']['id']
        r = self.my_papers.identify(paper_id_to_finish).put({'finished': 1}).status(200)
        r = self.my_papers.get().status(200)
        subscribed_papers = r.toJson()['items']
        ok = False
        for paper_subscription in subscribed_papers:
            if paper_subscription['paper']['id'] == paper_id_to_finish:
                assert paper_subscription['finished'] == True
                ok = True
        assert ok

        # select that one to set unfinished
        r = self.my_papers.identify(paper_id_to_finish).put({'finished': 0}).status(200)
        r = self.my_papers.get().status(200)
        subscribed_papers = r.toJson()['items']
        ok = False
        for paper_subscription in subscribed_papers:
            if paper_subscription['paper']['id'] == paper_id_to_finish:
                assert paper_subscription['finished'] == False
                ok = True
        assert ok

    def test_maniplate_error_paper_or_user_boundary(self):
        r = self.my_papers.identify(2333).delete()
        r = self.my_papers.identify(2333).put({'finished': 2333}).status(400)
        r = self.my_papers.identify(2333).put({'asdfinished': -1}).status(400)
        r = self.my_papers.identify(2333).put({'paper': 'ha'}).status(400)
        r = self.my_papers.identify(2333).put({'paper_id': 'ha'}).status(400)

        r = self.some_user_papers.identify(2333).delete().status(400)
        r = self.some_user_papers.identify(2333).put({'finished': 2333}).status(400)
        r = self.some_user_papers.identify(2333).put({'asdfinished': -1}).status(400)
        r = self.some_user_papers.identify(2333).put({'paper': 'ha'}).status(400)
        r = self.some_user_papers.identify(2333).put({'paper_id': 'ha'}).status(400)

    def test_insert_after(self):
        r = self.papers.get().status(200)
        all_papers = r.toJson()['items']
        random.shuffle(all_papers)

        # select some papers to subscribe
        selected_papers = all_papers[:-1]
        for paper in selected_papers:
            paper_id = paper['id']
            r = self.my_papers.post({
                'paper_id': paper_id
            }).status(200)

        subscribed_papers = self.my_papers.get().status(200).toJson()['items']
        papers = []
        for has_paper in subscribed_papers:
            papers.append(has_paper['paper'])

        result = self.my_papers.identify(papers[1]['id']).identify('insert_at_position').identify(0).post().status(
            200).toJson()

        subscribed_papers = self.my_papers.get().status(200).toJson()['items']
        assert papers[1]['id'] == subscribed_papers[0]['paper']['id']
        assert subscribed_papers[0]['position'] == 0


class TestLog(unittest.TestCase):
    logs = None

    def setUp(self):
        auth = dom.res('auth')
        r = auth.post(root_user).status(200)
        dic = r.toJson()
        self.assertTrue('\'' not in dic['token'])
        token = dic['token']
        self.logs = dom.res('logs', token=token)

    def test_get_log(self):
        j = self.logs.get().status(200).toJson()
        assert len(j) > 0

    def test_pagination_boundary(self):
        j = self.logs.get({'page': 2, 'per_page': 3}).status(200).toJson()
        assert j['page'] == 2
        assert j['per_page'] == 3
        assert j['has_prev'] == True
        j = self.logs.get({'page': 1, 'per_page': 3}).status(200).toJson()
        assert j['per_page'] == 3
        assert j['has_next'] == True
        assert j['has_prev'] == False
        assert j['page'] == 1


if __name__ == '__main__':
    unittest.main()
