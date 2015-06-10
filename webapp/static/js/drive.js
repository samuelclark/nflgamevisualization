/*
Samuel Clark
February 2014
NFL D3 Viz
*/

var render_drive= function (play_config, field_config) {
    // Hits json_url flask endpoint loads the data using d3.json
      drive_chart(field_config);
      play_table(play_config);

};

 var get_x_pos = function get_x_pos (offset, yards_gained, scale) {
        // returns x value for rect which is equivelant of the yardline the play is from
        // if it is a sack or penalty than move x and width by <yards_gained>
        var pivot = 50;
        if (yards_gained < 0) {
            return scale(pivot + offset + yards_gained);
        }
        else {
            return scale(pivot  + offset);
        }
    };

var get_width = function get_width (yards_gained, scale) {
        // calculates width of rect --> yards gained in the play
       if (yards_gained === 0) {
        // in complete pass --> we still want to show a bar
                    return scale(0.5);
        }
        return scale(Math.abs(yards_gained));
};


var get_svg = function get_svg(config) {
    var margin = config.margin;
    var existing = d3.selectAll(config.container +" svg")[0];
    if (existing.length) {
        return existing[0];
    }
    var svg = d3.select(config.container).append("svg")
            .attr("height", config.height+margin.top + margin.bottom)
            .attr("width", config.width + margin.right +margin.left)
            .attr("class", config.container)
            .append("g")
                .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
    return svg;
};
var play_table = function(config){
    /* 
        -renders a sequential table of each play in the drive
        - columns = play_keys
        - config contains play and drive data, margin + container information
    */
    var margin = config.margin;
    var height = config.height;
    var width = config.width;
    var drive = config.data.drive;
    var plays = config.data.plays;
    if (!plays[0].down) {
        plays = plays.slice(1);
    }
    var svg = config.svg;
    // create headers
    var play_keys = ['play', 'down',  'ydstogo', 'yrdln','type','yards_gained','qtr', 'time'];//, 'desc'];
    var thead = d3.select("thead").selectAll("th")
    .data(play_keys)
    .enter().append("th").text(function(d){return d;});
    var clean_plays = [];
    for (var i = 0, len = plays.length; i < len; i++) {
        var play = plays[i];
        var info = {};
        for (var j = 0, klen = play_keys.length; j < klen; j++){
            var play_key = play_keys[j];
            if (play_key == 'play') {
                info[play_key] = i;
            }
            else if (play_key!= 'yards_gained' && play_key!= 'type' && play_key!= 'playid'){
            info[play_key] = play.data[play_key];
            }
            else {
                info[play_key] = play[play_key];
            }
        }
        clean_plays.push(info);
    }
    // clear canvas
    d3.select("tbody").selectAll("*").remove();
    // create rows
    var tr = d3.select("tbody").selectAll("tr")
        .data(clean_plays).enter().append("tr")
        .attr("class", function(d) {return d.type+ " a"+d.time.replace(":",'');});
    // fill cells with data
    var td = tr.selectAll("td")
            .data(function(d){return d3.values(d);})
             .enter().append("td")
        .text(function(d, i) {return d;});
};



var drive_chart = function(config) {
    // returns a football-field sized svg  as child container
    var p_height = 20;
    var xoffset = 10; // for aligning x and y axis
    var yoffset = 20;
    var text_buffer = 10;
    var height = config.height;
    var width = config.width;
    var margin = config.margin;
    console.log(config.data);
    var plays = config.data.plays;
    if (!plays[0].down) {
        plays = plays.slice(1);
    }
    var drive = config.data.drive;
    var driveinfo = d3.select("#driveinfo").html(drive);
    console.log(drive);

    console.log(plays);
    var svg = config.svg;
    svg.selectAll("*").remove();

    // lots of setup ...

    var x_home_scale = d3.scale.linear()
                    .range([0, width/2])
                    .domain([0,50]); //currently not including endzone
    var x_away_scale = d3.scale.linear()
                    .range([width/2, 0])
                    .domain([0,50]);

    var x_play_scale = d3.scale.linear()
                        .range([0,width])
                        .domain([0,100]);

    var y_scale = d3.scale.linear()
                    .range([yoffset, height-yoffset])
                    .domain([plays.length, 1]);

    var x_bot_away = d3.svg.axis()
                    .scale(x_away_scale)
                    .orient("bottom")
                    .ticks(5);

    var x_bot_home = d3.svg.axis()
                    .scale(x_home_scale)
                    .orient("bottom")
                    .ticks(5);

 

    var x_top_home = d3.svg.axis()
                    .scale(x_home_scale)
                    .orient("top")
                    .ticks(5);

    var x_top_away = d3.svg.axis()
                        .scale(x_away_scale)
                        .orient("top")
                        .ticks(5);



    var y_axis_left = d3.svg.axis()
                        .scale(y_scale)
                        .orient("left")
                        .ticks(plays.length);


 svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(" + width/2 + ",0)")//0 +")")
        .call(x_top_away);

    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0 ,0)")
        .call(x_top_home);
    svg.append("g")
        .attr("class", "y axis")
        .call(y_axis_left);

    // add half field line
    svg.append("svg:line")
    .attr("x1", x_home_scale(50))
    .attr("x2", x_home_scale(50))
    .attr("y1", 0)
    .attr("y2", height)
    .style("stroke-dasharray", ("3, 3"))
    .style("stroke", "black");

    // add labels first so plays are rendered on top
    var labels = svg.selectAll("play_labels")
                    .data(plays)
                    .enter()
                    .append("text")
                    .attr("x", function(d) {return get_x_pos(d.yardline.offset, d.yards_gained, x_play_scale) + get_width(d.yards_gained, x_play_scale) + 3;})
                    .attr("y", function(d, i) {return y_scale(i + 1) + 14;})
                    .style("text-align", "middle");
        labels.transition().delay(function(d,i) {return 500*plays.length + i *100;})
                    .text(function(d) {
                        if (d.type == "timeout") {
                            return "timeout";
                        }
                        return d.yards_gained;});//return d.type + "\t" + ;});

    // add plays
    var play_rects = svg.selectAll("plays")
        .data(plays);
    play_rects
        .enter()
        .append("rect")
        .attr("x", function(d) { return get_x_pos(d.yardline.offset, d.yards_gained, x_play_scale);})
        .attr("y", function(d, i) {return y_scale(i + 1);})
        .attr("height", function(d) {return p_height;})
        .attr("width", function(d) { return 0;})//return get_width(d.yards_gained, x_play_scale);})
        .attr("class", function(d) { return d.type + " p" + d.playid;});
    play_rects
        .on("mouseover", function(d, i) {
            var trow = d3.selectAll("tr")[0][i];
            trow.className+= " highlight";
            render_play_info({"container": "#playdetail"}, d);
        })
        .on("mouseout", function(d, i) {
            var trow = d3.selectAll("tr")[0][i];
            var tmp = trow.className.slice(0,-" highlight".length);
            trow.className = tmp;
            var detail_container = d3.selectAll("#playdetail");
            detail_container[0][0].innerHTML = "";

        });
    //  stagger play transitions in sequential order...
    play_rects.transition().duration(1000)
                .delay(function(d,i) {return i * 500;})
                .attr("width", function(d) { return get_width(d.yards_gained, x_play_scale);});
};

var render_play_info = function(config, play) {
    /*
        Sets html of playinfo div to the description of the selected play
        - should add a feature that enables this when a table row is selected as well
    */
    var detail_container = d3.selectAll(config.container).html(play.desc);

};

