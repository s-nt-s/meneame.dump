jQuery.fn.extend({
  column: function() {
    if (this.length!=1 && !this.is("th")) return null;
    var index=this.closest("tr").find("th").index(this);
    return this.closest("table").find("tbody tr").find("td:eq("+index+")");
  },
  reverse: Array.prototype.reverse,
});

function mkTableSortable(scope) {
  if (!scope) scope=$("body");
  scope = scope.filter("table:has(.isSortable)").add(scope.find("table:has(.isSortable)"));
  scope.find("thead th.isSortable").each(function(){
    var t=$(this);
    var cl = t.column().map(function(){ return this.textContent.trim() })
    var dif = [...new Set(cl.get())]
    if (dif.length<2) {
      t.removeClass("isSortable");
    } else {
      var table = t.closest("table").find("tbody");
      var trs = table.find("tr");
      var index = t.closest("tr").find("th").index(t);
      t.data("index", index);
      var tdsel = "td:eq("+index+")";
      var isStr = t.is(".str");
      var i;
      for (i=0; i<trs.length;i++) {
        var td = trs.eq(i).find(tdsel);
        if (td.data("sortkey") == null) {
          var sortkey = td.text().trim();
          if (isStr) {
            sortkey = sortkey.toLowerCase();
          } else {
            if (typeof sortkey == "string") sortkey = Number(sortkey.replace("%", ""));
          }
          td.data("sortkey", sortkey)
        }
      }
    }
  })
  scope.find("th.isSortable").closest("table").find("tbody tr").each(function(index){
    this.setAttribute("data-rownum", index);
  })
  scope.find("th.isSortable").each(function() {
    var t=$(this);
    var index = t.data("index");
    var tdsel = "td:eq("+index+")";
    var order = t.closest("table").find("tbody tr").get().map(function(tr){
      tr = $(tr);
      return [tr.data("rownum"), tr.find(tdsel).data("sortkey")];
    }).sort(function(a, b) {
      if (typeof a[1] == "number") return a[1] - b[1];
      return a[1].localeCompare(b[1])
    }).map(function(i) {
      return i[0];
    })
    t.data("order", order);
  });
  scope.find("th.isSortable").each(function(){
    if (this.title && this.title.trim().length) {
        this.title = this.title + " (haz click para ordenar)"
    } else {
        this.title = "Haz click para ordenar"
    }
  }).click(function () {
    var t = $(this);
    var doReversed = (t.is(".isSortedByMe") && !t.is(".isReversed"));
    t.closest("tr").find("th").removeClass("isSortedByMe isReversed");
    t.addClass("isSortedByMe");
    var table = t.closest("table").find("tbody");
    var order = t.data("order");
    if (doReversed) order = order.slice().reverse();
    order.forEach((o, i) => {
      var tr = table.find("tr[data-rownum="+o+"]");
      table.append(tr);
    });
    if (doReversed) {
      t.addClass("isReversed");
    } else {
      t.removeClass("isReversed");
    }
  });
}

$(document).ready(function(){
  mkTableSortable();
})
