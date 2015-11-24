
/* stolen from http://stackoverflow.com/questions/3870019/javascript-parser-for-a-string-which-contains-ini-data */
function parseINIString(data){
  var regex = {
    section: /^\s*\[\s*([^\]]*)\s*\]\s*$/,
    param: /^\s*([\w\.\-\_]+)\s*=\s*(.*?)\s*$/,
    comment: /^\s*;.*$/
  };
  var match;
  var value = {};
  var lines = data.split(/\r\n|\r|\n/);
  var section = null;
  lines.forEach(function(line){
    if(regex.comment.test(line)){
      return;
    } else if(regex.param.test(line)){
      match = line.match(regex.param);
      if(section){
        value[section][match[1]] = match[2];
      }else{
        value[match[1]] = match[2];
      }
    } else if(regex.section.test(line)){
      match = line.match(regex.section);
      value[match[1]] = {};
      section = match[1];
    } else if(line.length === 0 && section){
      section = null;
    }
  });
  return value;
}

/* from http://stackoverflow.com/questions/901115/how-can-i-get-query-string-values-in-javascript */
function getParameterByName(name) {
  name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
  var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
    results = regex.exec(location.search);
  return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}

function fuzzyMatchRepos(repos, query, response) {
  var fuzzyMatch = new RegExp(query.split('').join('\\w*').replace(/\W/, ""), 'i');
  response($.grep(Object.keys(repos), function(item) {
    return fuzzyMatch.test(repos[item]);
  }));
}

$(document).ready(function() {

  var query = getParameterByName('q');
  $("#package-search input").val(query);

  $.ajax({
    url: 'sources.cfg',
    type: 'GET',
    success: function(data) {
      var sourcesCFG = parseINIString(data);
      var options = {};
      $(Object.keys(sourcesCFG.sources)).each(function() {
        var reponame = sourcesCFG.forks[this] + '/' + this;
        options[reponame] = reponame.replace(/\W/, "");
      });

      $("#package-search input").autocomplete({
        source: function(request, response) {
          fuzzyMatchRepos(options, request.term, response);
        },

        select: function(event, ui) {
          event.preventDefault();
          $("#package-search input").val('');

          var selected = ui.item.value;
          window.location = 'https://github.com/'.concat(selected);
        }

      }).focus();
      $("#package-search input").autocomplete("search");

      fuzzyMatchRepos(options, query, function(result) {
        if (result.length === 1)
          window.location = 'https://github.com/'.concat(result[0]);
      });
    }
  });


});
