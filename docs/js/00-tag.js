var mockAjax = (function mockAjax(){
    var timeout;
    return function(duration){
        clearTimeout(timeout); // abort last request
        return new Promise(function(resolve, reject){
            timeout = setTimeout(resolve, duration || 1000)
        })
    }
})()

// tag added callback
function onAddTag(e){
    //console.log("onAddTag: ", e.detail);
    //console.log("original input value: ", e.detail.tagify.DOM.originalInput.value)
    e.detail.tagify.off('add', onAddTag) // exmaple of removing a custom Tagify event
    //$(e.detail.tagify.DOM.originalInput).change();
}

// tag remvoed callback
function onRemoveTag(e){
    //console.log("onRemoveTag:", e.detail, "tagify instance value:", e.detail.tagify.value)
    //$(e.detail.tagify.DOM.originalInput).change();
}

// on character(s) added/removed (user is typing/deleting)
function onInput(e){
    //console.log("onInput: ", e.detail);
    e.detail.tagify.settings.whitelist.length = 0; // reset current whitelist
    e.detail.tagify.loading(true).dropdown.hide.call(e.detail.tagify) // show the loader animation

    // get new whitelist from a delayed mocked request (Promise)
    mockAjax()
        .then(function(){
            // replace tagify "whitelist" array values with new values
            // and add back the ones already choses as Tags
            var result = e.detail.tagify.settings.full_whitelist
            console.log("dadsadsad")
            e.detail.tagify.settings.whitelist.push(...result, ...e.detail.tagify.value)

            // render the suggestions dropdown.
            e.detail.tagify.loading(false).dropdown.show.call(e.detail.tagify, e.detail.value);
        })
}

function onTagEdit(e){
    //console.log("onTagEdit: ", e.detail);
}

// invalid tag added callback
function onInvalidTag(e){
    //console.log("onInvalidTag: ", e.detail);
}

// invalid tag added callback
function onTagClick(e){
    //console.log(e.detail);
    //console.log("onTagClick: ", e.detail);
}

function onTagifyFocusBlur(e){
    //console.log(e.type, "event fired")
}

function onDropdownSelect(e){
    //console.log("onDropdownSelect: ", e.detail)
}


$(document).ready(function(){
  $("input.tag_filter").each(function(){
    // initialize Tagify on the above input node reference
    var values = this.value;
    var $this = $(this);
    var full_whitelist = tags[$this.data("source")];
    if (full_whitelist==null) return;
    if ($this.data("addtowhitelist")) {
      var whitelist=$this.data("addtowhitelist").trim().split(/\s*,\s*/);
      if (whitelist.length) Array.prototype.push.apply(full_whitelist, whitelist);
    }
    if (values.startsWith("[{")) {
      values = JSON.parse(values).map(function(x){return x.value})
    } else {
      values = values.trim().split(/\s*,\s*/).filter(function(x){return x.length>0});
      if ($this.is(".domains")) {
          values = values.map(function(v){
            if (full_whitelist.indexOf(v)>-1) return v;
            if (!v.startsWith("*.")) return null;
            v = v.substr(2);
            if (full_whitelist.indexOf(v)>-1) return v;
            return null;
          }).filter(function(x){return x!=null})
          this.value = values.join(", ");
      }
    }
    values = values.filter(function (x) {return full_whitelist.indexOf(x)>-1})
    console.log(values);
    var tagify = new Tagify(this, {
        enforceWhitelist: true,
        whitelist: values, // Array of values. stackoverflow.com/a/43375571/104380
        full_whitelist: full_whitelist,
        dropdown : {
          classname     : "color-blue",
          enabled       : 0,              // show the dropdown immediately on focus
          maxItems      : Infinity,
          position      : "text",         // place the dropdown near the typed text
          closeOnSelect : false,          // keep the dropdown open after selecting a suggestion
          highlightFirst: true
      }
    })
    console.log(tagify.value);
    $this.data("mytagify", tagify)

    // Chainable event listeners
    tagify.on('add', onAddTag)
          .on('remove', onRemoveTag)
          .on('input', onInput)
          .on('edit', onTagEdit)
          .on('invalid', onInvalidTag)
          .on('click', onTagClick)
          .on('focus', onTagifyFocusBlur)
          .on('blur', onTagifyFocusBlur)
          //.on('dropdown:hide dropdown:show', e => console.log(e.type))
          .on('dropdown:select', onDropdownSelect)

  })
})
