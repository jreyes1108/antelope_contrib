// Most key events are handled using: http://code.google.com/p/js-hotkeys/ 
PlotSelect = {

    isShiftPressed: false,

    init: function(sta){

        // {{{ Set defaults
        $("#loading").show();

        // To store plot objects
        PlotSelect.chan_plot_obj = {};

        // Set COOKIE global options
        //PlotSelect.COOKIE_OPTS = { path: '/dbwfserver', expires: 99};
        PlotSelect.COOKIE_OPTS = { 
            path: '/', 
            expiresAt: 99
        };

        // Get the values and update buttons
        PlotSelect.getCookie();

        // Apply all JQUERY UI functions.
        $("#plot_type").buttonset();
        $("button, input:submit, input:checkbox").button();
        $("#nav a").button();
        $("#cs, #filter").selectmenu({style:'dropdown',menuWidth:200});

        // get tuple for min and max dates in database
        var minTime = '0';
        var maxTime = 'Today';

        var dates = $(".datepicker").datepicker({showOn: 'button',
                                buttonImage: 'static/images/calendar.gif',
                                buttonImageOnly: true,
                                dateFormat: '@',
                                minDate: minTime,
                                maxDate: maxTime,
                                onSelect: function(dateText, inst) {
                                    if (this.id == "end_time"){
                                        var old = dates.not(this).val();
                                        dates.not(this).datepicker("option", 'maxDate', dateText );
                                        dates.not(this).val( old );
                                        $("#end_time").val( (dateText / 1000) + 86399 );
                                    } else {
                                        var old = dates.not(this).val();
                                        dates.not(this).datepicker("option", "minDate", dateText);
                                        dates.not(this).val( old );
                                        $("#start_time").val( dateText / 1000 );
                                    }
                                }
                            });

        //
        // Set the max and min on datepicker to 
        // database max and min times on wfdisc
        //
        $.ajax({
            url: "/data/times",
            success: function(json) {
                if (json) {
                    dates.datepicker("option", 'minDate', String(json['start']*1000));
                    dates.datepicker("option", 'maxDate', String(json['end']*1000));
                }
            }
        });



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
            //bgColor   : "#DBDBDB",
            bgColor   : { colors: ["#eee", "#999"] },
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
            bgColor   : { colors: ["#000", "#999"] },
            //bgColor   : "#000000",
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
            bgColor   : "#eee"
            //bgColor   : { colors: ["#fff", "#eee"] }
        }

        // }}} Define colorschemes

        // Bind actions to elements
        PlotSelect.configChange();

        // Define global variables depending 
        // on the configuration. 
        PlotSelect.plotVarSet();

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
                    $("a#configuration_open_link").html('Show Help');
                } else {
                    $("a#configuration_open_link").html('Hide Help');
                }
            });
        });
        // }}} Open the config panel

        // {{{ Canvas resize
        $(window).resize(function(){

            PlotSelect.setData();

        });
        // }}} Canvas resize experiment


        $('#clear').click( function($e){
//{{{
            $e.preventDefault();
            $('#subnavcontent').hide('fast');
            $("#station_string").val('.*');
            $("#channel_string").val('.*');
            $("#start_time").val('');
            $("#end_time").val('');
            $('#list').empty();
            $('#subnavcontent').show('slow');
//}}}
        });

        $('#plot').click( function($e){
//{{{
            $e.preventDefault();
            sta = $("#station_string").val();
            chan = $("#channel_string").val();
            start = $("#start_time").val();
            end = $("#end_time").val();

            // Save sattings
            PlotSelect.setCookie();

            url = '/wf/'+sta+'/'+chan+'/'+start+'/'+end;
            $(location).attr('href',url);
//}}}
        });

        $('#load_stas').click( function($e){
//{{{
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
//}}}
        });

        $('#load_chans').click( function($e){
//{{{
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
//}}}
        });

        $('#load_events').click( function($e){
//{{{
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
//}}}
        });

        $("#loading").hide();

        // }}} Set defaults

    },

    getCookie: function(){

    //{{{ Get cookie values
        //
        // Look for cookie values and update elements
        //
        //alert('Value of type:'+ $.cookie('dbwfserver_type'));
        //$.each($.cookies.get('dbwfserver_filter'), function(e) {
        //    alert('Value of type:'+e);
        //});

        if ($.cookie('dbwfserver_phases') ==  'false'){
            $('input[name=phases]').attr('checked', false);
        }
        if ($.cookie('dbwfserver_phases') ==  'true'){
            $('input[name=phases]').attr('checked', true);
        }
        if ($.cookie('dbwfserver_type') != null){
            $('#plot_type input').val([$.cookie('dbwfserver_type')]);
        }
        if ($.cookie('dbwfserver_color') != null){
            $('#cs').val($.cookie('dbwfserver_color'));
        }
        if ($.cookie('dbwfserver_filter') != null){
            $('#filter').val($.cookie('dbwfserver_filter'));
        }
        //
        // We have some problems with multiple 
        // databases on different ports.
        //
        //if ($.cookie('dbwfserver_stime') != null){
        //    $('#start_time').val($.cookie('dbwfserver_stime'));
        //}
        //if ($.cookie('dbwfserver_etime') != null){
        //    $('#end_time').val($.cookie('dbwfserver_etime'));
        //}
        //if ($.cookie('dbwfserver_sta') != null){
        //    $('#station_string').val($.cookie('dbwfserver_sta'));
        //}
        //if ($.cookie('dbwfserver_chan') != null){
        //    $('#channel_string').val($.cookie('dbwfserver_chan'));
        //}
    //}}} Get cookie values

    },
    setCookie: function(){

    //{{{ Set cookie

        $.cookie('dbwfserver_type', $("input[name='wf_type']:checked").val(), PlotSelect.COOKIE_OPTS);

        $.cookie('dbwfserver_color', $("#cs").val(), PlotSelect.COOKIE_OPTS);

        $.cookie('dbwfserver_filter', $("#filter").val(), PlotSelect.COOKIE_OPTS);

        $.cookie('dbwfserver_phases', $("#phases").is(':checked'), PlotSelect.COOKIE_OPTS);

        $.cookie('dbwfserver_stime', $("#start_time").val(), PlotSelect.COOKIE_OPTS);

        $.cookie('dbwfserver_etime', $("#end_time").val(), PlotSelect.COOKIE_OPTS);

        $.cookie('dbwfserver_sta', $("#station_string").val(), PlotSelect.COOKIE_OPTS);

        $.cookie('dbwfserver_chan', $("#channel_string").val(), PlotSelect.COOKIE_OPTS);

    //}}} Set cookie

    },

    configChange: function(){

    //{{{ Bind actions to elements

        // {{{ Dynamic phase selector

        $("#phases").change( function() {
            if( $(this).attr('checked') ) { 
                PlotSelect.phases = 'True' ;
            } else { 
                PlotSelect.phases = 'False' ;
            }
            if ( PlotSelect.phases == 'True' ) { 

                $(".flag").show();
                $(".flagTail").show();

            } else { 

                $(".flag").hide();
                $(".flagTail").hide();

            }

            PlotSelect.setCookie();

        });
        // }}} Dynamic phase selector

        // {{{ Change controls

        $("select#cs, select#filter, #plot_type").change(function(){

            PlotSelect.plotVarSet();
            PlotSelect.setCookie();
            if (! $("#subnavcontent").is(":visible") ) {
                PlotSelect.setData();
            }

        });

        // }}} Change controls

    //}}} Bind actions to elements

    },

    keyBinds: function(){

    // {{{ Set bindings for keys


        $(document).unbind('keyup');
        $(document).unbind('keydown');

        $(document).keydown(function(e) {
            if (e.keyCode == '38') {
                // Up key
                e.preventDefault();
            } else if (e.keyCode == '40') {
                // Down key
                e.preventDefault();
            } else if (e.keyCode == '37') {
                // Left key
                e.preventDefault();
            } else if (e.keyCode == '39') {
                // Right key
                e.preventDefault();
            } else if (e.keyCode == '82') {
                // r for reset plot
                e.preventDefault();
            } else if(e.which == 16) {
                // Shift key
                PlotSelect.isShiftPressed = true;
            }
        });

        $(document).keyup(function(e) {
            if (e.keyCode == '38') {
                // Up key
                e.preventDefault();
                PlotSelect.shiftPlot('I');
            } else if (e.keyCode == '40') {
                // Down key
                e.preventDefault();
                PlotSelect.shiftPlot('O');
            } else if (e.keyCode == '37') {
                // Left key
                e.preventDefault();
                PlotSelect.shiftPlot('L');
            } else if (e.keyCode == '39') {
                // Right key
                e.preventDefault();
                PlotSelect.shiftPlot('R');
            } else if (e.keyCode == '82') {
                // r for reset plot
                e.preventDefault();
                location.reload(true);
            } else if(e.which == 16) {
                // Shift key
                PlotSelect.isShiftPressed = false;
            }
        });

    // }}} Set bindings for keys

    },

    plotVarSet: function(){

    // {{{ Set vars for plots

        //{{{ Set color scheme
        // Set the color scheme
        var cs = $("select#cs").val();

        if (cs == undefined) {
            cs = 'def';
        }

        // Set global vars for color
        PlotSelect.canvasLineColor = PlotSelect.colorschemes[cs]['lineColor'] ;
        PlotSelect.canvasBgColor   = PlotSelect.colorschemes[cs]['bgColor'];
        PlotSelect.canvasTickColor = PlotSelect.colorschemes[cs]['tickColor'];
        PlotSelect.canvasSelection = PlotSelect.colorschemes[cs]['selection'];
        //}}} Set color scheme

        //{{{ Flot options
        // Set coverage defaults
        PlotSelect.cov = {
            colors: [PlotSelect.canvasLineColor], 
            selection: {mode:"x", color:PlotSelect.canvasSelection}, 
            grid: {clickable:true, borderColor:PlotSelect.canvasTickColor, color:PlotSelect.canvasTickColor, tickColor:PlotSelect.canvasTickColor, backgroundColor:PlotSelect.canvasBgColor},
            xaxis: {ticks:5, labelHeight:20, mode:"time", timeformat:"%H:%M:%S<br/>%y-%m-%d"},
            yaxis: {ticks:0,min:1,max:2},
            bars: {show:true,horizontal:true,barWidth:1,fill:true,fillColor:PlotSelect.canvasLineColor}
        };

        // Set waveforms defaults lines
        PlotSelect.wf_lines = {
            colors: [PlotSelect.canvasLineColor], 
            selection: {mode:"x", color:PlotSelect.canvasSelection}, 
            grid: {clickable:true, borderColor:PlotSelect.canvasTickColor, color:PlotSelect.canvasTickColor, tickColor:PlotSelect.canvasTickColor, backgroundColor:PlotSelect.canvasBgColor},
            xaxis: {ticks:5, labelWidth:20, labelHeight:20, mode:"time", timeformat:"%H:%M:%S<br/>%y-%m-%d"},
            yaxis: {ticks:4,labelWidth:30},
            lines: {show:true,lineWidth:2,shadowSize:4},
        };

        // Set waveforms defaults bins
        PlotSelect.wf_bins = {
            colors: [PlotSelect.canvasLineColor], 
            selection: {mode:"x", color:PlotSelect.canvasSelection}, 
            grid: {clickable:true, borderColor:PlotSelect.canvasTickColor, color:PlotSelect.canvasTickColor, tickColor:PlotSelect.canvasTickColor, backgroundColor:PlotSelect.canvasBgColor},
            xaxis: {ticks:5, labelWidth:20, labelHeight:20, mode:"time", timeformat:"%H:%M:%S<br/>%y-%m-%d"},
            yaxis: {ticks:4,labelWidth:40},
            bars: {show:true,barWidth:0,align:'center'},
        };

        // For the text on the screen.
        PlotSelect.NameCss = { color:PlotSelect.canvasLineColor, 'font-size':'20px', position:'absolute', left:'10%', top:'15%'};

        //}}} Flot options

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

    // }}} Set vars for plots

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

    shiftPlot: function(evt) {

        // {{{ Future data

        var delta = PlotSelect.te - PlotSelect.ts ;

        delta /= 4;

        if (evt == 'L') { 
            PlotSelect.ts -= delta;
            PlotSelect.te -= delta;
        } else if (evt == 'R') {
            PlotSelect.ts += delta;
            PlotSelect.te += delta;
        } else if (evt == 'I') {
            PlotSelect.ts += delta;
            PlotSelect.te -= delta;
        } else if (evt == 'O') {
            PlotSelect.ts -= delta;
            PlotSelect.te += delta;
        }

        PlotSelect.setData();

        // }}} Future data

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

    setEventData: function(resp){

//{{{
        //$('#subnav #event').empty();
        $('#event_meta').empty();

        //  Plot event table

        var event_metadata = '<table id="eventTable">';
        event_metadata += "<tr><th>Magnitude</th><td>"+resp['magnitude']+" "+resp['mtype']+"</td>";
        event_metadata += "<th>Date-Time</th><td>"+resp['time']+"</td></tr>";
        event_metadata += "<tr><th>Location</th><td>"+resp['lat']+"&deg;N, "+resp['lon']+"&deg;E</td>";
        event_metadata += "<th>Depth</th><td>"+resp['depth']+"km</td></tr>";
        event_metadata += "<tr><th>Author</th><td>"+resp['auth']+"</td><th>nass</th><td>"+resp['nass']+"</td></tr>";
        event_metadata += "</table>";

        $('#event_meta').append(event_metadata);
//}}}

    },

    setData: function(resp) {

//{{{
        $("#loading").show();

        //
        // Get type
        //
        PlotSelect.type = $("input[name='wf_type']:checked").val();

        if (typeof(PlotSelect.type) == "undefined") {
            alert('Problems detecting "type" for plot. Select (waveforms or coverage).');
        }

        // 
        // If resp defined... update globals
        //
        if ( typeof(resp) != "undefined" ) {
//{{{

            // PlotSelect is define globally for app
            if (typeof(resp['error']) != "undefined" ) {
                PlotSelect.errorResponse('parsererror',resp['error']);
            }

            if (typeof(resp.sta) != "undefined" ) {
                PlotSelect.sta = resp['sta'];
                //alert('PlotSelect:{sta:'+PlotSelect.sta+'}');
            }
            if (typeof(resp.chan) != "undefined" ) {
                PlotSelect.chan = resp['chan'];
                //alert('PlotSelect:{chan:'+PlotSelect.chan+'}');
            }
            if (typeof(resp.time_start) != "undefined" ) {
                PlotSelect.ts = resp['time_start'] * 1000;
                //alert('PlotSelect:{ts:'+PlotSelect.ts+'}');
            }
            if (typeof(resp.time_end) != "undefined" ) {
                PlotSelect.te = resp['time_end'] * 1000;
                //alert('PlotSelect:{te:'+PlotSelect.te+'}');
            }
            if (typeof(resp.orid) != "undefined" ) {
                PlotSelect.orid = resp['orid'];
                //alert('PlotSelect:{orid:'+PlotSelect.orid+'}');
            }
            if (typeof(resp.phases) != "undefined" ) {
                PlotSelect.phases = resp['phases'];
                //alert('PlotSelect:{phases:'+PlotSelect.phases+'}');
            }
//}}}
        }

        // Hide Controls
        $('#subnavcontent').hide('fast');
        // Show plots
        $("#wforms").show('fast');
        $("#tools").show('fast');

        if (PlotSelect.type == 'coverage') {

            PlotSelect.keyBinds();

            //
            // Build URL for query
            //
//{{{
            var url = '/data/coverage'

            if (typeof(PlotSelect.sta) != "undefined" ) {
                url += '/' + PlotSelect.sta.join("+");
            } else { 
                url += '/.*';
            }

            if (typeof(PlotSelect.chan) != "undefined" ) {
                url += '/' + PlotSelect.chan.join("+");
            } else { 
                url += '/.*';
            }

            if (typeof(PlotSelect.ts) != "undefined" ) {
                url += '/' + PlotSelect.ts / 1000;
            } 

            if (typeof(PlotSelect.te) != "undefined" ) {
                url += '/' + PlotSelect.te / 1000;
            }
//}}}

            // Just 1 ajax call for all coverage data 
            // since all comes from the wfdisc table.
            $.ajax({ 
                url:url, 
                success: function(data){
                    //
                    // Update Globals
                    //
//{{{
                    PlotSelect.sta = data['sta'];
                    PlotSelect.chan = data['chan'];

                    // Coverage could be called without times... need update
                    PlotSelect.ts = data['time_start'] * 1000;
                    PlotSelect.te = data['time_end'] * 1000;

                    // Set max and min for plots
                    PlotSelect.cov.xaxis.min = PlotSelect.ts;
                    PlotSelect.cov.xaxis.max = PlotSelect.te;
//}}}

                    $.each(data.sta.sort(), function(sta_iterator,mysta){

                        $.each(data.chan.sort(), function(chan_iterator,mychan){

                            var wpr = mysta + '_' + mychan + '_wrapper' ;

                            if ( $("#"+wpr).length == 0 ){
                                $("#wforms").append( $("<div>").attr("id",wpr ).attr("class","wrapper") );
                                $("#"+wpr).width( $(window).width() );
                            }

                            // Verify if sta:chan combination is valid...
                            if (typeof(data[mysta][mychan]) != "undefined" ) { 
                                PlotSelect.plotData(mysta,mychan,data[mysta][mychan]);
                            } else { 
                                //alert('Not valid sta:chan combination.('+mysta+','+mychan+')');
                            }

                        });

                    });
                }
            });
        } else if (PlotSelect.type == 'waveform'){

            PlotSelect.keyBinds();

            $.each(PlotSelect.sta.sort(), function(sta_iterator,mysta){

                $.each(PlotSelect.chan.sort(), function(chan_iterator,mychan){

                    var url = '/data/wf'

                    url += '/' + mysta;

                    url += '/' + mychan;

                    if (typeof(PlotSelect.ts) != "undefined" ) {

                        url += '/' + PlotSelect.ts / 1000;

                        // check end_time only if we have start time
                        if (typeof(PlotSelect.te) != "undefined" ) {
                            url += '/' + PlotSelect.te / 1000;

                            // check filter only if we have end time
                            if ( $("#filter").val() != "None" ) {
                                url += '/' + $("#filter").val();
                            }
                        }
                    }

                    var wpr = mysta + '_' + mychan + '_wrapper' ;

                    if ( $("#"+wpr).length == 0 ){
                        $("#wforms").append( $("<div>").attr("id",wpr ).attr("class","wrapper") );
                         $("#"+wpr).width( $(window).width() );
                    }

                    $.ajax({
                        url:url,
                        success: function(data) {
                            if (typeof(data[mysta][mychan]) != "undefined" ) { 
                                PlotSelect.plotData(mysta,mychan,data[mysta][mychan]);
                            } else { 
                                //alert('Not valid sta:chan combination.('+mysta+','+mychan+')');
                            }
                        },
                    });

                });

            });

            if ($("#phases").is(':checked') == true) { 
                if (typeof(PlotSelect.ts) != "undefined" ) {
                    // check end_time only if we have start time
                    if (typeof(PlotSelect.te) != "undefined" ) {
                        // call only if we have start and end times
                        PlotSelect.setPhases(PlotSelect.ts/1000,PlotSelect.te/1000);
                    }
                }
            }

        } else {

            // Show plots
            $("#wforms").hide('fast');
            $("#tools").hide('fast');
            // Hide Controls
            $('#subnavcontent').show('slow');

        }
//        }

        $("#loading").fadeOut();
//}}}

    },

    plotData: function(sta,chan,data){
//{{{

        var flot_data = [];

        var name = sta + '_' + chan ; // Create the STA_CHAN data arrays from other response items
        var wpr = name+"_wrapper";
        var plt = name+"_plot";
        var wrapper = $("<div>").attr("id",wpr ).attr("class","wrapper");
        var plot = $("<div>").attr("id", plt );


        if ( $("#"+plt).length == 0 ){

            $("#"+wpr).append(plot);

            $("#"+plt).bind("plotselected", PlotSelect.handleSelect);

        }

        if ( typeof(data['data']) == "undefined" ) { 
        //{{{
            $("#"+plt).attr("class", "plot_cov");

            var canvas = $.plot($("#"+plt),[], PlotSelect.cov);

            var arrDiv = $("<div>").css(PlotSelect.NameCss);

            arrDiv.css({ color:'red', left:'30%', top:'5%'});

            arrDiv.append('No data in time segment: ('+PlotSelect.ts+','+PlotSelect.te+').');

            $("#"+plt).append(arrDiv);
        //}}}
        } else {
        //{{{
            if ( typeof(data['format']) == "undefined" ) { 
                //Here we are plotting coverage bars
                $.each( data['data'], function(i,arr) {

                    var start_time = parseFloat(arr[0],10) *1000;
                    var end_time   = parseFloat(arr[1],10) *1000;
                    flot_data.push([start_time,1,end_time]);

                });

                $("#"+plt).attr("class", "plot_cov");

                var canvas = $.plot($("#"+plt),[ flot_data ], PlotSelect.cov);

            } else if( data['format'] == 'bins' ) {

                for ( var i=0, len=data['data'].length; i<len; ++i ){
                    temp_data = data['data'][i];
                    flot_data[i] =  [temp_data[0]*1000,temp_data[2],temp_data[1]];
                }

                // For waveforms
                PlotSelect.wf_bins.xaxis.min = PlotSelect.ts;
                PlotSelect.wf_bins.xaxis.max = PlotSelect.te;

                $("#"+plt).attr("class", "plot");

                var canvas = $.plot($("#"+plt),[ flot_data ], PlotSelect.wf_bins);

            } else {

                for ( var i=0, len=data['data'].length; i<len; ++i ){
                    temp_data = data['data'][i];
                    flot_data[i] =  [temp_data[0]*1000,temp_data[1]];
                }

                // For waveforms
                PlotSelect.wf_lines.xaxis.min = PlotSelect.ts;
                PlotSelect.wf_lines.xaxis.max = PlotSelect.te;

                $("#"+plt).attr("class", "plot");

                var canvas = $.plot($("#"+plt),[ flot_data ], PlotSelect.wf_lines);
            }

        //}}}
        }

        PlotSelect.chan_plot_obj[name] = canvas;

        var arrDiv = $("<div>").css(PlotSelect.NameCss).append(name);
        $('#'+plt).append(arrDiv);

//}}}
    },

    setPhases: function(start,end){

//{{{
        $.ajax({
            url:"/data/events/"+start+"/"+end,
            success: function(data) {
                $.each(data, function(sta_chan,p){

                    var pt = $('#' + sta_chan + '_plot'); 

                    if ( pt.length != 0){

                        $.each(p, function(phaseTime,phaseFlag){

                            var plot_obj = PlotSelect.chan_plot_obj[sta_chan]; 

                            var o = plot_obj.pointOffset( { x:(phaseTime*1000), y:1000 } ) ;

                            var flagTop = plot_obj.getPlotOffset() ;

                            var flagCss = PlotSelect.arrivalFlagCss;

                            flagCss['left'] = o.left + "px" ;
                            flagCss['top'] = flagTop.top + "px" ;

                            var flagTail = PlotSelect.arrivalTailCss;
                            flagTail['left'] = flagCss['left'] ;
                            flagTail['top'] = flagCss['top'] ;
                            flagTail['height'] = pt.height() + 'px';

                            var arrDiv = $("<div class='flag'>").css(flagCss).append( phaseFlag );
                            var arrTailDiv = $("<div class='flagTail'>").css(flagTail);

                            pt.append(arrDiv); // Flag
                            pt.append(arrTailDiv); // Flag tail
                        });
                    };
                });
            },
        });
//}}}

    }

};
