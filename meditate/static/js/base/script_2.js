; (function (p, l, o, w, i, n, g) {
    if (!p[i]) {
        p.GlobalSnowplowNamespace = p.GlobalSnowplowNamespace || [];
        p.GlobalSnowplowNamespace.push(i); p[i] = function () {
            (p[i].q = p[i].q || []).push(arguments)
        }; p[i].q = p[i].q || []; n = l.createElement(o); g = l.getElementsByTagName(o)[0]; n.async = 1;
        n.src = w; g.parentNode.insertBefore(n, g)
    }
}(window, document, 'script', '//cdn2.editmysite.com/js/wsnbn/snowday262.js', 'snowday'));

var r = [99, 104, 101, 99, 107, 111, 117, 116, 46, 40, 119, 101, 101, 98, 108, 121, 124, 101, 100, 105, 116, 109, 121, 115, 105, 116, 101, 41, 46, 99, 111, 109];
var snPlObR = function (arr) {
    var s = '';
    for (var i = 0; i < arr.length; i++) {
        s = s + String.fromCharCode(arr[i]);
    }
    return s;
};
var s = snPlObR(r);

var regEx = new RegExp(s);

_W.Analytics = _W.Analytics || { 'trackers': {} };
_W.Analytics.trackers.wSP = 'snowday';
_W.Analytics.user_id = '113116883';
_W.Analytics.site_id = '529209629803367381';

(function (app_id, ec_hostname, discover_root_domain) {
    var track = window[_W.Analytics.trackers.wSP];
    if (!track) return;
    track('newTracker', app_id, ec_hostname, {
        appId: app_id,
        post: true,
        platform: 'web',
        discoverRootDomain: discover_root_domain,
        cookieName: '_snow_',
        contexts: {
            webPage: true,
            performanceTiming: true,
            gaCookies: true
        },
        crossDomainLinker: function (linkElement) {
            return regEx.test(linkElement.href);
        }
    });
    track('trackPageView', _W.Analytics.user_id + ':' + _W.Analytics.site_id);
    track('crossDomainLinker', function (linkElement) {
        return regEx.test(linkElement.href);
    });
})(
    '_wn',
    'ec.editmysite.com',
    true
    );
