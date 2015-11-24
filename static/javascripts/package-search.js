
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


$(document).ready(function() {

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
          var fuzzyMatch = new RegExp(request.term.split('').join('\\w*').replace(/\W/, ""), 'i');
          response($.grep(Object.keys(options), function(item) {
            return fuzzyMatch.test(options[item]);
          }));
        },

        select: function(event, ui) {
          event.preventDefault();
          $("#package-search input").val('');

          var selected = ui.item.value;
          window.location = 'https://github.com/'.concat(selected);
        }

      }).focus();

    }
  });


});
