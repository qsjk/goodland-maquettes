// Mini runtime: renders the prototype templates ({{ }}, <sc-for>, <sc-if>, onClick) in plain HTML.
(function () {
  var handlers = [];
  function esc(v) {
    return String(v == null ? '' : v).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
  function lookup(path, scope) {
    path = path.trim();
    if (path === 'true') return true;
    if (path === 'false') return false;
    var parts = path.split('.'), v = scope;
    for (var i = 0; i < parts.length; i++) { if (v == null) return undefined; v = v[parts[i]]; }
    return v;
  }
  function attr(tag, name) {
    var m = tag.match(new RegExp(name + '="\\{\\{([^}]*)\\}\\}"')) || tag.match(new RegExp(name + '="([^"]*)"'));
    return m ? m[1] : null;
  }
  function findClose(src, from, tag) {
    var depth = 1, re = new RegExp('<' + tag + '[\\s>]|</' + tag + '>', 'g'), m;
    re.lastIndex = from;
    while ((m = re.exec(src))) {
      if (m[0].charAt(1) === '/') { depth--; if (depth === 0) return m.index; } else depth++;
    }
    return -1;
  }
  function interp(s, scope) {
    s = s.replace(/on[A-Z]\w*="\{\{\s*([\w.$]+)\s*\}\}"/g, function (_, p) {
      var fn = lookup(p, scope);
      if (typeof fn !== 'function') return '';
      handlers.push(fn);
      return 'data-dc-click="' + (handlers.length - 1) + '"';
    });
    return s.replace(/\{\{\s*([^}]+?)\s*\}\}/g, function (_, p) { return esc(lookup(p, scope)); });
  }
  function render(src, scope) {
    var out = '', i = 0;
    while (i < src.length) {
      var re = /<sc-(for|if)\b[^>]*>/g;
      re.lastIndex = i;
      var m = re.exec(src);
      if (!m) { out += interp(src.slice(i), scope); break; }
      out += interp(src.slice(i, m.index), scope);
      var tag = 'sc-' + m[1], openEnd = m.index + m[0].length;
      var close = findClose(src, openEnd, tag);
      var inner = src.slice(openEnd, close);
      if (m[1] === 'for') {
        var list = lookup(attr(m[0], 'list') || '', scope) || [];
        var as = attr(m[0], 'as') || 'item';
        for (var k = 0; k < list.length; k++) {
          var s2 = Object.create(scope); s2[as] = list[k]; s2.$index = k;
          out += render(inner, s2);
        }
      } else if (lookup(attr(m[0], 'value') || 'false', scope)) {
        out += render(inner, scope);
      }
      i = close + tag.length + 3;
    }
    return out;
  }
  window.DCLogic = function (props) { this.props = props || {}; this.state = {}; };
  window.DCLogic.prototype.setState = function (p) { Object.assign(this.state, p); window.__dcRender(); };
  window.DCLogic.prototype.forceUpdate = function () { window.__dcRender(); };
  window.__dcMount = function (Component, props) {
    var root = document.getElementById('dc-root');
    var tpl = document.getElementById('dc-template').textContent;
    var inst = new Component(props);
    window.__dcRender = function () {
      var vals = [].map.call(root.querySelectorAll('input,textarea,select'), function (el) { return el.value; });
      handlers = [];
      root.innerHTML = render(tpl, inst.renderVals());
      [].forEach.call(root.querySelectorAll('input,textarea,select'), function (el, n) { if (vals[n] !== undefined && el.tagName !== 'SELECT') el.value = vals[n]; });
    };
    root.addEventListener('click', function (e) {
      var t = e.target.closest('[data-dc-click]');
      if (t) handlers[+t.getAttribute('data-dc-click')]();
    });
    window.__dcRender();
  };
})();
