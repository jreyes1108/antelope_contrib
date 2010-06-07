// Most key events are handled using: http://code.google.com/p/js-hotkeys/ 
PlotSelect = {

    isShiftPressed: false,

    init: function(sta){

        // {{{ Set defaults

        $(document).bind("keydown", "r", PlotSelect.resetPlot);
        $(document).bind("keydown", "left", PlotSelect.shiftPlotViewLeft);
        $(document).bind("keydown", "right", PlotSelect.shiftPlotViewRight);
        $(window).bind("keydown", PlotSelect.toggleShift);
        $(window).bind("keyup", PlotSelect.toggleShift);

        // Create initial plot with max values:
        $("#loading").hide();
        $("#plot_type").buttonset();
        $("button, input:submit, input:checkbox").button();
        $("#nav a").button();
        //if(! $("#wforms").is(':visible') ){
        //    $("#subnavcontent").show('slow');
        //};

        PlotSelect.chan_plot_obj = {};

        // {{{ Define colorschemes

        PlotSelect.colorschemes = {};

        PlotSelect.colorschemes.yb = {
            lineColor : "#FDFF4F",
            bgColor   : "#00029F",
            tickColor : "#0009FF",
            selection : "#FFFFFF"
        };
        PlotSelect.colorschemes.bw = {
            lineColor : "#000000",
            bgColor   : "#DBDBDB",
            tickColor : "#666666",
            selection : "#666666"
        };
        PlotSelect.colorschemes.yg = {
            lineColor : "#FDFF4F",
            bgColor   : "#009F02",
            tickColor : "#00FF09",
            selection : "#FFFFFF"
        };
        PlotSelect.colorschemes.wb = {
            lineColor : "#FFFFFF",
            bgColor   : "#000000",
            tickColor : "#666666",
            selection : "#FFFFFF"
        };
        PlotSelect.colorschemes.yp = {
            lineColor : "#FDFF4F",
            bgColor   : "#660066",
            tickColor : "#993399",
            selection : "#FFFFFF"
        };
        PlotSelect.colorschemes.ob = {
            lineColor : "#FF6600",
            bgColor   : "#000000",
            tickColor : "#666666",
            selection : "#FFFFFF"
        }
        PlotSelect.colorschemes.def = {
            selection : "#FFFFFF"
        }

        // Set defaults for the colorscheme
        if( PlotSelect.canvasLineColor == undefined ) PlotSelect.canvasLineColor = PlotSelect.colorschemes.def.lineColor;
        if( PlotSelect.canvasBgColor == undefined ) PlotSelect.canvasBgColor = PlotSelect.colorschemes.def.bgColor;
        if( PlotSelect.canvasTickColor === undefined ) PlotSelect.canvasTickColor = PlotSelect.colorschemes.def.tickColor;
        if( PlotSelect.canvasSelection === undefined ) PlotSelect.canvasSelection = PlotSelect.colorschemes.def.selection;

        // }}} Define colorschemes

        PlotSelect.wf_opts = {
            colors: [PlotSelect.canvasLineColor], 
            selection: {mode:"x", color:PlotSelect.canvasSelection}, 
            grid: {clickable:true, borderColor:PlotSelect.canvasTickColor, color:PlotSelect.canvasTickColor, tickColor:PlotSelect.canvasTickColor, backgroundColor:PlotSelect.canvasBgColor},
            xaxis: {ticks:5, labelWidth:20, labelHeight:20, mode:"time", timeformat:"%H:%M:%S<br/>%y-%m-%d"},
            yaxis: {ticks:4, labelWidth:25},
            lines: {show:false},
            bars: {show:false} 
        };

        PlotSelect.cov_opts = {
            colors: [PlotSelect.canvasLineColor], 
            selection: {mode:"x", color:PlotSelect.canvasSelection}, 
            grid: {clickable:true, borderColor:PlotSelect.canvasTickColor, color:PlotSelect.canvasTickColor, tickColor:PlotSelect.canvasTickColor, backgroundColor:PlotSelect.canvasBgColor},
            //xaxis: {ticks:3, labelWidth:20, labelHeight:20, mode:"time", timeformat:"%H:%M:%S<br/>%y-%m-%d"},
            xaxis: {ticks:5, labelWidth:20, labelHeight:20, mode:"time", timeformat:"%H:%M:%S<br/>%y-%m-%d"},
            yaxis: {ticks:0,max:2,min:1},
            bars: {show:true, horizontal:true, barWidth:1}
        };



        // {{{ Setup AJAX defaults
        $.ajaxSetup({
            type: 'get',
            dataType: 'json',
            timeout: 120000,
            error:PlotSelect.errorResponse
        });

        // }}} Set defaults

        // {{{ Open the config panel
        $("a#configuration_open_link").click( function() {
            $("#configpanel").slideToggle("slow", function() {
                if( $(this).is(":hidden") ) {
                    $("a#configuration_open_link").html('Show configuration');
                } else {
                    $("a#configuration_open_link").html('Hide configuration');
                }
            });
        });
        // }}} Open the config panel

        // {{{ Canvas resize experiment
        // Not used yet
        // $(window).resize(function(){
        //     $('canvas').css({'width':'100%'});
        // });
        // }}} Canvas resize experiment

        // {{{ Arrival flag CSS
        PlotSelect.arrivalFlagCss = {
            'border':'1px solid #FFF',
            'background-color':'#F00',
            'font-weight':'bold',
            'font-size':'smaller',
            'color':'#FFF',
            'padding':'3px',
            'position':'absolute'
        };
        PlotSelect.arrivalTailCss = {
            'position':'absolute',
            'border':'none',
            'border-left':'1px solid #FFF',
            'margin':'0',
            'padding':'0',
            'width':'1px'
        };
        // }}} Arrival flag CSS

        $('#clear').click( function($e){
            $e.preventDefault();
            $('#subnavcontent').hide('fast');
            $("#station_string").val('.*');
            $("#channel_string").val('.*');
            $("#start_time").val('');
            $("#end_time").val('');
            $('#list').empty();
            $('#subnavcontent').show('slow');
        });
        $('#plot').click( function($e){
            $e.preventDefault();
            sta = $("#station_string").val();
            chan = $("#channel_string").val();
            start = $("#start_time").val();
            end = $("#end_time").val();
            type = $("input[name='type']:checked").attr('id');
            //if ( typeof(sta) != "undefined" ) {
            //    alert('We need value for ...');
            //    return;
            //}
            //alert('Got this values...\n\tsta:'+sta+'\n\tchan:'+chan+'\n\tstart:'+start+'\n\tend:'+end+'\n\ttype:'+type);
            url = "/"+type+'/'+sta+'/'+chan+'/'+start+'/'+end;
            $(location).attr('href',url);
        });

        $('#load_stas').click( function($e){
            $e.preventDefault();
            $('#list').empty();
            $("<ul></ul>").appendTo("#list")
            $.ajax({
                url: "/data/stations",
                success: function(json) {
                    sorted_list = [];
                    $.each(json, function(k,v) {
                        sorted_list.push(v);
                    });
                    sorted_list = sorted_list.sort();
                    $.each(sorted_list, function(i,item){
                        $("#list ul").append('<li><button id="'+item+'" class="add_sta">'+item+'</button></li>');
                    });
                    $('.add_sta').click( function(){
                        name = $(this).text();
                        if ($("#station_string").val() == '.*'){
                            $("#station_string").val(name);
                        } else {
                            old = $("#station_string").val()
                            $("#station_string").val(old+'+'+name);
                        }
                    });
                }
            });
        });

        $('#load_chans').click( function($e){
            $e.preventDefault();
            $('#list').empty();
            $("<ul></ul>").appendTo("#list")
            $.ajax({
                url: "/data/channels",
                success: function(json) {
                    sorted_list = [];
                    $.each(json, function(k,v) {
                        sorted_list.push(v);
                    });
                    sorted_list = sorted_list.sort();
                    $.each(sorted_list, function(i,item){
                        $("#list ul").append('<li><button id="'+item+'" class="add_chan">'+item+'</button></li>');
                    });
                    $('.add_chan').click( function(){
                        name = $(this).text();
                        if ($("#channel_string").val() == '.*'){
                            $("#channel_string").val(name);
                        } else {
                            old = $("#channel_string").val()
                            $("#channel_string").val(old+'+'+name);
                        }
                    });
                }
            });
        });

        $('#load_events').click( function($e){
            $e.preventDefault();
            $('#list').empty();
            $.ajax({
                url: "/data/events",
                success: function(json) {
                    sorted_e_list = [];
                    table_headers = [];

                    jQuery.each(json, function(key,value) {
                        sorted_e_list.push(key);
                        jQuery.each( value, function(sKey,sVal) {
                            if( jQuery.inArray(sKey,table_headers) == -1 ) { table_headers.push(sKey); }
                        });
                    });
                    sorted_e_list = sorted_e_list.sort();
                    table_headers = table_headers.sort();

                    subnavcontent = '<table id="evsTbl" class="evListTable">';

                    subnavcontent += '<thead><tr>\n';
                    subnavcontent += '<th>time</th>\n';
                    jQuery.each(table_headers, function(thi, thv) {
                        if( thv !== 'time' ) {
                            subnavcontent += '<th>'+thv+'</th>\n';
                        }
                    });
                    subnavcontent += '</tr></thead><tbody>\n';

                    jQuery.each(sorted_e_list, function(key, value) {
                        subnavcontent += "<tr>";
                        var time  = json[value]['time'];
                        var tbl_date = new Date(time * 1000);
                        subnavcontent += "<td><a class='add_events'href='#'id='";
                        subnavcontent += json[value]['time'] * 1000 + "'>";
                        subnavcontent += "<span style='display:none;'>";
                        subnavcontent += json[value]['time'] * 1000 + "</span>" + tbl_date + "</a></td>";
                        jQuery.each(table_headers, function(thi, thv) { 
                            if( thv !== 'time' ) {
                                subnavcontent += "<td>" + json[value][thv] + "</td>";
                            }
                        });
                        subnavcontent += "</tr>";
                    });
                    subnavcontent += '</tbody></table>';
                    $("#list").append(subnavcontent);
                    $("#list #evsTbl").tablesorter( {sortList: [[0,0], [1,0]]} );
                    $('.add_events').click( function($e){
                        $e.preventDefault();
                        $('#list').empty();
                        time = $(this).attr("id");
                        if ( typeof(time) != "undefined" ) {
                            time /=  1000;
                        }
                        $("#start_time").val(time);
                    });
                }
            });
        });
        $('#last_1_hr').click( function(){
            $('#start_time').val('last_1_hr');
            $('#end_time').val('');
        });

        $('#last_24_hrs').click( function(){
            $('#start_time').val('last_24_hrs');
            $('#end_time').val('');
        });

        $('#last_week').click( function(){
            $('#start_time').val('last_week');
            $('#end_time').val('');
        });

        $('#last_month').click( function(){
            $('#start_time').val('last_month');
            $('#end_time').val('');
        });

        // }}} Set defaults

    },

    resetPlot: function(evt){

        location.reload(true);

    },

    filterChange: function(evt){

        // {{{ Dynamic filter change data query


        $("select#filter").change( function() {
            PlotSelect.setData();
        });


        // }}} Dynamic filter change data query

    },

    colorschemeChange: function(evt){

        // {{{ Change colorscheme

        $("select#cs").change(function(){

            var cs = $(this).val() ;

            PlotSelect.canvasLineColor = PlotSelect.colorschemes[cs]['lineColor'] ;
            PlotSelect.canvasBgColor   = PlotSelect.colorschemes[cs]['bgColor'];
            PlotSelect.canvasTickColor = PlotSelect.colorschemes[cs]['tickColor'];
            PlotSelect.canvasSelection = PlotSelect.colorschemes[cs]['selection'];

            $("span#csFg").css("background-color",PlotSelect.canvasLineColor);
            $("span#csBg").css("background-color",PlotSelect.canvasBgColor);

            PlotSelect.setData();

        });

        // }}} Change colorscheme

    },

    phaseSelector: function(evt){

        // {{{ Dynamic phase selector

        $("input#phases").change( function() {
            if( $(this).attr('checked') ) { 
                PlotSelect.phases = 'True' ;
            } else { 
                PlotSelect.phases = 'False' ;
            }
            $(".flag").toggle();
            $(".flagTail").toggle();
        });
        // }}} Dynamic phase selector

    },

    typeChange: function(evt){

        // {{{ Dynamic type change data query

        $("form#conftype select#type").change( function() {
            PlotSelect.type = $(this).val();
            PlotSelect.setData();

        });
        // }}} Dynamic type change data query

    },

    tickTranslator:function(tickSizeArr){

        // {{{ tickTranslator

        var increment = tickSizeArr[0], unit = tickSizeArr[1], factor=null;

        if( unit == 'hour' ) {
            factor = 3600 ;
        } else if( unit == 'minute' ) {
            factor = 60 ;
        } else if( unit == 'second' ) {
            factor = 1 ;
        } else {
            factor = 1 ;
        }

        return increment * factor ;

        // }}} tickTranslator

    },

    errorResponse:function(x,e) {

        // {{{ Report Errors to user

        if(x.status==0){

            alert('You are offline!!\n Please Check Your Network.' + '\n\n' + e);

        }else if(x.status==404){

            alert('Requested URL not found.' + '\n\n' + e);

        }else if(x.status==500){

            alert('Internel Server Error.' + '\n\n' + e);

        }else if(e=='parsererror'){

            alert('Error.\nParsing JSON Request failed.' + '\n\n' + e);

        }else if(e=='timeout'){

            alert('Request Time out.' + '\n\n' + e);

        }else {

            //alert('Error.\n'+ x.responseText);
            alert('Error:'+ x + '\n\n' + e);

        }

        // }}}

    },

    shiftPlotViewRight: function(evt) {

        // {{{ Future data

        var delta = PlotSelect.te - PlotSelect.ts ;

        dleta = delta/4;

        PlotSelect.ts += delta;

        PlotSelect.te += delta;

        PlotSelect.setData();

        // }}} Future data

    },

    shiftPlotViewLeft: function(evt) {

        // {{{ Past data

        var delta = PlotSelect.te - PlotSelect.ts ;

        dleta = delta/4;

        PlotSelect.ts -= delta;

        PlotSelect.te -= delta;

        PlotSelect.setData();

        // }}} Past data

    },

    toggleShift: function(evt) {

//{{{
    /*XXX Is there a better way to do this (toggleShift)?
     Currently this pre and post Shift toggling is done
     such that we can detect if Shift is pressed before
     we go into "PlotSelect.handleSelect"  which is an
     event handler that Flot passes plot click position data to.
    */
        PlotSelect.isShiftPressed = evt.shiftKey;
//}}}

    },

    handleSelect: function(evt, pos){

        // {{{ Selection zoom functionality

        if (PlotSelect.isShiftPressed) { /*if the Shift Key is pressed, we zoom out. */
            var delta = 0;

            delta = parseInt( pos.xaxis.from, 10 ) - PlotSelect.ts ;

            PlotSelect.ts -= delta;

            delta = PlotSelect.te - parseInt( pos.xaxis.to, 10 ) ;

            PlotSelect.te += delta;

        }
        else { 

            PlotSelect.ts = parseInt( pos.xaxis.from, 10 ) ;

            PlotSelect.te = parseInt( pos.xaxis.to, 10 ) ;

        }

        PlotSelect.setData();

        // }}} Selection zoom functionality

    },

    setData: function(resp) {

//{{{
        $("#loading").show();

        if ( typeof(resp) != "undefined" ) {
            // PlotSelect is define globally for app
            if (typeof(resp['error']) != "undefined" ) {
                PlotSelect.errorResponse('parsererror',resp['error']);
            }

            if (typeof(resp.type) != "undefined" ) {
                PlotSelect.type = resp['type'];
            }
            if (typeof(resp.stas) != "undefined" ) {
                PlotSelect.stas = resp['sta'];
            }
            if (typeof(resp.chans) != "undefined" ) {
                PlotSelect.chans = resp['chans'];
            }
            if (typeof(resp.ts) != "undefined" ) {
                PlotSelect.ts = resp['ts'] * 1000;
            }
            if (typeof(resp.te) != "undefined" ) {
                PlotSelect.te = resp['te'] * 1000;
            }
            if (typeof(resp.orid) != "undefined" ) {
                PlotSelect.orid = resp['orid'];
            }
            if (typeof(resp.phases) != "undefined" ) {
                PlotSelect.phases = resp['phases'];
            }
        }

        // Hide Controls
        $('#subnavcontent').hide('fast');
        // Show plots
        $("#wforms").show();
        $("#interact").show();
        $("#tools").show();

        if (PlotSelect.type == 'coverage') {
            var url = '/data/coverage'

            if (typeof(PlotSelect.stas) != "undefined" ) {
                url += '/' + PlotSelect.stas.join("+");
            }
            if (typeof(PlotSelect.chans) != "undefined" ) {
                url += '/' + PlotSelect.chans.join("+");
            }
            if (typeof(PlotSelect.ts) != "undefined" ) {
                url += '/' + PlotSelect.ts / 1000;
            }
            if (typeof(PlotSelect.te) != "undefined" ) {
                url += '/' + PlotSelect.te / 1000;
            }

            $.ajax({ 
                url:url, 
                success: function(data){
                    PlotSelect.setCoverage(data); 
                }
            });
        } else {

            $.each(PlotSelect.stas.sort(), function(sta_iterator,mysta){

                $.each(PlotSelect.chans.sort(), function(chan_iterator,mychan){

                    PlotSelect.plotData(mysta,mychan);

                });

            });
        }

        $("#loading").fadeOut();
//}}}

    },

    setCoverage: function(data) {

//{{{
        var NameCss = { color:'black', 'font-size':'20px', position:'absolute', left:'10%', top:'25%'};
        var ErrorCss = { color:'red', 'ont-size':'20px', position:'absolute', left:'30%', top:'25%'};

        PlotSelect.ts = data['time_start'] * 1000;
        PlotSelect.te = data['time_end'] * 1000;
        PlotSelect.stas = data['sta'];
        PlotSelect.chans = data['chan'];

        PlotSelect.cov_opts['xaxis']['min'] = PlotSelect.ts;
        PlotSelect.cov_opts['xaxis']['max'] = PlotSelect.te;

//{{{
        $.each(data.sta, function(sta_iterator,mysta){

            $.each(data.chan, function(chan_iterator,mychan){

                if (typeof(data[mysta]) == "undefined" ) { 
                } else if (typeof(data[mysta][mychan]) == "undefined" ) { 
                } else {
                    var name = mysta + '_' + mychan ; // Create the STA_CHAN data arrays from other response items
                    var wrapper = $("<div>").attr("id", name+"_wrapper").attr("class","wrapper_cov");
                    var plt = $("<div>").attr("id", name+"_plot" ).attr("class", "plot_cov");

                    if ($("#"+name+"_plot").length == 0) {
                        $("#wforms").append(wrapper);
                        wrapper.append(plt);
                        plt.bind("plotselected", PlotSelect.handleSelect);
                    }

                    plt = $("#"+name+"_plot");

                    var flot_data = [];

//{{{
                    //  Coverage plot

                    if (typeof(data[mysta][mychan]['data']) == "undefined" ) { 

                        var plot = $.plot(plt, [], PlotSelect.cov_opts);

                        var arrDiv = $("<div>").css(ErrorCss).append('No data in time segment: ('+PlotSelect.ts+','+PlotSelect.te+').');

                        plt.append(arrDiv);

                    } else {

                        $.each( data[mysta][mychan]['data'], function(i,arr) {

                            var start_time = parseFloat(arr[0],10) *1000;
                            var end_time   = parseFloat(arr[1],10) *1000;
                            flot_data.push([start_time,1,end_time]);

                        });

                        var plot = $.plot(plt,[ flot_data ], PlotSelect.cov_opts );
                    }
//}}}
                    var arrDiv = $("<div>").css(NameCss).append(name);

                    plt.append(arrDiv);

                    PlotSelect.chan_plot_obj[name] = plot;
                } 

            });

        });
//}}}
//}}}

    },

    setEventData: function(resp){

//{{{
        //$('#subnav #event').empty();
        $('#list').empty();

        //  Plot event table

        var event_metadata = '<table id="eventTable">';
        event_metadata += "<tr><th>Magnitude</th><td>"+resp['magnitude']+" "+resp['mtype']+"</td>";
        event_metadata += "<th>Date-Time</th><td>"+resp['time']+"</td></tr>";
        event_metadata += "<tr><th>Location</th><td>"+resp['lat']+"&deg;N, "+resp['lon']+"&deg;E</td>";
        event_metadata += "<th>Depth</th><td>"+resp['depth']+"km</td></tr>";
        event_metadata += "<tr><th>Author</th><td>"+resp['auth']+"</td><th>nass</th><td>"+resp['nass']+"</td></tr>";
        event_metadata += "</table>";

        $('#list').append(event_metadata);
//}}}

    },

    plotData: function(sta,chan){

//{{{
        //  Define graph defaults

        var NameCss = { color:'black', 'font-size':'20px', position:'absolute', left:'10%', top:'5%'};
        var ErrorCss = { color:'red', 'ont-size':'20px', position:'absolute', left:'50%', top:'50%'};


        PlotSelect.wf_opts.xaxis.min = PlotSelect.ts;
        PlotSelect.wf_opts.xaxis.max = PlotSelect.te;

        var flot_data = [];

        var url = '/data/wf'

        if (typeof(PlotSelect.stas) == "undefined" ) {
            alert("ERROR: we need station!");
            return;
        }
        url += '/' + PlotSelect.stas.join("+");

        if (typeof(PlotSelect.chans) == "undefined" ) {
            alert("ERROR: we need channels!");
            return;
        }
        url += '/' + PlotSelect.chans.join("+");

        if (typeof(PlotSelect.ts) == "undefined" ) {
            alert("ERROR: we need start-time!");
            return;
        }
        url += '/' + PlotSelect.ts / 1000;

        if (typeof(PlotSelect.te) != "undefined" ) {
            url += '/' + PlotSelect.te / 1000;
        }
        $.ajax({
            url:url,
            success: function(data) {
//{{{
                if (typeof(data[sta][chan]) == "undefined" ) { 
                    return;
                }

                var name = sta + '_' + chan ; // Create the STA_CHAN data arrays from other response items
                var wrapper = $("<div>").attr("id", name+"_wrapper").attr("class","wrapper");
                var plt = $("<div>").attr("id", name+"_plot" ).attr("class", "plot");

                if ($("#"+name+"_plot").length == 0) {
                    $("#wforms").append(wrapper);
                    wrapper.append(plt);
                    plt.bind("plotselected", PlotSelect.handleSelect);
                }

                plt = $("#"+name+"_plot");



                if (typeof(data[sta][chan]['data']) == "undefined" ) { 
//{{{
                    var plot = $.plot(plt, [], PlotSelect.wf_opts);

                    var arrDiv = $("<div>").css(ErrorCss).append('No data in time segment: ('+PlotSelect.ts+','+PlotSelect.te+').');

                    plt.append(arrDiv);
//}}}
                } else {
//{{{
                    if( data[sta][chan]['format'] == 'bins' ) {

                        for ( var i=0, len=data[sta][chan]['data'].length; i<len; ++i ){
                            temp_data = data[sta][chan]['data'][i];
                            flot_data[i] =  [temp_data[0]*1000,temp_data[2],temp_data[1]];
                        }
                        PlotSelect.wf_opts['bars'] = {show:true,barWidth:0,align:'center'};
                        PlotSelect.wf_opts['lines'] = {show:false};

                    } else {

                        for ( var i=0, len=data[sta][chan]['data'].length; i<len; ++i ){
                            temp_data = data[sta][chan]['data'][i];
                            flot_data[i] =  [temp_data[0]*1000,temp_data[1]];
                        }
                        PlotSelect.wf_opts['lines'] = {show:true,lineWidth:2,shadowSize:4};
                        PlotSelect.wf_opts['bars'] = {show:false};

                    }

                    var plot = $.plot(plt, [flot_data], PlotSelect.wf_opts);
//}}}
                }

                PlotSelect.chan_plot_obj[name] = plot;

                var arrDiv = $("<div>").css(NameCss).append(name);
                plt.append(arrDiv);
//}}}
            },
        });
//}}}

    }

};
