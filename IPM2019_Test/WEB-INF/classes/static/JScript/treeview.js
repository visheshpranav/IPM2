/* 
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
 
 var w = 1020,
    h = 800,
    i = 0,
    barHeight = 25,
    barWidth = w * 2,
    duration = 400,
    root;
//aish
var margin = {top: 20, right: 20, bottom: 30, left: 20},
    width = 960,
    barHeight = 20,
    barWidth = (width - margin.left - margin.right) *.9;

var i = 0,
    duration = 400,
    root;





	//aish end

var tree = d3.layout.tree()
    .size([h, 100]);

var diagonal = d3.svg.diagonal()
    .projection(function(d) { return [d.y, d.x]; });

var vis = d3.select("#chart").append("svg:svg")
    .attr("width", w)
    .attr("height", h)
  .append("svg:g")
    .attr("transform", "translate(20,30)");

function moveChildren(node) {
    if(node.children) {
        node.children.forEach(function(c) { moveChildren(c); });
        node._children = node.children;
        node.children = null;
    }
}

var foldername= localStorage.getItem("ipm_UserId") + "_"+ localStorage.getItem("reportname");
function loadata(file)
{

d3.json(file, function(json) {
  json.x0 = 0;
  json.y0 = 0;
  moveChildren(json);
  update(root = json);
});
}
function update(source) {

  // Compute the flattened node list. TODO use d3.layout.hierarchy.
  var nodes = tree.nodes(root);
  
  // Compute the "layout".
  nodes.forEach(function(n, i) {
    n.x = i * barHeight;
    ////console.log("height --->"+(i*barHeight));
  });
  
  //aish
  var height = Math.max(500, nodes.length * barHeight + margin.top + margin.bottom);
  d3.select("svg").transition()
      .duration(duration)
      .attr("height", height);
  d3.select(self.frameElement).transition()
      .duration(duration)
      .style("height", height + "px");

// commented without scrollbar layout - Compute the "layout". TODO https://github.com/d3/d3-hierarchy/issues/67
 /* var index = -1;
  root.eachBefore(function(n) {
    n.x = ++index * barHeight;
    n.y = n.depth * 20;
  });*/
  
  
  // Update the nodes…
  var node = vis.selectAll("g.node")
      .data(nodes, function(d) { return d.id || (d.id = ++i); });
  
  var nodeEnter = node.enter().append("svg:g")
      .attr("class", "node")
      .attr("transform", function(d) { return "translate(" + source.y0 + "," + source.x0 + ")"; })
      .style("opacity", 1e-6);

  // Enter any new nodes at the parent's previous position.
  nodeEnter.append("svg:rect")
      .attr("y", -barHeight / 2)
      .attr("height", barHeight)
      .attr("width", function(d) {
            return Math.max(d.name.length * 9, barWidth);
        })
      .style("fill", color)
      .on("click", click);
    
   //aish -dynamic sizing
/*   nodeEnter.append("svg:rect")
      .attr("y", -barHeight / 2)
      .attr("height", barHeight)
      .attr("width", function(d){
           
          if(d.name==("TITAN"))
                return (d.name*8);
          else if(d.tag=="Module")
              return (d.name+ "   ---Instruction Coverage-"+ Math.round(d.Module_covered)+"%")*2;
          else if(typeof(d.branch_covered)==("undefined"||"NaN"))
              return (d.name+ "   --- Instruction Coverage-"+ Math.round(d.percent_covered)+"%"+" --- Branch Coverage - NA ")*3;
          else
              return (d.name+ "   --- Instruction Coverage-"+ Math.round(d.percent_covered)+"%"+" --- Branch Coverage - "+Math.round(d.branch_covered)+"%")*3; 
    })
      .style("fill", color)
      .on("click", click);
    */
   /* for image */
     /*   nodeEnter
                .append("svg:a")
                .append("image")
                .attr(
                        "xlink:href",
                        function(d) {
                            if (d._children != 0 && (!d.children)){
                                return "/images/expand.png"
                             //   console.log("Image Loop");
                            }
                            else if (d.children && (!d._children))
                                return "/images/collapse.png";
                            else if ((!d.children) && (d._children.lenght == 0))
                                return "";
                        }).attr("width", function(d) {
                        //    console.log("length comp->"+d.name+"  ->"+d.name.length+" length-"+Math.max((d.name.length + 54 )* 6));
                    return Math.max((d.name.length + 64 )* 6, barWidth);
                })
                        .attr("y", "15").attr("height", "12px").on("click", click);
                

       // var diagonal = d3.svg.diagonal().projection(function(d) {
      //      return [ d.x + (barWidth / 2), d.y + (barHeight / 2) ];
       // });*/
       
                // aish end 
        
  nodeEnter.append("svg:text")
      .attr("dy", 3.5)
      .attr("dx", 5.5)
      .text(function(d){
          if(d.name=="Root" || d.name=="DM Table" || d.name=="DM Reports")
                return d.name;
		  else if(d.name == d.value)
              return d.name;
          else if(d.Count == "" || d.Count==undefined)
              return d.name+ "---" + d.value;
		  else 
			  return d.name+ "---" + d.value;
             // return d.name+ "---"+ d.value +"---"+ "Count--> "+d.Count;
    
          
  });
  
  
  
  // Transition nodes to their new position.
  nodeEnter.transition()
      .duration(duration)
      .attr("transform", function(d) { return "translate(" + d.y + "," + d.x + ")"; })
      .style("opacity", 1);
  
  node.transition()
      .duration(duration)
      .attr("transform", function(d) { return "translate(" + d.y + "," + d.x + ")"; })
      .style("opacity", 1)
    .select("rect")
      .style("fill", color);
  
  // Transition exiting nodes to the parent's new position.
  node.exit().transition()
      .duration(duration)
      .attr("transform", function(d) { return "translate(" + source.y + "," + source.x + ")"; })
      .style("opacity", 1e-6)
      .remove();
  
  // Update the links…
  var link = vis.selectAll("path.link")
      .data(tree.links(nodes), function(d) { return d.target.id; });
  
  // Enter any new links at the parent's previous position.
  link.enter().insert("svg:path", "g")
      .attr("class", "link")
      .attr("d", function(d) {
        var o = {x: source.x0, y: source.y0};
        return diagonal({source: o, target: o});
      })
    .transition()
      .duration(duration)
      .attr("d", diagonal);
  
  // Transition links to their new position.
  link.transition()
      .duration(duration)
      .attr("d", diagonal);
  
  // Transition exiting nodes to the parent's new position.
  link.exit().transition()
      .duration(duration)
      .attr("d", function(d) {
        var o = {x: source.x, y: source.y};
        return diagonal({source: o, target: o});
      })
      .remove();
  
  // Stash the old positions for transition.
  nodes.forEach(function(d) {
    d.x0 = d.x;
    d.y0 = d.y;
  });
}
//aishvar
 lastClickD = null;
function click(d) {
  if (d.children) {
    d._children = d.children;
    d.children = null;
  } else {
    d.children = d._children;
    d._children = null;
  }
  if (lastClickD){
    lastClickD._isSelected = false;
  }
  d._isSelected = true;
  lastClickD = d;
  update(d);
}

function setLabel(d){
    
}
// on the selected one change color to red
function color(d) {
    
 
if(d.name == "Root" )
     return '#3700B3';
else if(d.tag=="Node0"){
    return '#6200EE';
}
else if(d.tag=="Node1" || d.tag=="Node2" || d.tag=="Node3" ){
    return "#BB86FC";
}
else if(d.tag=="Node4" || d.tag=="Node5" || d.tag=="Node6" || d.tag=="Node7" ){
    return "#BB86FC";
}
else
{
	return "#6200EE";
}
 
}

function expand(d){   
    var children = (d.children)?d.children:d._children;
    if (d._children) {        
        d.children = d._children;
        d._children = null;       
    }
    if(children)
      children.forEach(expand);
}

function expandall(){
    expand(root); 
    update(root);
}

function collapse(d) {
  if (d.children) {
    d._children = d.children;
    d._children.forEach(collapse);
    d.children = null;
  }
}


function collapseall(){
    root.children.forEach(collapse);
    collapse(root);
    update(root);
}



    
     function zoom() {
        svgGroup.attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");
    }



/*commented'// Toggle children on click.
function click(d) {
  if (d.children) {
    d._children = d.children;
    d.children = null;
  } else {
    d.children = d._children;
    d._children = null;
  }
  update(d);
}

function color(d) {
  return d._children ? "#3182bd" : d.children ? "#c6dbef" : "#fd8d3c";
}
*/

