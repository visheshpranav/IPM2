/*
 Copyright (c) 2016, BrightPoint Consulting, Inc.

 MIT LICENSE:

 Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
 documentation files (the "Software"), to deal in the Software without restriction, including without limitation
 the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
 and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

 The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
 TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
 THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
 CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
 IN THE SOFTWARE.
 */

// @version 1.1.54

//**************************************************************************************************************
//
//  This is a test/example file that shows you one way you could use a vizuly object.
//  We have tried to make these examples easy enough to follow, while still using some more advanced
//  techniques.  Vizuly does not rely on any libraries other than D3.  These examples do use jQuery and
//  materialize.css to simplify the examples and provide a decent UI framework.
//
//**************************************************************************************************************

var ttip1=[];
var data = {};
var viz_container;
var viz;
var theme;
var valueField = "";
var level_length = 0;
var level_arr=[];
var expand_i = 1;



function loadData(file) {
	
	
	var valueFields = [];	
	var viz_container;
	var viz;
	var theme;
	data = {};
	//inserted
	var faultReason = "";
	var faultReasons = [];
	var ttipkey="";
	var ttipkeys=[];
	valueField = "Count";
	valueFields = ["Count"];
	faultReason = "F3";
	faultReasons = ["F3"];
	ttipkey="Level3";
	ttipkeys=["Level3"];
	document.getElementById("viz_container").innerHTML = "";

	
	
	/*var testname = localStorage.getItem("testname").toLowerCase();
	var userid = localStorage.getItem("UserId");
	var prjid = localStorage.getItem("PrjId");
	test_log = userid + "_"+prjid+"_"+testname;*/
//weightedtree_federal_budget faultmodel  Mumbai_Fault_Model
//DeliverableWF
    d3.csv(file, function (csv) {
        data.values=prepData(csv, valueFields, faultReasons);
		console.log(data);
        var blob = JSON.stringify(data);
        initialize(valueField, faultReason, ttipkey);

    });
	
}

/*function rearrange(csv)
{	
	var valueFields = [];	
	var viz_container;
	var viz;
	var theme;
	data = {};
	//inserted
	var faultReason = "";
	var faultReasons = [];
	var ttipkey="";
	var ttipkeys=[];
	valueField = "Failures";
	valueFields = ["Failures"];
	faultReason = "F3";
	faultReasons = ["F3"];
	ttipkey="Level3";
	ttipkeys=["Level3"];
	document.getElementById("viz_container").innerHTML = "";
	data.values=prepData(csv, valueFields, faultReasons);
	var blob = JSON.stringify(data);
	console.log(data);
	initialize(valueField, faultReason, ttipkey);
}*/

var formatCurrency = function (d) {
	return  (d)
};

function prepData(csv, valueFields, faultReasons) {

    var values=[];
	 var values2=[];
	 level_length = d3.keys(csv[0]).length;
	 level_arr = d3.keys(csv[0]);
	/*csv.forEach(function(infoArray, index) {
	  dataString = infoArray.join(',');
	  csvContent += index < data.length ? dataString + '\n' : dataString;
	});)*/
    //Clean federal budget data and remove all rows where all values are zero or no labels
    csv.forEach(function (d,i) {
        var t = 0;
        for (var i = 0; i < valueFields.length; i++) {
            t += Number(d[valueFields[i]]);
			//console.log("old"+valueFields.length+" value(i)"+i+" "+d[valueFields[i]]);
        }
        if (t > 0) {
			//console.log("in push1");
            values.push(d);
        }
		//inserted
		 //var z = 0;
        for (var i = 0; i < faultReasons.length; i++) {
			//console.log("in push3");
            ttip1.push( (d[faultReasons[i]]));

			//values.push(d);

        }
		 // for (var i = 0; i < ttipkeys.length; i++) {

		//inserted end
    })
	//inserted key value

//inserted end

    //Make our data into a nested tree.  If you already have a nested structure you don't need to do this.
    var nest = d3.nest();
	level_arr.forEach(function(level){
	  if(level != "Count")
	  {
		nest = nest.key(d => d[level])
	  }
	});
	nest = nest.entries(values);
		/*for (var level_i=0; level_i < level_length-2; level_i++)
		{
			nest = nest.key(function (d) {
				nest = nest.key(d => d[level])
			})
		}
        .key(function (d) {

            return d.Level2;
        })
        .key(function (d) {
            return d.Level3;
        })
        .key(function (d) {
            return d.Level4;
        })
        .key(function (d) {
            return d.Level5;
        })	
        .key(function (d) {
            return d.Level6;
        })		
        .key(function (d) {
            return d.Level7;
        })		
        .key(function (d) {
            return d.Level8;
        })				
        .key(function (d) {
            return d.Level9;
        })	
        .key(function (d) {
            return d.Level10;
        })	
        .entries(values);*/


    //This will be a viz.data function;
    vizuly.core.util.aggregateNest(nest, valueFields, function (a, b) {
		//alert("a= "+a+"  b="+b);
        return Number(a) + Number(b);
    });

    //Remove empty child nodes left at end of aggregation and add unqiue ids
    function removeEmptyNodes(node,parentId,childId) {
        if (!node) return;
        node.id=parentId + "_" + childId;
        if (node.values) {
            for(var i = node.values.length - 1; i >= 0; i--) {
                node.id=parentId + "_" + i;
                if(!node.values[i].key && !node.values[i].Level4) {
                    node.values.splice(i, 1);
                }
                else {
                    removeEmptyNodes(node.values[i],node.id,i)
                }
            }
        }
    }

    var node={};
    node.values = nest;
   removeEmptyNodes(node,"0","0");


    var blob = JSON.stringify(nest);

    return nest;

}

function initialize(valueField, faultReason, ttipkey) {

    viz = vizuly.viz.weighted_tree(document.getElementById("viz_container"));


    //Here we create three vizuly themes for each radial progress component.
    //A theme manages the look and feel of the component output.  You can only have
    //one component active per theme, so we bind each theme to the corresponding component.
    theme = vizuly.theme.weighted_tree(viz).skin(vizuly.skin.WEIGHTED_TREE_AXIIS);

    //Like D3 and jQuery, vizuly uses a function chaining syntax to set component properties
    //Here we set some bases line properties for all three components.
    viz.data(data)                                                      // Expects hierarchical array of objects.
        .width(850)                                                     // Width of component
        .height(500)                                                    // Height of component
        .children(function (d) { return d.values })                     // Denotes the property that holds child object array
        .key(function (d) { return d.id })                              // Unique key
        .value(function (d) {
            return Number(d["agg_" + valueField]) })                    // The property of the datum that will be used for the branch and node size
        .fixedSpan(-1)                                                  // fixedSpan > 0 will use this pixel value for horizontal spread versus auto size based on viz width
        .branchPadding(.07)
        .label(function (d) {                                           // returns label for each node.
            return trimLabel(d.key || (d['s' + d.depth]))})
        .on("measure",onMeasure)                                        // Make any measurement changes
        .on("mouseover",onMouseOver)                                    // mouseover callback - all viz components issue these events
        .on("mouseout",onMouseOut)                                      // mouseout callback - all viz components issue these events
        .on("click",onClick);                                           // mouseout callback - all viz components issue these events



    //We use this function to size the components based on the selected value from the RadiaLProgressTest.html page.
   changeSize(d3.select("#currentDisplay").attr("item_value"));

    // Open up some of the tree branches.
    /*viz.toggleNode(data.values[0]);
    viz.toggleNode(data.values[0].values[0]);	
    viz.toggleNode(data.values[0]);
	viz.toggleNode(data.values[0].values[0]);
	viz.toggleNode(data.values[0].values[0].values[0]);*/

}


function trimLabel(label) {
   return (String(label).length > 10) ? String(label).substr(0, 8) + "..." : label;
   //return (String(label).length > 20) ? String(label).substr(0, 17) + "..." : label;
}


var datatip='<div class="tooltip" style="width: 100px; opacity:0.5; word-break: break-all;font-family: AccentureRotis,Arial,sans-serif;">' +
    '<div style="font-weight:bold; font-size: 12px; text-align: center;margin-bottom: 2px; font-family: AccentureRotis,Arial,sans-serif;">HEADER1</div>' +
    //'<div class="header-rule"></div>' +
    '<div style="font-size: 11px;text-align: center; font-family: AccentureRotis,Arial,sans-serif;">HEADER2</div>' +
    //'<div class="header-rule"></div>' +
    //'<div class="header3"> HEADER3 </div>' +
    '</div>';


// This function uses the above html template to replace values and then creates a new <div> that it appends to the
// document.body.  This is just one way you could implement a data tip.
function createDataTip(x,y,h1,h2,h3) {

    var html = datatip.replace("HEADER1", h1);
    html = html.replace("HEADER2", h2);
    //html = html.replace("HEADER3", h3);
	//console.log("h1"+h1);
    d3.select("body")
        .append("div")
        .attr("class", "vz-weighted_tree-tip")
        .style("position", "absolute")
        .style("top", y + "px")
        .style("left", (x + 55) + "px")
        .style("opacity",0)
        .html(html)
        .transition().style("opacity",1);

}

function onMeasure() {
    viz.tree().nodeSize([100,0]);
}

function onMouseOver(e,d,i) {
   // console.log("mouse over");
    if (d == data) return;
    var rect = e.getBoundingClientRect();
    if (d.target) d = d.target; //This if for link elements
	{
		if(d.depth=="20"){
			//console.log("in 3"+d.Level4);
		var temp1=d.F3;
			console.log("print-"+d["agg_Tcode"]+"-key-"+formatCurrency(d["agg_" + valueField]));
/* 	createDataTip(rect.left,
	(rect.top+viz.height() *.10),
	"Details",
	" Tcode failures: "+ d["agg_" + valueField]+"/"+d["agg_TcodeCount"] +"\n"+
	"Impacted Users: "+d["agg_UserCount"]+"/"+d["agg_TotalUserCount"],
	""); */

	}
	

		
	else{
		var keyvalue = "";
		var key_count=0;
				
		if(d.depth <= 13)
		{
			
			key_count = d._children.length;
			key_count = "No of types - "  + key_count.toString();
			
		}
		else{
				key_count = d["agg_" + valueField];
			}
		if(d.depth > 13)
		{
			key_count = "Count - " + key_count.toString()	
		}
	
		keyvalue = d.key;
		
		
		
    createDataTip(rect.left, (rect.top+viz.height() *.05), ( keyvalue ||(d['Level' + d.depth])), key_count,key_count);
	//console.log("val"+" key"+d["agg_" + faultReason] +" depth- "+(d['Level']));
	}
	}
}
	
function get_countVal(dep_children)
{
	var key_count = 0;
	if(dep_children.children != "" && dep_children.children != undefined)
	{
		for(var dep_2=0; dep_2<dep_children.children.length; dep_2++)
		{
			key_count = key_count + master_unique[dep_children.children[dep_2].key];
		}
	}
	else{
		for(var dep_2=0; dep_2<dep_children._children.length; dep_2++)
		{
			key_count = key_count + master_unique[dep_children._children[dep_2].key];
		}
	}
	return key_count;
}

function onMouseOut(e,d,i) {
    d3.selectAll(".vz-weighted_tree-tip").remove();
}

//We can capture click events and respond to them
function onClick(g,d,i) {
	viz.tree().nodeSize([100,0]);
	if(d.values[0].key != "undefined" && d.values[0].key != undefined)
	{
		viz.toggleNode(d);
	}
    //viz.toggleNode(d);
}


/*function onClick(g,d,i) {
	if(d.values[0].key != "undefined" && d.values[0].key != undefined && d.values[0].key != "Trade characteristics" && d.values[0].key != Trade characteristics)
	{
		viz.toggleNode(d);
	}
    //viz.toggleNode(d);
}*/


//This function is called when the user selects a different skin.
function changeSkin(val) {
    if (val == "None") {
        theme.release();
    }
    else {
        theme.viz(viz);
        theme.skin(val);
    }

    viz().update();  //We could use theme.apply() here, but we want to trigger the tween.
}

//This changes the size of the component by adjusting the width/height;
function changeSize(val) {
    var s = String(val).split(",");
    viz_container.transition().duration(300).style('width', s[0] + 'px').style('height', s[1] + 'px');
    viz.width(s[0]).height(s[1]*.8).update();
}

//This sets the same value for each radial progress
function changeData(val) {

    valueField=valueFields[Number(val)];
    viz.update();
}
function expand(data) {
    var children = (data.children) ? data.children : data._children;
    if (data._children) {
		if(data._children[0].key != undefined)
		{
			if(data.depth < 3 && expand_i==1)
			{
				data.children = data._children;
				data._children = null;
			}
			else if(expand_i==2){
				data.children = data._children;
				data._children = null;
			}
		}
    }
    if (children) children.forEach(expand);
}

function collapse(d) {
    if (d.children) {
      d._children = d.children;
      d._children.forEach(collapse);
      d.children = null;
    }
}

function expandall(){
    expand(data)
	if(expand_i == 1)
	{
		expand_i = expand_i + 1;
	}
    viz.update();
}

function collapseall(){
	expand_i = 1;
    data.children.forEach(collapse);
    viz.update();
}

/*function collapseall(){
    collapse(data)
    viz.update();
}*/