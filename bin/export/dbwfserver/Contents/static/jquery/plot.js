function build_dialog_boxes() {
    //{{{

    //Set loading dialog box
    $("#loading").dialog({ 
        //{{{
        autoOpen: false,
        dialogClass: "loading", 
        draggable: false, 
        resizable: false,
        //}}}
    }); // end of dialog 

    //}}}
}
function waitingDialog(waiting) { 
    //{{{

    $("#loading").html(waiting.message && '' != waiting.message ? waiting.message : 'Please wait...'); 
    $("#loading").dialog('option', 'title', waiting.title && '' != waiting.title ? waiting.title : 'Loading'); 
    $("#loading").dialog('open'); 
    PlotSelect.isPlotting = true;

    //}}}
}
function closeWaitingDialog() { 
    //{{{

    if (PlotSelect.activeQueries > 0) {
        setTimeout(closeWaitingDialog,100);
    }
    else {
        PlotSelect.isPlotting = false;
        $("#loading").dialog('close'); 
    }

    //}}}
}

// Automatic canvas resize
//{{{
var TO = false;
var window_active = false;
window.onblur = function() { window_active = false; }
window.onfocus = function() { window_active = true; }

$(window).resize(function(){

    if (TO !== false) {
        clearTimeout(TO);
    }
    if (window_active && $('#wforms').is(":visible") && ! PlotSelect.isPlotting ) {
        TO = setTimeout('PlotSelect.setData();', 2000);
    }
});
//}}}

PlotSelect = {
    init: function(){

    // {{{ Set defaults


        build_dialog_boxes();

        waitingDialog({title: "Waveform Explorer:", message: "Initializing..."});


        //  Setup AJAX defaults
        $.ajaxSetup({
            type: 'get',
            dataType: 'json',
            timeout: 120000,
            error:PlotSelect.errorResponse
        });

        // Set data conversion table
        PlotSelect.datatypes = {
            'A': 'acceleration (nm/sec/sec)',
            'B': 'UV (sunburn) index NOAA (25*nw/m/m)',
            'D': 'displacement (nm)',
            'H': 'hydroacoustic (pascal)',
            'I': 'infrasound (pascal)',
            'J': 'power (watts)',
            'K': 'generic pressure (kilopascal)',
            'M': 'Wood-Anderson drum recorder (millimeters)',
            'N': 'dimensionless (-)',
            'P': 'barometric pressure (millibar)',
            'R': 'rain fall (millimeters)',
            'S': 'strain (nm/m)',
            'T': 'time (seconds)',
            'V': 'velocity (nm/sec)',
            'W': 'insolation (watts/m/m)',
            'X': 'integrated displacement (nm*sec)',
            'Y': 'waveform power (power)',
            'a': 'azimuth (degrees)',
            'b': 'bit rate (bits/second)',
            'c': 'dimesionless integer(counts)',
            'd': 'depth or height(meters)',
            'f': 'photoactive radiation flux (micromoles/s/m/m)',
            'h': 'hydrogen ion concentration (pH)',
            'i': 'electric current (amperes)',
            'l': 'slowness (sec/km)',
            'm': 'dimensionless bitmap (bitmap)',
            'n': 'angle - tilt (nanoradians)',
            'o': 'dilution of oxygen (milligrams/liter)',
            'p': 'percentage (percent)',
            'r': 'rainfall (inches)',
            's': 'speed (meter/second)',
            't': 'temperature (degrees_Celsius)',
            'u': 'conductivity (microsiemens/cm)',
            'v': 'electric potential (volts)',
            'w': 'rotation rate (radians/second)',
            '-': 'UNKNOWN'
        };

        // To store plot objects
        PlotSelect.chan_plot_obj = {};

        // Defaults
        PlotSelect.isShiftPressed =  false;

        PlotSelect.activeQueries = 0;

        PlotSelect.isPlotting =  false;

        PlotSelect.dates_allowed = [];

        PlotSelect.show_points = false;
        PlotSelect.show_phases = true;
        PlotSelect.timezone = 'UTC';
        PlotSelect.type = 'waveform';
        PlotSelect.acceleration  = 'SI';
        PlotSelect.color = 'def';
        PlotSelect.ts = 0;
        PlotSelect.te = 0;
        PlotSelect.filter = 'None';
        PlotSelect.stations = '';
        PlotSelect.channels = '';


        // {{{ Define colorschemes

        PlotSelect.colorschemes = {};

        PlotSelect.colorschemes.yb = {
            bgColor   : { colors: ["#3366ff", "#00029f"] },
            selection : "#FFFFFF"
        };
        PlotSelect.colorschemes.bw = {
            lineColor : "#000000",
            bgColor   : { colors: ["#eee", "#404040"] },
            tickColor : "#666666",
            selection : "#666666"
        };
        PlotSelect.colorschemes.yg = {
            bgColor   : { colors: ["#00cc00", "#009900"] }
        };
        PlotSelect.colorschemes.wb = {
            lineColor : "#FFFFFF",
            bgColor   : { colors: ["#000", "#404040"] },
            tickColor : "#666666",
            selection : "#FFFFFF"
        };
        PlotSelect.colorschemes.yp = {
            bgColor   : { colors: ["#990066", "#660066"] }
        };
        PlotSelect.colorschemes.ob = {
            lineColor : "#FF6600",
            bgColor   : { colors: ["#000", "#404040"] },
            tickColor : "#666666",
            selection : "#FFFFFF"
        }
        PlotSelect.colorschemes.def = {
            selection : "#666666",
            bgColor   : { colors: ["#ffffff", "#d0d0d0"] }
        }

        // }}} Define colorschemes

        // Define global variables depending 
        // on the configuration. 
        PlotSelect.plotVarSet();

        closeWaitingDialog();

        // }}} Set defaults

    },

    keyBinds: function(){

    // {{{ Set bindings for keys

        $(document).unbind('keyup');
        $(document).unbind('keydown');

        $(document).keydown(function(e) {
            if (e.keyCode == '82') {
                // r for reset plot
                e.preventDefault();
            } else if(e.which == 16) {
                // Shift key
                PlotSelect.isShiftPressed = true;
            }
        });

        $(document).keyup(function(e) {
            if (e.keyCode == '82') {
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
        // Set global vars for color
        PlotSelect.canvasLineColor = PlotSelect.colorschemes['def']['lineColor'] ;
        PlotSelect.canvasBgColor   = PlotSelect.colorschemes['def']['bgColor'];
        PlotSelect.canvasTickColor = PlotSelect.colorschemes['def']['tickColor'];
        PlotSelect.canvasSelection = PlotSelect.colorschemes['def']['selection'];
        //}}} Set color scheme

        //{{{ Flot options

        // Function to produce tick labels for X axis
        x_formatter =  function (val, axis) {
            
            if ( $("input[name='timezone']:checked").val() == "local" ) {
                diff = - new Date(val).getTimezoneOffset();
                val = val + (diff * 60 *1000);
                if (diff < 0) {
                    lbl = '(UTC-' + (diff/60)+')';
                }
                else {
                    lbl = '(UTC+' + (diff/60)+')';
                }
            }
            else {
                lbl = 'UTC'
            }

            var newDate = new Date(val);

            var string =  newDate.getFullYear()+'-'+newDate.getMonth()+'-'+newDate.getDate()+' '
            string += newDate.getHours()+':'+newDate.getMinutes()+':'+newDate.getSeconds()+' '+lbl

            return string

        };
        // Function to produce tick labels for X axis
        y_formatter =  function (val, axis) {
            
            var range = Math.abs(axis.max - axis.min)

            if (val == 0) {
                return 0
            } 

            if (range < 100) {
                return val.toPrecision(2);
            }
            if (range < 1000) {
                return val.toPrecision(3);
            }

            if (Math.abs(val) > 0.01) {
                return val.toFixed(1);
            } else {
                return val.toPrecision(1);
            }

        };

        // Set FLOT defaults
        PlotSelect.flot_ops = {
            hoverable: false,
            clickable: false,
            colors: [PlotSelect.canvasLineColor], 
            selection: {mode:"x", color:PlotSelect.canvasSelection}, 
            grid: {hoverable:false,clickable:false, borderColor:PlotSelect.canvasTickColor, color:PlotSelect.canvasTickColor, tickColor:PlotSelect.canvasTickColor, backgroundColor:PlotSelect.canvasBgColor},
            xaxis: {tickFormatter:x_formatter, ticks:5, mode:"time", timeformat:"%y-%m-%d %H:%M:%S UTC"},
            yaxis: {tickFormatter:y_formatter, ticks:4, min:null, max:null },
            points: {show:false},
            lines: {show:false},
            bars: {show:false}
        };


        // For the text on the screen.
        PlotSelect.NameCss = { color:PlotSelect.canvasLineColor, 'font-size':'20px', position:'absolute', left:'10%', top:'15%'};

        // For the text on the screen.
        PlotSelect.calibCss = { color:PlotSelect.canvasLineColor, 'font-size':'10px', position:'absolute', left:'5%', bottom:'10%'};

        // For the exit icon
        PlotSelect.IconCss = { cursor:'pointer', position:'absolute', right:'1%', top:'5%'};

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

            alert('Error:'+ x + '\n\n' + e);

        }

        // }}}

    },

    handleSelect: function(evt, pos){

        // {{{ Selection zoom functionality

        if (PlotSelect.isShiftPressed) { /*if the Shift Key is pressed, we zoom out. */
            var delta = 0;

            delta = parseInt( pos.xaxis.from, 10 ) - PlotSelect.ts ;

            PlotSelect.ts -= delta;

            delta = PlotSelect.te - parseInt( pos.xaxis.to, 10 ) ;

            PlotSelect.te += delta;

            if (PlotSelect.ts < PlotSelect.original_ts) { 
                PlotSelect.ts = PlotSelect.original_ts; 
                //alert('You are limited to the original window!');
            }
            if (PlotSelect.te > PlotSelect.original_te) { 
                PlotSelect.te = PlotSelect.original_te; 
                //alert('You are limited to the original window!');
            }

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
        //$("#loading").show();
        waitingDialog({});

        console.log(PlotSelect.sta);
        console.log(PlotSelect.chan);
        console.log(PlotSelect.traces);
        console.log(PlotSelect.ts);
        console.log(PlotSelect.te);

        if ( typeof(resp) !="undefined") {
            // 
            // If resp defined... update globals
            //
            // PlotSelect is define globally for app
            if (resp['error']) {
                PlotSelect.errorResponse('parsererror',resp['error']);
            }

            if (resp.traces) {
                PlotSelect.traces = resp['traces'];
            }
            else {
                PlotSelect.errorResponse('parsererror','No stations/channels selected.');
                closeWaitingDialog();
                return
            }
            if (resp.sta) {
                PlotSelect.sta = resp['sta'].sort();
            }
            if (resp.chan) {
                PlotSelect.chan = resp['chan'].sort();
            }
            if (resp.time_start) {
                PlotSelect.ts = resp['time_start'] * 1000;
                if ( typeof(PlotSelect.original_ts) == "undefined" ) {
                    PlotSelect.original_ts = PlotSelect.ts;
                }
            }
            if (resp.time_end) {
                PlotSelect.te = resp['time_end'] * 1000;
                if ( typeof(PlotSelect.original_te) == "undefined" ) {
                    PlotSelect.original_te = PlotSelect.te;
                }
            }
            if (resp.orid) {
                PlotSelect.orid = resp['orid'];
            }
            if (resp.phases) {
                PlotSelect.phases = resp['phases'];
            }
        }
        //if ( ! PlotSelect.sta ) {
        //    PlotSelect.errorResponse('parsererror','No stations selected.');
        //    closeWaitingDialog();
        //    return
        //}
        //if ( ! PlotSelect.chan ) {
        //    PlotSelect.errorResponse('parsererror','No channels selected.');
        //    closeWaitingDialog();
        //    return
        //}
        //console.log(PlotSelect.sta);
        //console.log(PlotSelect.chan);
        //console.log(PlotSelect.traces);
        //console.log(PlotSelect.ts);
        //console.log(PlotSelect.te);

        // Show plots
        $("#wforms").show('fast');

        //{{{
        PlotSelect.keyBinds();

        PlotSelect.getPhases(PlotSelect.ts/1000,PlotSelect.te/1000);

        // Sort Stations
        var s_stations = []
        $.each(PlotSelect.traces, function(mysta,mysta_object ){
            s_stations.push(mysta);
        });

        s_stations.sort();

        // Limit to 1 station
        s_stations = s_stations[0];

        // Start loop of stations
        //$.each(s_stations, function(ii,mysta){
        $.each([s_stations], function(ii,mysta){

            var s_channels = []

            $.each(PlotSelect.traces[mysta], function(mychan,mychan_object ){
                s_channels.push(mychan);
            });

            s_channels.sort();

            //$.each(mysta_object, function(mychan,mychan_object ){
            $.each(s_channels, function(jj,mychan){


                if ( PlotSelect.traces[mysta][mychan] == 'True' ) {

                    var url = '/data/wf'

                    url += '/' + mysta;

                    url += '/' + mychan;

                    if (PlotSelect.ts) {
                        url += '/' + PlotSelect.ts / 1000;
                    } else {
                        url += '/-';
                    }
                    if (PlotSelect.te ) {
                        url += '/' + PlotSelect.te / 1000;
                    } else {
                        url += '/-';
                    }
                    if ( PlotSelect.filter ) {
                        url += '/' + PlotSelect.filter;
                    } else {
                        url += '/-';
                    }

                    var wpr = mysta + '_' + mychan + '_wrapper' ;

                    $("#wforms").append( $("<div>").attr("id",wpr ).attr("class","wrapper") );

                    $("#"+wpr).width( $(window).width() );

                    PlotSelect.activeQueries += 1; 
                    $.ajax({

                        url:url,
                        success: function(data) {
                            if (typeof(data[mysta][mychan]) != "undefined" ) { 
                                PlotSelect.plotData(mysta,mychan,data[mysta][mychan]);
                                if (typeof(PlotSelect.ts) != "undefined" ) {
                                    // check end_time only if we have start time
                                    if (typeof(PlotSelect.te) != "undefined" ) {
                                        // call only if we have start and end times
                                        PlotSelect.setPhases(mysta,mychan,PlotSelect.ts/1000,PlotSelect.te/1000);
                                    }
                                }
                            } else { 
                                PlotSelect.activeQueries -= 1; 
                                PlotSelect.traces.mysta.mychan = 'False';
                            }

                        },

                    });

                }

            });

        });

        //}}}

        $(".flag").show();
        $(".flagTail").show();

        closeWaitingDialog();
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

            var canvas = $.plot($("#"+plt),[], PlotSelect.flot_ops);

            var arrDiv = $("<div>").css(PlotSelect.NameCss);

            arrDiv.css({ color:'red', left:'30%', top:'5%'});

            arrDiv.append('No data in time segment: ('+PlotSelect.ts/1000+','+PlotSelect.te/1000+').');

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

                // Set FLOT options
                // for coverage
                PlotSelect.flot_ops.lines     = {show:false};
                PlotSelect.flot_ops.yaxis.ticks = 0;
                PlotSelect.flot_ops.yaxis.min   = 1;
                PlotSelect.flot_ops.yaxis.max   = 2;
                PlotSelect.flot_ops.bars = {
                        show:true,
                        horizontal:true,
                        barWidth:1,
                        fill:true,
                        fillColor:PlotSelect.canvasLineColor
                };

                $("#"+plt).attr("class", "plot_cov");

                var canvas = $.plot($("#"+plt),[ flot_data ], PlotSelect.flot_ops);

            } else if( data['format'] == 'bins' ) {

                if ( typeof(data['metadata']['segtype']) != "undefined" ) { 
                    var segtype = data['metadata']['segtype'];
                } else {
                    var segtype = '-';
                }
                if ( typeof(data['metadata']['calib']) != "undefined" ) { 
                    var calib = data['metadata']['calib'];
                } else {
                    var calib = 1;
                }

                if ( calib == 0 ){
                    calib = 1;
                }

                if ( typeof(PlotSelect.datatypes[segtype]) != "undefined") {
                    if (segtype == 'A' ) {

                        if (PlotSelect.acceleration == 'G') {
                            segtype = '(A) => acceleration (G)';
                            // "1 g = 9.80665 m/s2" 
                            calib = 1/9806;
                        }
                        else {
                            segtype = '(A) => ' + PlotSelect.datatypes[segtype];
                        }
                    }
                    else {
                        segtype = '(' + segtype + ') => ' + PlotSelect.datatypes[segtype];
                    }
                }

                for ( var i=0, len=data['data'].length; i<len; ++i ){
                    temp_data = data['data'][i];
                    if (temp_data[1] == temp_data[2]) { 
                        //temp_data[2] += .1; 
                        flot_data[i] =  [temp_data[0]*1000,temp_data[1]*calib];
                    }
                    else { 
                        flot_data[i] =  [temp_data[0]*1000,temp_data[2]*calib,temp_data[1]*calib];
                    }
                }

                // Set FLOT options
                // for bars
                PlotSelect.flot_ops.xaxis.min   = PlotSelect.ts;
                PlotSelect.flot_ops.xaxis.max   = PlotSelect.te;
                PlotSelect.flot_ops.points      = {show:false};
                //PlotSelect.flot_ops.lines       = {show:false};
                PlotSelect.flot_ops.lines       = {show:true};
                PlotSelect.flot_ops.bars        = {show:true,barWidth:0,align:'center'};
                PlotSelect.flot_ops.yaxis.ticks = 4;

                $("#"+plt).attr("class", "plot");

                var canvas = $.plot($("#"+plt),[ flot_data ], PlotSelect.flot_ops);
                PlotSelect.activeQueries -= 1; 

                var arrDiv = $("<div>").css(PlotSelect.calibCss).append('[ calib:'+calib+',  segtype:'+segtype+' ]');
                $('#'+plt).append(arrDiv);

            } else {

                if ( typeof(data['metadata']['segtype']) != "undefined" ) { 
                    var segtype = data['metadata']['segtype'];
                } else {
                    var segtype = '-';
                }
                if ( typeof(data['metadata']['calib']) != "undefined" ) { 
                    var calib = data['metadata']['calib'];
                } else {
                    var calib = 1;
                }

                if ( calib == 0 ){
                    calib = 1;
                }

                if ( typeof(PlotSelect.datatypes[segtype]) != "undefined") {
                    if (segtype == 'A' ) {

                        if (PlotSelect.acceleration == 'G') {
                            segtype = '(A) => acceleration (G)';
                            // "1 g = 9.80665 m/s2" 
                            calib = 1/9806;
                        }
                        else {
                            segtype = '(A) => ' + PlotSelect.datatypes[segtype];
                        }
                    }
                    else {
                        segtype = '(' + segtype + ') => ' + PlotSelect.datatypes[segtype];
                    }
                }

                for ( var i=0, len=data['data'].length; i<len; ++i ){
                    temp_data = data['data'][i];
                    flot_data[i] =  [temp_data[0]*1000,temp_data[1]*calib];
                }

                // Set FLOT options
                // for lines
                PlotSelect.flot_ops.xaxis.min   = PlotSelect.ts;
                PlotSelect.flot_ops.xaxis.max   = PlotSelect.te;
                if ( PlotSelect.show_points ) { 
                    PlotSelect.flot_ops.points      = {show:true,lineWidth:1,shadowSize:0};
                } else { 
                    PlotSelect.flot_ops.points      = {show:false};
                }
                PlotSelect.flot_ops.lines       = {show:true,lineWidth:1,shadowSize:0};
                PlotSelect.flot_ops.bars        = {show:false};
                PlotSelect.flot_ops.yaxis.ticks = 4;
                PlotSelect.flot_ops.yaxis.min   = null;
                PlotSelect.flot_ops.yaxis.max   = null;

                $("#"+plt).attr("class", "plot");

                var canvas = $.plot($("#"+plt),[ flot_data ], PlotSelect.flot_ops);
                PlotSelect.activeQueries -= 1; 

                var arrDiv = $("<div>").css(PlotSelect.calibCss).append('[ calib:'+calib+',  segtype:'+segtype+' ]');
                $('#'+plt).append(arrDiv);
            }

        //}}}
        }

        PlotSelect.chan_plot_obj[name] = canvas;

        var arrDiv = $("<div>").css(PlotSelect.NameCss).append(name);
        $('#'+plt).append(arrDiv);

        var arrDiv = $("<div>").attr("id","remove_"+name).css(PlotSelect.IconCss).attr("class","icons ui-state-dfault ui-corner-all").append("<span class='ui-icon ui-icon-close'></span>");
        $('#'+plt).append(arrDiv);

        $(function() {
            $("#remove_"+name) .click(function() {
                $("#"+wpr).remove();
                delete PlotSelect.traces[sta][chan];
            })
            .mouseenter(function() {
                $(this).addClass('ui-state-hover');
            })
            .mouseleave(function() {
                $(this).removeClass("ui-state-hover");
            });
        });




//}}}

    },

    getPhases: function(start,end){

//{{{
        $.ajax({
            url:"/data/events/"+start+"/"+end,
            success: function(data) {
                if (typeof(data) == "undefined" ) { return; }
                if (data == "null" ) { return; }
                if (! data ) { return; }
                PlotSelect.phases = data;
            },
        });
//}}}

    },

    setPhases: function(sta,chan,start,end){

//{{{
        $.each(PlotSelect.phases, function(sta_chan,p){

            if ( sta+'_'+chan == sta_chan ) {
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
            };
        });
//}}}

    }
};
