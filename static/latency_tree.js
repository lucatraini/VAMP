function draw_latency_tree(checked){

  d3.select(".rpc").select("text").remove();

  d3.select(".service_name").select("text").remove();

  d3.select(".my_dataviz").select("svg").remove()
    // Get the window height
  const windowHeight = window.innerHeight;
  console.log(windowHeight)

  // Set the dimensions and margins of the diagram
  var margin = {top: 20, right: 90, bottom: 30, left: 90},
      width = 1900 - margin.left-margin.right,
      height = 1900 - margin.top - margin.bottom;

  var margin_div = {top: 20, right: 90, bottom: 30, left: 2200}

    //searchBox  
    
    var input = document.getElementById("service");
   
    input.addEventListener("keypress", function(event) {
      if (event.key === "Enter") {
        event.preventDefault();
        document.getElementById("myBtn").click();
      }
    });
    searchBox = document.querySelector("#searchBox");
    countries = document.querySelector("#service");
    var when = "change"; //You can change this to keydown, keypress or change
    
    searchBox.addEventListener("change", function (e) {
        var text = e.target.value; //searchBox value
        var options = countries.options; //select options
        for (var i = 0; i < options.length; i++) {
            var option = options[i]; //current option
            var optionText = option.text; //option text ("Somalia")
            var lowerOptionText = optionText.toLowerCase(); //option text lowercased for case insensitive testing
            var lowerText = text.toLowerCase(); //searchBox value lowercased for case insensitive testing
            var regex = new RegExp("^" + text, "i"); 
            var match = optionText.match(regex); //test if regExp is true
            var contains = lowerOptionText.indexOf(lowerText) != -1; //test if searchBox value is contained by the option text
            if (match || contains) { //if one or the other goes through
                option.selected = true; //select that option
                var value =option.value
                onChange(value)
                console.log(value)
                return ; //prevent other code inside this event from executing
            }
            console.log(value)
            searchBox.selectedIndex = 0; //if nothing matches it selects the default option
        }
    });

  //select
  var e = document.getElementById("service")
  
  //timestamp range
  document.getElementById("calc").onclick=function(){myfunction()};

  function myfunction() {
      var date_from = document.getElementById("date_from").value,
          time_from = document.getElementById("time_from").value

          var date_to = document.getElementById("date_to").value,
          time_to = document.getElementById("time_to").value
      
      draw_treeTimestamp(e.value,date_from,time_from,date_to,time_to)
      console.log(date_from,date_to)
      console.log(time_from,time_to)
  }


  function onChange() {

    d3.select(".barchart")
        .select("svg").select("g").selectAll(".bar2")
        .remove()
    
        d3.select(".my_dataviz")
        .select("svg").remove()
    
        d3.select(".my_dataviz1")
        .select("svg").remove()
        
    
    d3.select(".name").select("text").remove()
    d3.select("svg").remove()

    var svg = d3.select(".tree").append("svg")
              .attr("width", width + margin.right + margin.left)
              .attr("height", windowHeight-50-margin.top-margin.bottom)
              .attr("style", "outline: solid black;")

              .call(d3.zoom().scaleExtent([0.1, 2]).on("zoom", function () {
                svg.attr("transform", d3.event.transform)
              }))
              .append("g")
              .attr("width", width)
              .attr("height", height)
              .style("fill", "white")
              .attr("transform", "translate(" + margin.left + "," + margin.top  + ")");
      
  var i = 0,
      duration = 750,
      root;

  var data = [{key:""}];

  // get the data
  d3.json("compareLatency/"+e.value, function(error,treeData) {
    if (error) throw error;
    
    var children = treeData.children
    service_name=children[0].name
    
    //service Histogram
    drawHist();

    d3.select(".name").append("text")
      .attr("text-anchor", "middle")
      .attr("x", 4)
      .attr("y", 1)
      .style('font-size','30px')
      .style('position','absolute')
      .style('left','100px')
      .style('width','600px')
      .text(e.value);

    // declares a tree layout and assigns the size
    var treemap = d3.tree().size([height, width]);

    // Assigns parent, children, height, depth
    root = d3.hierarchy(treeData, function(d) { return d.children; });
    root.x0 = height / 2;
    root.y0 = 0;

    // Collapse after the second level
    //root.children.forEach(collapse);

    update(root);
   
    // Collapse the node and all it's children
    /*function collapse(d) {
      if(d.children) {
        d._children = d.children
        d._children.forEach(collapse)
        d.children = null
      }
    }
  */

  
  function update(source) {

    // Assigns the x and y position for the nodes
    var treeData = treemap(root);

    // Compute the new tree layout.
    var nodes = treeData.descendants(),
        links = treeData.descendants().slice(1);

    // Normalize for fixed-depth.
    nodes.forEach(function(d){ d.y = d.depth * 180});

    // ****************** Nodes section ***************************

    // Update the nodes...
    var node = svg.selectAll('g.node')
        .data(nodes, function(d) {return d.id || (d.id = ++i); });
    
    var timeout = null;

    d3.select("svg").on("dblclick.zoom", null);

    //Double-click
    var nodeEnter = node.enter().append('g')
        .attr('class', 'node')
        .attr("transform", function(d) {
          return "translate(" + source.y0 + "," + source.x0 + ")";
      })
      .on('dblclick', function(d){
        if (d.children) {
          d3.select("rect.node").style('stroke','black')

          d3.select(this).append("rect")
          .attr('cursor', 'pointer')
          .attr('class','addButton')
          .attr("width", 30)
          .attr("height", 30)
          .attr("x", (rectWidth-30))
          .attr("y", (rectHeight/8)-3)
          .style("fill",'white')
          .style('stroke',"black")
          .text('+')
          .style('position','center')
          .on('click', function(d){

          console.log('addButton')
        });


          console.log(d)
            d._children = d.children;
            

              const arr =[]
              for (i in d.descendants()){
                arr.push(parseInt(d.descendants()[i].data.fill.substr(1), 16))
              }
              min =  Math.min(...arr)
              color='#'+min.toString(16)
              if (color=='#ffffff'){
                color='#000000'
              }
              console.log(arr)
              console.log(color)
                
          // + button
          d3.select(this).append('text')
            .attr('class','text_button')
            .attr('cursor', 'pointer')
            .attr("x", (rectWidth-22))
            .attr("y", (rectHeight/2)-5)
            .text("+")
            .style('fill',color)
            .style('font-size','30px')
            .on('click', function(d){
            console.log('addButton')
            });
          

          d.children = null
        } else {
          
          d3.select(this).select(".text_button").remove()

          d3.select(this).select("rect.addbutton").remove()
          
          d.children = d._children;
          
          d._children = null;
        }
      update(d);
        
        clearTimeout(timeout)
        //click(d)
      });

      var rectHeight = 70, rectWidth = 160;
     
    //node clik
    nodeEnter.append('rect')
      .attr('class', 'node')
      .attr("width", rectWidth)
      .attr("height", rectHeight)
      .attr("x", 0)
      .attr("y", (rectHeight/2)*-1)
      .attr("rx","5")
      .style('stroke',"black")
      .style('fill', function(d) {
        return d.data.fill
      }).on('click', function(d) { 

        d3.select(".rpc").select("text").remove();
        d3.select(".service_name").select("text").remove();

        var node_path=""
        var path_name=""
        //create path corrsponding to the selected node
        d.ancestors().slice(0, -1).forEach((val) => 
          node_path=(val.data.name+"/"+node_path));
        path_name=encodeURIComponent(node_path.slice(0, -1))
        console.log(path_name)
        
        
        d3.select("#barchart")
        .select("svg").select("g").selectAll(".bar2").remove()

        nodeUpdate.select('rect.node')
            .attr('r', 10)
            .attr('cursor', 'pointer')
            .style('stroke','black')
          .attr("stroke-width","5px");

          d3.selectAll('rect.node').style("fill", function(d){
            return d.data.fill
          })
        
          d3.select(this).style('stroke',"green")
            .style("fill", "lightgreen")
            .attr("stroke-width","20px");
          
        d3.selectAll("#occ.checkboxes").remove()
        clearTimeout(timeout);
        
        timeout = setTimeout(function() {
          /*
            d._children = d.children;
            
            nodeUpdate.select('rect.node')
            .attr('r', 10)
            .attr('cursor', 'pointer')
            .style('stroke',function(d) {
              return d._children ? "yellow" : "black";
          })
          .attr("stroke-width","5px");*/
          console.log(d.data.name)

          d3.select(".rpc")
          .append("text")
          .text("Remote Procedure Call:")
          .style('font-size','30px')
          .style("font-weight", "bold");

          d3.select(".service_name")
          .append("text")
          .text(d.data.name)
          .style('font-size','30px');

          
          console.log(d.data.name)
          console.log(d.data)
          
          var node_path=""
          var path_name=""
          //create path corrsponding to the selected node
          d.ancestors().slice(0, -1).forEach((val) => 
            node_path=(val.data.name+"/"+node_path));
          
          var param = "url=" + encodeURIComponent(node_path.slice(0, -1));
          var endpoint = "getOcc?" + param;
          //path_name=encodeURIComponent(node_path.slice(0, -1))
          console.log(typeof(path_name))

          d3.json("/getPercDuration?string="+encodeURIComponent(node_path), function(error,perc_occ) {
            if (error) throw error;
            console.log(perc_occ)
            // Set the dimensions of the canvas
      var margin = {top: 20, right: 20, bottom: 30, left: 160},
      width = 550 - margin.left - margin.right,
      height = 450 - margin.top - margin.bottom;

  // Define the x and y scales
  var x = d3.scaleLinear()
      .range([0, width])
      .domain([0, 100]);

  var y = d3.scaleBand()
      .range([height, 0])
      .padding(0.1)
      .domain(d3.keys(perc_occ));

  var xAxis= d3.axisBottom(x)
    
  var yAxis= d3.axisLeft(y)

  // Create the SVG element
  var svg = d3.select("#my_dataviz").append("svg")
      .attr("width", width + margin.left + margin.right+300)
      .attr("height", height + margin.top + margin.bottom)
    .append("g")
      .attr("transform",
            "translate(" + margin.left + "," + margin.top + ")");

  // Add the bars
  svg.selectAll(".bar")
      .data(d3.entries(perc_occ))
    .enter().append("rect")
      .attr("class", "bar")
      .attr("x", 0)
      .attr("height", y.bandwidth())
      .attr("y", function(d) { return y(d.key); })
      .attr("width", function(d) { return x(d.value); })
      .attr("fill", "lightblue")
      .on("click", function(d) {
        // Add the bars
        svg.selectAll(".bar")
          .attr("fill", "lightblue");  
        // Change the fill color of the clicked rectangle to red
        d3.select(this).attr("fill", "red");
        // Retrieve the value of the bar that was clicked
        var value = d.key;
        
        // Retrieve the label of the bar that was clicked
        var label = d.label;
        
        // Do something with the value and label
        console.log("Clicked on bar with value " + value + " and label " + label);

        x=d.key
        double_histByLatency(node_path,e.value,x,checked)
    });

  // Add the x axis
  svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis)
      .selectAll("text")
      .style("font-size", "12px");

  // Add the y axis
  svg.append("g")
      .attr("class", "y axis")
      .call(yAxis)
      .selectAll("text")
      .style("font-size", "16px");

      svg.selectAll(".label")
      .data(d3.entries(perc_occ))
      .enter().append("text")
      .attr("class", "label")
      .attr("x", function(d) { return x(d.value) + 5; }) // position the label to the right of the bar
      .attr("y", function(d) { return y(d.key) + y.bandwidth() / 2; }) // center the label vertically
      .attr("dy", ".35em")
      .text(function(d) { return d.value+'%'; })
      .style("font-size", 20 + "px"); // set the text of the label to the value of the corresponding bar

            
          
    }, 300)
    })
    d3.select('#my_dataviz').select('svg').remove()
        /*    
        tooltip
          .text(d.data.perc_occ+"text added")
          .style('font-size','30px');*/
      })

      d3.selectAll('rect.node').style("fill", function(d){
        return d.data.fill
      })
      
    // Add labels for the nodes
    nodeEnter.append('text')
        .style('fill', '#000000')
        .attr("dy", "-1.5em")
        .attr("x", function(d) {
          return 5;
        })
        .attr("text-anchor", function(d) {
          return "start";
        })
        .text(function(d) { return d.data.name.split("_")[0]; })
        .append("tspan")
        .attr("dy", "1.75em")
        .attr("x", function(d) {
          return 5;
        })
        .text(function(d) { return d.data.name.split("_")[1]; })
        .append("tspan")
        .attr("dy", "1.75em")
        .attr("x", function(d) {
          return 5;
        })
        .text(function(d) { return d.data.subname; })
        .style('fill', '#000000');
    
    nodeEnter.append("g")
    .attr("class", "node")
    .attr("transform", function(d) {
      return "translate(" + source.y0 + "," + source.x0 + ")";
    });
    
    // UPDATE
    var nodeUpdate = nodeEnter.merge(node);
    

    // Transition to the proper position for the node
    nodeUpdate.transition()
      .duration(duration)
      .attr("transform", function(d) { 
          return "translate(" + d.y + "," + d.x + ")";
      });

    // Update the node attributes and style
    nodeUpdate.select('circle.node')
      .attr('r', 10)
      .style("fill", function(d) {
          return d._children ? "lightsteelblue" : "#fff";
      })
      .attr('cursor', 'pointer');


    // Remove any exiting nodes
    var nodeExit = node.exit().transition()
        .duration(duration)
        .attr("transform", function(d) {
            return "translate(" + source.y + "," + source.x + ")";
        })
        .remove();

    // On exit reduce the node circles size to 0
    nodeExit.select('circle')
      .attr('r', 1e-6);

    // On exit reduce the opacity of text labels
    nodeExit.select('text')
      .style('fill-opacity', 1e-6);

    // ****************** links section ***************************

    // Update the links...
    var link = svg.selectAll('path.link')
        .data(links, function(d) { return d.id; });

    // Enter any new links at the parent's previous position.
    var linkEnter = link.enter().insert('path', "g")
        .attr("class", "link")
        .attr('d', function(d){
          var o = {x: source.x0, y: source.y0}
          return diagonal(o, o)
        });

    // UPDATE
    var linkUpdate = linkEnter.merge(link);

    // Transition back to the parent element position
    linkUpdate.transition()
        .duration(duration)
        .attr('d', function(d){ return diagonal(d, d.parent) });

    // Remove any exiting links
    var linkExit = link.exit().transition()
        .duration(duration)
        .attr('d', function(d) {
          var o = {x: source.x, y: source.y}
          return diagonal(o, o)
        })
        .remove();

    // Store the old positions for transition.
    nodes.forEach(function(d){
      d.x0 = d.x;
      d.y0 = d.y;
    });

    // Creates a curved (diagonal) path from parent to the child nodes
    function diagonal(s, d) {

      path = `M ${s.y} ${s.x}
              C ${(s.y + d.y) / 2} ${s.x},
                ${(s.y + d.y) / 2} ${d.x},
                ${d.y} ${d.x}`

      return path
    }
  }})

  //onChange
  }  
  e.onchange = onChange;
  service = onChange();
}

