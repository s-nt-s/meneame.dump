sigma.classes.graph.addMethod('neighbors', function(nodeId) {
  var k;
  var neighbors = {};
  var index = this.allNeighborsIndex[nodeId] || {};
  for (k in index) neighbors[k] = this.nodesIndex[k];
  return neighbors;
});

$(document).ready(function(){

$("div.graph").each(function(){
  var $this = $(this);
  if ($this.find("div").length==0) $this.append(`
    <div class="rootpanel">
      <div class='panel'></div>
    </div>
    <p class="caption" style="display:none"></p>
  `);

  var s = new sigma({
    graph: graphs[$this.data("graph")],
    renderer: {
      container: $this.find("div.panel")[0],
      type: 'canvas'
    },
    settings: {
     minEdgeSize: 0.5,
     maxEdgeSize: 5,
     labelThreshold: 0
   }
  });
  s.graph.nodes().forEach(function(n) {
    n.hidden = false;
    if (n.label==null) n.label = n.id;
    n.originalColor = n.color;
    n.originalLabel = n.label;
  });
  s.graph.edges().forEach(function(e) {
    if (e.color==null) e.color = "grey";
    e.hidden = false;
  });
  s.refresh()

  s.bind('clickNode', function(e) {
    var s  = e.target;
    if (e.data.node.selected) {
      e.data.node.selected=false;
      s.dispatchEvent('reset');
      return;
    }
    var container = s.renderers[0].container;
    var caption = container?$(s.renderers[0].container).closest("div.graph").find(".caption"):$([]);
    caption.hide();
    var nodeId = e.data.node.id;
    var toKeep = s.graph.neighbors(nodeId);
    toKeep[nodeId] = e.data.node;

    s.graph.nodes().forEach(function(n) {
      n.label = n.originalLabel;
      if (toKeep[n.id]) {
        n.hidden = false;
        if (n.id == nodeId) {
          n.color = "red";
          n.selected = true;
        }
        else n.color = "blue"; //n.originalColor;
      } else {
        n.hidden = true;
      }
    });
    var high_sibling={};
    s.graph.edges().forEach(function(e) {
      if (e.source!=nodeId && e.target!=nodeId || !(toKeep[e.source] && toKeep[e.target])) {
        e.hidden = true;
        return;
      }
      e.hidden = false;
      var me = e.source;
      var ot = e.target;
      if (ot == nodeId) {
        me = e.target;
        ot = e.source;
      }
      me = s.graph.nodes(me);
      ot = s.graph.nodes(ot);

      ot.prc = null;
      if (me.weight!=null && e.weight!=null) {
        ot.prc = e.weight*100/me.weight;
      }
      if (ot.prc!=null) {
        var m;
        var d=0;
        var prc=0;
        while (prc==0) {
          m = Math.pow(10, d);
          prc = Math.round(ot.prc*m)/m;
          d++;
        }
        ot.label = prc+"% "+ot.originalLabel;
      }
      if (high_sibling.prc == null || high_sibling.prc<ot.prc) {
        high_sibling = ot;
      }
      //e.label = e.originalLabel;
    });

    // Since the data has been modified, we need to
    // call the refresh method to make the colors
    // update effective.
    s.refresh();
    if (high_sibling.prc) {
      var prc = Math.round(high_sibling.prc);
      if (prc == 0) prc=Math.round(high_sibling.prc*100)/100;
      //high_sibling.color = "green";
      caption.html(
        "El "+prc+"% de las noticias etiquetas con <code>"+
        s.graph.nodes(nodeId).label+"</code> tambien tienen la etiqueta <code>"+
        high_sibling.originalLabel+"</code>"
      ).show();
    }
    s.refresh();
  });

  // When the stage is clicked, we just color each
  // node and edge with its original color.
  s.bind('reset', function(e) {
    var s  = e.target;
    var container = s.renderers[0].container;
    var caption = container?$(s.renderers[0].container).closest("div.graph").find(".caption"):$([]);
    caption.hide();
    s.graph.nodes().forEach(function(n) {
      n.color = n.originalColor;
      n.label = n.originalLabel;
      n.hidden = false;
    });

    s.graph.edges().forEach(function(e) {
      e.hidden = false;
    });

    // Same as in the previous event:
    s.refresh();
  });

  //s.refresh();
  $this.data("mygraph", s);
});

})
