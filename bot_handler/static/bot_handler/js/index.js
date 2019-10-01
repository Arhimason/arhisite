let vh = window.innerHeight * 0.01;
document.documentElement.style.setProperty('--vh', `${vh}px`);

window.addEventListener('resize', () => {
    // We execute the same script as before
    let vh = window.innerHeight * 0.01;
    document.documentElement.style.setProperty('--vh', `${vh}px`);
});

var token = getCookie('token');
var top_box, wrapper, login_form, login_input, pass_input, messages_box, input_box, chat_box, chatSocket, start_vs,
    alive_vs;
var ws_protocol = 'ws://';
if (location.protocol === 'https:') {
    ws_protocol = 'wss://';
}
var ws_location = ws_protocol + window.location.host + '/ws/bot_web';


function show_chat() {
    logged_in = 1;
    start_ws(ws_location);
    top_box.style.visibility = "visible";
    top_box.style.opacity = "1";
    login_form.style.opacity = "0";


}

function hide_chat() {
    document.getElementById('sidebar').setAttribute('class', 'menu-sidebar js-sidebar');
    login_form.style.visibility = "visible";
    login_form.style.opacity = "1";
    top_box.style.visibility = "hidden";
    top_box.style.opacity = "0";
    logged_in = 0;
}

window.onload = function () {
    top_box = document.getElementById('top-box');
    wrapper = document.getElementById('wrapper');
    login_form = document.getElementById('login-form');
    login_input = document.getElementById('login-input');
    pass_input = document.getElementById('pass-input');
    messages_box = document.getElementById("messages");
    input_box = document.getElementById("input");
    chat_box = document.getElementById("chat_box");
    if (logged_in) {
        show_chat();
        document.title = bot_name;
    }
};

function login_button() {
    var login = login_input.value;
    var pass = pass_input.value;
    if ((!login) || (!pass)) {
        shake_animation();
        return false;
    }
    // login_form.visibility="hidden";
    // login_form.style.opacity="0";

    var xhr = new XMLHttpRequest();

    xhr.open('POST', 'login', true);
    xhr.setRequestHeader("Content-Type", "application/json");

    var csrftoken = getCookie('csrftoken');
    xhr.setRequestHeader("X-CSRFToken", csrftoken);
    xhr.send(JSON.stringify({'login': login, 'password': pass}));

    xhr.onreadystatechange = function () {
        if (this.readyState !== 4) return;


        if (this.status !== 200) {
            // обработать ошибку
            alert('ошибка: ' + (this.status ? this.statusText : 'запрос не удался'));
            return;
        } else {

            var resp_json = JSON.parse(xhr.responseText);
            eval(resp_json['eval']);
            if (resp_json['status'] === 'ok') {
                show_chat();
                token = getCookie('token');
                document.getElementById('login-box').innerText = login;
                document.title = bot_name;
            } else {
                shake_animation();
            }


        }

        // получить результат из this.responseText или this.responseXML
    };

    window.scrollTo(0, document.body.scrollHeight);
    return false;
}

function shake_animation() {
    login_form.style.animation = 'none';
    login_form.offsetHeight;
    /* trigger reflow */
    login_form.style.animation = null;
    login_form.style.animationName = 'shake-wrong';
}

function append_msg(text, own, uuid) {
    var cur_class = "message ";
    if (own) {
        cur_class += '-own';
    }
    var i = document.createElement("div");
    // var n = document.createTextNode('');
    i.setAttribute("class", cur_class);
    i.setAttribute('id', uuid);
    // i.appendChild(n);
    // n.textContent = text;
    i.innerHTML = text;
    messages_box.appendChild(i);

    chat_box.scrollTop = chat_box.scrollHeight;
}

function runScript(e) {
    //See notes about 'which' and 'key'
    if (e.keyCode === 13) {

        var cur_text = input_box.value;
        if (!cur_text) {
            return 0;
        }

        var payload = {
            'type': 'message',
            'text': cur_text,
            'date': Math.floor(Date.now() / 1000),
            'token': token
        };

        var serialized = JSON.stringify(payload);
        var uuid = MD5(serialized);
        payload['uuid'] = uuid;

        chatSocket.send(JSON.stringify(payload));

        append_msg(cur_text, 1);
        input_box.value = '';
    }
}

function message_handle(e) {
    var data = JSON.parse(e.data);
    eval(data['eval']);
    if (data['status'] !== 'ok') {
        logout();
        return 0;
    }
    var cur_text = data['text'];
    cur_text = cur_text.replaceAll('\n', '<br>');
    var cur_uuid = data['uuid'];
    if (data['type'] === 'edit_message') {
        var ee = document.getElementById(cur_uuid);

        // var text = ee.childNodes[0];
        // text.textContent = cur_text;
        ee.innerHTML = cur_text;
        return 1
    }
    append_msg(cur_text, 0, cur_uuid)
}

function logout() {
    deleteCookie('token');
    token = 0;
    hide_chat();
    document.title = bot_name + ': Login';
    // todo clear history?

}

var MD5 = function (d) {
    result = M(V(Y(X(d), 8 * d.length)));
    return result.toLowerCase()
};

function M(d) {
    for (var _, m = "0123456789ABCDEF", f = "", r = 0; r < d.length; r++) _ = d.charCodeAt(r), f += m.charAt(_ >>> 4 & 15) + m.charAt(15 & _);
    return f
}

function X(d) {
    for (var _ = Array(d.length >> 2), m = 0; m < _.length; m++) _[m] = 0;
    for (m = 0; m < 8 * d.length; m += 8) _[m >> 5] |= (255 & d.charCodeAt(m / 8)) << m % 32;
    return _
}

function V(d) {
    for (var _ = "", m = 0; m < 32 * d.length; m += 8) _ += String.fromCharCode(d[m >> 5] >>> m % 32 & 255);
    return _
}

function Y(d, _) {
    d[_ >> 5] |= 128 << _ % 32, d[14 + (_ + 64 >>> 9 << 4)] = _;
    for (var m = 1732584193, f = -271733879, r = -1732584194, i = 271733878, n = 0; n < d.length; n += 16) {
        var h = m, t = f, g = r, e = i;
        f = md5_ii(f = md5_ii(f = md5_ii(f = md5_ii(f = md5_hh(f = md5_hh(f = md5_hh(f = md5_hh(f = md5_gg(f = md5_gg(f = md5_gg(f = md5_gg(f = md5_ff(f = md5_ff(f = md5_ff(f = md5_ff(f, r = md5_ff(r, i = md5_ff(i, m = md5_ff(m, f, r, i, d[n + 0], 7, -680876936), f, r, d[n + 1], 12, -389564586), m, f, d[n + 2], 17, 606105819), i, m, d[n + 3], 22, -1044525330), r = md5_ff(r, i = md5_ff(i, m = md5_ff(m, f, r, i, d[n + 4], 7, -176418897), f, r, d[n + 5], 12, 1200080426), m, f, d[n + 6], 17, -1473231341), i, m, d[n + 7], 22, -45705983), r = md5_ff(r, i = md5_ff(i, m = md5_ff(m, f, r, i, d[n + 8], 7, 1770035416), f, r, d[n + 9], 12, -1958414417), m, f, d[n + 10], 17, -42063), i, m, d[n + 11], 22, -1990404162), r = md5_ff(r, i = md5_ff(i, m = md5_ff(m, f, r, i, d[n + 12], 7, 1804603682), f, r, d[n + 13], 12, -40341101), m, f, d[n + 14], 17, -1502002290), i, m, d[n + 15], 22, 1236535329), r = md5_gg(r, i = md5_gg(i, m = md5_gg(m, f, r, i, d[n + 1], 5, -165796510), f, r, d[n + 6], 9, -1069501632), m, f, d[n + 11], 14, 643717713), i, m, d[n + 0], 20, -373897302), r = md5_gg(r, i = md5_gg(i, m = md5_gg(m, f, r, i, d[n + 5], 5, -701558691), f, r, d[n + 10], 9, 38016083), m, f, d[n + 15], 14, -660478335), i, m, d[n + 4], 20, -405537848), r = md5_gg(r, i = md5_gg(i, m = md5_gg(m, f, r, i, d[n + 9], 5, 568446438), f, r, d[n + 14], 9, -1019803690), m, f, d[n + 3], 14, -187363961), i, m, d[n + 8], 20, 1163531501), r = md5_gg(r, i = md5_gg(i, m = md5_gg(m, f, r, i, d[n + 13], 5, -1444681467), f, r, d[n + 2], 9, -51403784), m, f, d[n + 7], 14, 1735328473), i, m, d[n + 12], 20, -1926607734), r = md5_hh(r, i = md5_hh(i, m = md5_hh(m, f, r, i, d[n + 5], 4, -378558), f, r, d[n + 8], 11, -2022574463), m, f, d[n + 11], 16, 1839030562), i, m, d[n + 14], 23, -35309556), r = md5_hh(r, i = md5_hh(i, m = md5_hh(m, f, r, i, d[n + 1], 4, -1530992060), f, r, d[n + 4], 11, 1272893353), m, f, d[n + 7], 16, -155497632), i, m, d[n + 10], 23, -1094730640), r = md5_hh(r, i = md5_hh(i, m = md5_hh(m, f, r, i, d[n + 13], 4, 681279174), f, r, d[n + 0], 11, -358537222), m, f, d[n + 3], 16, -722521979), i, m, d[n + 6], 23, 76029189), r = md5_hh(r, i = md5_hh(i, m = md5_hh(m, f, r, i, d[n + 9], 4, -640364487), f, r, d[n + 12], 11, -421815835), m, f, d[n + 15], 16, 530742520), i, m, d[n + 2], 23, -995338651), r = md5_ii(r, i = md5_ii(i, m = md5_ii(m, f, r, i, d[n + 0], 6, -198630844), f, r, d[n + 7], 10, 1126891415), m, f, d[n + 14], 15, -1416354905), i, m, d[n + 5], 21, -57434055), r = md5_ii(r, i = md5_ii(i, m = md5_ii(m, f, r, i, d[n + 12], 6, 1700485571), f, r, d[n + 3], 10, -1894986606), m, f, d[n + 10], 15, -1051523), i, m, d[n + 1], 21, -2054922799), r = md5_ii(r, i = md5_ii(i, m = md5_ii(m, f, r, i, d[n + 8], 6, 1873313359), f, r, d[n + 15], 10, -30611744), m, f, d[n + 6], 15, -1560198380), i, m, d[n + 13], 21, 1309151649), r = md5_ii(r, i = md5_ii(i, m = md5_ii(m, f, r, i, d[n + 4], 6, -145523070), f, r, d[n + 11], 10, -1120210379), m, f, d[n + 2], 15, 718787259), i, m, d[n + 9], 21, -343485551), m = safe_add(m, h), f = safe_add(f, t), r = safe_add(r, g), i = safe_add(i, e)
    }
    return Array(m, f, r, i)
}

function md5_cmn(d, _, m, f, r, i) {
    return safe_add(bit_rol(safe_add(safe_add(_, d), safe_add(f, i)), r), m)
}

function md5_ff(d, _, m, f, r, i, n) {
    return md5_cmn(_ & m | ~_ & f, d, _, r, i, n)
}

function md5_gg(d, _, m, f, r, i, n) {
    return md5_cmn(_ & f | m & ~f, d, _, r, i, n)
}

function md5_hh(d, _, m, f, r, i, n) {
    return md5_cmn(_ ^ m ^ f, d, _, r, i, n)
}

function md5_ii(d, _, m, f, r, i, n) {
    return md5_cmn(m ^ (_ | ~f), d, _, r, i, n)
}

function safe_add(d, _) {
    var m = (65535 & d) + (65535 & _);
    return (d >> 16) + (_ >> 16) + (m >> 16) << 16 | 65535 & m
}

function bit_rol(d, _) {
    return d << _ | d >>> 32 - _
}

String.prototype.replaceAll = function (search, replacement) {
    var target = this;
    return target.replace(new RegExp(search, 'g'), replacement);
};


function getCookie(name) {
    var matches = document.cookie.match(new RegExp(
        "(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
    ));
    return matches ? decodeURIComponent(matches[1]) : undefined;
}

function setCookie(name, value, options) {
    options = options || {};

    var expires = options.expires;

    if (typeof expires == "number" && expires) {
        var d = new Date();
        d.setTime(d.getTime() + expires * 1000);
        expires = options.expires = d;
    }
    if (expires && expires.toUTCString) {
        options.expires = expires.toUTCString();
    }

    value = encodeURIComponent(value);

    var updatedCookie = name + "=" + value;

    for (var propName in options) {
        updatedCookie += "; " + propName;
        var propValue = options[propName];
        if (propValue !== true) {
            updatedCookie += "=" + propValue;
        }
    }

    document.cookie = updatedCookie;
}

function deleteCookie(name) {
    setCookie(name, "", {
        expires: -1
    })
}

function start_ws(websocketServerLocation) {
    chatSocket = new WebSocket(websocketServerLocation);
    chatSocket.onmessage = function (e) {
        message_handle(e)
    };
    chatSocket.onopen = function (e) {
        clearTimeout(alive_vs);
        alive_vs = setTimeout(function () {
            alive_ws()
        }, 10000);
    };
    chatSocket.onclose = function () {
        // Try to reconnect in 5 seconds
        if (logged_in) {
            clearTimeout(start_vs);
            start_vs = setTimeout(function () {
                start_ws(websocketServerLocation)
            }, 5000);
        }
    };
}

function alive_ws() {
    var payload = {
        'type': 'alive',
        'token': token
    };
    chatSocket.send(JSON.stringify(payload));
    if (logged_in) {
        clearTimeout(alive_vs);
        alive_vs = setTimeout(function () {
            alive_ws()
        }, 10000);
    }
}

function toggleFullScreen() {

    document.getElementById('sidebar').setAttribute('class', 'menu-sidebar js-sidebar');
    var doc = window.document;
    var docEl = doc.documentElement;

    var requestFullScreen = docEl.requestFullscreen || docEl.mozRequestFullScreen || docEl.webkitRequestFullScreen || docEl.msRequestFullscreen;
    var cancelFullScreen = doc.exitFullscreen || doc.mozCancelFullScreen || doc.webkitExitFullscreen || doc.msExitFullscreen;

    if (!doc.fullscreenElement && !doc.mozFullScreenElement && !doc.webkitFullscreenElement && !doc.msFullscreenElement) {
        requestFullScreen.call(docEl);
    }
    else {
        cancelFullScreen.call(doc);
    }
}