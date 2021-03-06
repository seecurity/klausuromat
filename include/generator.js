// Generated by CoffeeScript 1.6.2
(function() {
  var __indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

  String.prototype.between = function(start, stop, escape) {
    var pAfter, pBefore, pos;

    pBefore = this.indexOf(start);
    pos = 0;
    while (true) {
      pAfter = this.indexOf(stop, pos);
      if (pAfter === -1 || this.substring(pAfter, pAfter + escape.length) !== escape) {
        break;
      }
      pos = pAfter + escape.length;
    }
    if (pBefore === -1 || pAfter === -1) {
      return [null, null, this.toString()];
    }
    return [this.substring(0, pBefore), this.substring(pBefore + start.length, pAfter).replace(escape, stop), this.substring(pAfter + stop.length)];
  };

  ($(document)).ready(function() {
    var after, before, content, element, escape, i, lang, line, lines, pos, raw, remove, replace, search, splitter, start, stop, str, strings, text, _, _i, _j, _len, _len1, _ref, _ref1, _ref2, _ref3, _ref4, _ref5, _results;

    _ref = $('pre[class*=lang]');
    _results = [];
    for (_i = 0, _len = _ref.length; _i < _len; _i++) {
      element = _ref[_i];
      element = $(element);
      _ref1 = ['#{', '}', '}}', '\n'], start = _ref1[0], stop = _ref1[1], escape = _ref1[2], splitter = _ref1[3];
      _ref2 = [';;', '<br />'], search = _ref2[0], replace = _ref2[1];
      lines = element.html().split(splitter);
      strings = [];
      remove = [];
      _ref3 = element.html().split(splitter);
      for (i = _j = 0, _len1 = _ref3.length; _j < _len1; i = ++_j) {
        line = _ref3[i];
        _ref4 = line.between(start, stop, escape), before = _ref4[0], text = _ref4[1], after = _ref4[2], raw = _ref4[3];
        if (text) {
          strings.push([i - remove.length - 1, text.split(search).join(replace)]);
          remove.push(i);
        }
      }
      element.html(((function() {
        var _k, _len2, _results1;

        _results1 = [];
        for (i = _k = 0, _len2 = lines.length; _k < _len2; i = ++_k) {
          line = lines[i];
          if (__indexOf.call(remove, i) < 0) {
            _results1.push(line);
          }
        }
        return _results1;
      })()).join('\n'));
      _ref5 = element.attr('class').split(':'), _ = _ref5[0], lang = _ref5[1];
      element.snippet(lang, {
        style: 'ide-eclipse'
      });
      content = element.html();
      lines = $('ol', element).children();
      _results.push((function() {
        var _k, _len2, _ref6, _results1;

        _results1 = [];
        for (_k = 0, _len2 = strings.length; _k < _len2; _k++) {
          str = strings[_k];
          _ref6 = str, pos = _ref6[0], str = _ref6[1];
          _results1.push($(lines[pos]).append("<div class=\"hint\">" + str + "</div>"));
        }
        return _results1;
      })());
    }
    return _results;
  });

}).call(this);
