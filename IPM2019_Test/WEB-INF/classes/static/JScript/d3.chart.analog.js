(function () {
	var x_val1 = 0;
	var c1 = "";
    d3.analog= function() {
		var containerWidth = 800, containerHeight = 450;
		var margin = { top: 100, right: 50, bottom: 30, left: 60 },
		width = containerWidth - margin.left - margin.right;
            var height = 100, gap=10,
                xValue = function(d) { return d[0]; },
                xScale = null,
                color = d3.scale.category10();
            function chart(selection) {
                selection.each(function(d) {
					//console.log(d);
                    var g = d3.select(this);
                    var chartConfig = this.__chart__;

                    if (chartConfig) {
                        var yDomain = chartConfig.yDomain;
                        var y = chartConfig.y;
                    } else {
                        var minY = _.min(d.data, function(v) {
                            return _.chain(d.yVal).map(function(c) { return v[c]; }).min().value();
                        });
                        var maxY = _.max(d.data, function(v) {
                            return _.chain(d.yVal).map(function(c) { return v[c]; }).max().value();
                        });
                        minY = _.chain(d.yVal).map(function(c) { return minY[c]; }).min().value();
                        maxY = _.chain(d.yVal).map(function(c) { return maxY[c]; }).max().value();
                        yDomain = [minY, maxY];
						var x = d3.time.scale().range([0, width]);
                        y = d3.scale.linear().domain(yDomain).range([height - gap, 0]);
                        var yAxis = d3.svg.axis().scale(y).orient("left").ticks(6);
                        g.attr('id', d.id) // add y axis
                            .append('g')
                            .attr("class", "y axis")
                            //.attr('transform', 'translate(-1, 0)') // avoid making the vertical line disappear by clip when zoomed with brush
                            .call(yAxis);
                    }

                    //add path for each y-Value dimension 
                    _.each(d.yVal, function(c, i,yDim) {
                        //setup line function
						var x_val;
                        var valueline = d3.svg.line()
                            //.interpolate('basis')
                            //.x(function (a) { return xScale(moment(a.DateTime).toDate()); })
                            .x(X)
                            .y(function (a) { return y(a[c]); });
						var valueline1 = d3.svg.line()
                            //.interpolate('basis')
                            //.x(function (a) { return xScale(moment(a.DateTime).toDate()); })
                            .x(X)
                            .y(function (a) { console.log(a[c]); return y(a[c]); });
						
						//console.log(xDim);
                        if (chartConfig) {
							//console.log(d.data);
                            g.select(".path." + c).transition().duration(1000) //update path
                                .attr("d", valueline(d.data));
                        } else {
                            g.append("path") //add path 
                                .attr('class', 'path ' + c)
                                .attr("d", function(d){
									var valin_arr = valueline(d.data).split(",");
									//console.log(valin_arr);
								x_val = valin_arr[valin_arr.length-1];
								return valueline(d.data);})
                                .attr("clip-path", "url(#clip)")
                                .style('stroke', color(d.id + i));
                            //add legend
                            g.append('text').text(d.name)
                                .attr('class', 'legend')
                                .attr('x', 10).attr('y', 1);
								
							
							// g.append("text")
							  // .attr("transform", "translate("+(width+200)+","+x_val+")")
							  // .attr("dy", ".35em")
							  // .attr("text-anchor", "start")
							  // .style("font-size", "10px")
								// .style("font-weight", "bold")
								// .style("font-family", "Verdana, sans-serif")
							  // .text(function(d){								
							  // if (x_val1 == x_val){	
								  // c =c1+"/"+c;
								  // }
								  // c1 = c;
								  // x_val1 = x_val; 
								  // return c;});
                        }
                    });


                    //stash chart settings for update
                    this.__chart__ = { yDomain: yDomain, y: y };
                });
            }

            // The x-accessor for the path generator; xScale 

            function X(d) {
                return xScale(xValue(d));
            }

            chart.timeScale = function(_) {
                if (!arguments.length) return xScale;
                xScale = _;
                return chart;
            };

            chart.x = function(_) {
                if (!arguments.length) return xValue;
                xValue = _;
                return chart;
            };

            chart.height = function(_) {
                if (!arguments.length) return height;
                height = _;
                return chart;
            };
            chart.gap = function (_) {
                if (!arguments.length) return gap;
                gap = _;
                return chart;
            };

            chart.color = function(_) {
                if (!arguments.length) return color;
                color = _;
                return chart;
            };
        

            return chart;    
    };
        
})();