console.log('main.js loaded');

$(function () {
    $('div.vue_component').map((i, v) => {
        new Vue({
            'el': v
        });
    });
    $('script[type="text/x-template"]').remove();
});

let base_url = '/api/v1';
let api = new Proxy({}, {
    get: function (target, key, receiver) {
        if (!target.url) {
            target.url = base_url;
        }
        key = key.replace('_', '');
        if (['post', 'delete', 'get', 'put'].indexOf(key) >= 0) {
            let url = target.url;
            let method = key;
            target.url = null;
            axios.defaults.headers.common['Authorization'] = 'Bearer ' + localStorage.token;
            return (data = {}, params = {}) => axios[method](url, {...data, params}).catch((err) => {
                if (err.response.status == 401) {
                    verify_auth();
                }
                if (err.response.status != 401) {
                    return Promise.reject(err);
                }
            });
        } else {
            target.url += '/' + key;
            return api
        }
    }
});

let verify_auth = function () {
    axios.get(base_url + '/users/0').catch((err) => {
        if (err.response.status == 401) {
            localStorage.token = '';
        }
    });
};

let raw_pagination = {
    items: [],
    has_prev: false,
    page: 1,
    per_page: 1,
    has_next: false,
    total_items: 0,
    total_pages: 0,
};

Vue.component('pagination', {
    template: `
    <ul class="pagination justify-content-center row">
        <li class="page-item" :class="{'disabled':!has_prev}">
            <a href="javascript:void(0)" class="page-link" aria-label="Previous" @click="change_page(page-1)" >
                <span aria-hidden="true">&laquo;</span>
            </a>
        </li>
        <li class="page-item" :class="{'active':i==page}" v-for="i in range">
            <a href="javascript:void(0)" class="page-link" @click="change_page(i)">{{ i }}</a>
        </li>
        <li class="page-item" :class="{'disabled':!has_next}" >
            <a href="javascript:void(0)" class="page-link" aria-label="Next" @click="change_page(page+1)">
                <span aria-hidden="true">&raquo;</span>
            </a>
        </li>
    </ul>
            `,
    props: ['change_page', 'total_pages', 'page', 'has_prev', 'has_next'],
    data() {
        return {
            need: 7,
        }
    },
    computed: {
        range() {
            let in_range = (i) => {
                return i >= 1 && i <= this.total_pages;
            };

            if (this.total_pages < this.need) {
                //  enough
                return this.total_pages;
            } else {
                // not enough
                let has = 1;
                let page = this.page;
                let result = [page];
                for (let i = 1; i <= this.total_pages && has < this.need; i++) {
                    if (in_range(page - i)) {
                        result = [page - i].concat(result);
                        has += 1;
                    }
                    if (in_range(page + i)) {
                        result = result.concat([page + i]);
                        has += 1;
                    }
                }
                return result
            }
        }
    }
});

Vue.prototype.is_password_ok = function (password) {
    if (password && 8 <= password.length && password.length <= 20) {
        if (password.match('[A-Z]') && password.match('[a-z]') && password.match('[0-9]')) {
            return true;
        }
    }
    return false;
};

Vue.prototype.is_username_ok = function (username) {
    if (1 <= username.length && username.length <= 20) {
        return true;
    }
    return false;
};

Vue.filter('arxiv_raw_id',
    function (id) {
        if (id) {
            id = id.replace(':', '/');
            return id;
        } else {
            return '';
        }
    });

Vue.filter('arxiv_origin',
    function (id) {
        return `https://arxiv.org/abs/${id}`;
    });



