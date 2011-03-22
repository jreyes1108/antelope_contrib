// Defaults
//{{{ Set defaults
var proxy = '';
var mode = 'full';
var isShiftPressed =  false;
var activeQueries = 0;
var isPlotting =  false;

var ts = null;
var te = null;
var original_ts = null;
var original_te = null;
var sta = ['.*'];
var chan = ['.*'];

var filter = 'None';
var timezone = 'UTC';
var type = 'waveform';
var size = 'medium';
var show_points = true;
var show_phases = true;
var acceleration  = 'SI';
var tick_color = '#000000';
var bg_top_color = '#000080';
var bg_bottom_color = '#0000FF';
var text_color = '#D3D3D3';
var data_color = '#FFFF00';

var TO = false;
var window_active = false;

var chan_plot_obj = {};

var dates_allowed = [];

var traces = {};
//var sta_array = [];
//var chan_array = [];

// Set data conversion table
//{{{
datatypes = {
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
//}}}

//}}} Default vars

function init(){
// {{{ Set defaults

    //{{{ Automatic canvas resize
    window.onblur = function() { window_active = false; }
    window.onfocus = function() { window_active = true; }

    $(window).resize(function(){

        if (TO !== false) {
            clearTimeout(TO);
        }
        if (window_active && ! $('#wforms').hasClass("ui-helper-hidden") && ! isPlotting ) {
            TO = setTimeout('setData();', 2000);
        }
    });
    //}}} Automatic canvas resize

    build_dialog_boxes();

    waitingDialog({title: "Waveform Explorer:", message: "Initializing..."});

    //  Setup AJAX defaults
    $.ajaxSetup({
        type: 'get',
        dataType: 'json',
        timeout: 120000,
        error:errorResponse
    });

    getCookie();

    set_click_responses();

    //build_calendars();

    varSet();

    keyBinds();

    $("button, input:submit, input:checkbox").button();

    closeWaitingDialog();

    // }}} Set defaults
}

function openSubnav() {
    // {{{ open subnav div

    waitingDialog({title: "Waveform Explorer:", message: "Initializing..."});

    var selection = '';
    for (var i in sta ) {
        selection = (selection == '') ? sta[i] : selection+'-'+sta[i];
    }
    $("#station_string").val(selection);

    var selection = '';
    for (var i in chan ) {
        selection = (selection == '') ? chan[i] : selection+'-'+chan[i];
    }
    $("#channel_string").val(selection);

    $("#start_time").val(ts);
    $("#end_time").val(te);

    $('#subnav').removeClass('ui-helper-hidden');

    closeWaitingDialog();

    // }}}
}
function closeSubnav() {
    // {{{ close subnav div

    $('#subnav').addClass('ui-helper-hidden');

    // }}}
}
function getCookie() {
    //{{{ Get cookie values
        //
        // Look for cookie values and update elements
        //
        show_phases = ($.cookie('dbwfserver_phases') == 'true') ? true : false;

        show_points = ($.cookie('dbwfserver_points') == 'true') ? true : false;

        timezone = ($.cookie('dbwfserver_time_zone') == 'local') ? 'local' : 'UTC';

        type = ($.cookie('dbwfserver_type') == 'coverage') ? 'coverage' : 'waveform';

        acceleration = ($.cookie('dbwfserver_acceleration') == 'SI') ? 'SI' : 'G';

        if ($.cookie('dbwfserver_size')) size  =  $.cookie('dbwfserver_size');

        if ($.cookie('dbwfserver_bg_top_color')) bg_top_color  =  $.cookie('dbwfserver_bg_top_color');

        if ($.cookie('dbwfserver_bg_bottom_color')) bg_bottom_color  =  $.cookie('dbwfserver_bg_bottom_color');

        if ($.cookie('dbwfserver_tick_color')) tick_color  =  $.cookie('dbwfserver_tick_color');

        if ($.cookie('dbwfserver_data_color')) data_color  =  $.cookie('dbwfserver_data_color');

        if ($.cookie('dbwfserver_text_color')) text_color  =  $.cookie('dbwfserver_text_color');

        if ($.cookie('dbwfserver_filter')) filter  =  $.cookie('dbwfserver_filter');

    //}}} Get cookie values
}

function setCookie() {
    //{{{ Set cookie

        // Set COOKIE global options
        COOKIE_OPTS = { path: '/', expiresAt: 99 };

        $.cookie('dbwfserver_time_zone', timezone, COOKIE_OPTS);

        $.cookie('dbwfserver_type', type, COOKIE_OPTS);

        $.cookie('dbwfserver_size', size, COOKIE_OPTS);

        $.cookie('dbwfserver_acceleration', acceleration, COOKIE_OPTS);

        $.cookie('dbwfserver_bg_top_color', bg_top_color, COOKIE_OPTS);

        $.cookie('dbwfserver_bg_bottom_color', bg_bottom_color, COOKIE_OPTS);

        $.cookie('dbwfserver_tick_color', tick_color, COOKIE_OPTS);

        $.cookie('dbwfserver_text_color', text_color, COOKIE_OPTS);

        $.cookie('dbwfserver_data_color', data_color, COOKIE_OPTS);

        $.cookie('dbwfserver_filter', filter, COOKIE_OPTS);

        $.cookie('dbwfserver_phases', show_phases, COOKIE_OPTS);

        $.cookie('dbwfserver_points', show_points, COOKIE_OPTS);

        //$.cookie('dbwfserver_stime', ts , COOKIE_OPTS);

        //$.cookie('dbwfserver_etime', te , COOKIE_OPTS);

        //$.cookie('dbwfserver_sta', stations , COOKIE_OPTS);

        //$.cookie('dbwfserver_chan', channels , COOKIE_OPTS);

    //}}} Set cookie
}

function build_dialog_boxes() {
    //{{{

    //Set station and channel dialog boxes
    $("#list").dialog({ 
        //{{{
        height: 'auto',
        width: 'auto',
        autoOpen: false,
        draggable: true, 
        resizable: true,
        buttons: {
            OK: function() {

                var target;
                var selection = '';
                var type_opt = $( this ).dialog('option', 'title'); 


                if (type_opt == 'Select Channels:') {
                    target = $("#channel_string");
                }
                else if (type_opt == 'Select Stations:') {
                    target = $("#station_string");
                }
                else { 
                    alert( 'ERROR: '+ type_opt );
                    $( this ).dialog( "close" );
                    return;
                }

                target.val('.*');

                $(".ui-selected").each(function(){
                    if ( ! selection ) {
                        selection = $( this ).text();
                    }
                    else { 
                        selection = selection+'-'+$( this ).text();
                    }
                });

                if ( selection ) target.val(selection);

                $( this ).dialog( "close" );

            },
            Cancel: function() {
                $( this ).dialog( "close" );
            }
        }
        //}}}
    }); // end of dialog 

    //Set loading dialog box
    $("#event_list").dialog({ 
        //{{{
        autoOpen: false,
        draggable: true, 
        resizable: true,
        minWidth:  600, 
        //}}}
    }); // end of dialog 

    //Set loading dialog box
    $("#configpanel").dialog({ 
        //{{{
        autoOpen: false,
        draggable: true, 
        resizable: true,
        buttons: {
            OK: function() {

                timezone = $("input[name='timezone']:checked").val();

                type = $("input[name='wf_type']:checked").val();

                size = $("input[name='wf_size']:checked").val();

                acceleration = $("input[name='accel_type']:checked").val();

                bg_top_color = $("#bg_top_color").val();

                bg_bottom_color = $("#bg_bottom_color").val();

                tick_color = $("#tick_color").val();

                text_color = $("#text_color").val();

                data_color = $("#data_color").val();

                filter = $("#filter").val(); 

                show_phases = $('#phases').is(':checked') ? true : false; 

                show_points = $('#points').is(':checked') ? true : false;

                setCookie();

                varSet();

                $( this ).dialog( "close" );

                if (! $("#subnav").is(":visible") ) { setData(); }

            },
            Cancel: function() {
                $( this ).dialog( "close" );
            }
        },
        //}}}
    }); // end of dialog 

    //Set loading dialog box
    $("#helppanel").dialog({ 
        //{{{
        autoOpen: false,
        draggable: true, 
        resizable: true,
        buttons: {
            OK: function() {
                $( this ).dialog( "close" );
            }
        }
        //}}}
    }); // end of dialog 

    //Set loading dialog box
    $("#loading").dialog({ 
        //{{{
        autoOpen: false,
        dialogClass: "ui-state-error", 
        draggable: false, 
        resizable: false,
        open: function(event, ui) { isPlotting = true; },
        close: function(event, ui) { isPlotting = false; }
        //}}}
    }); // end of dialog 

    //}}}
}

function waitingDialog(waiting) { 
    //{{{

    $("#loading").html( (waiting.message && '' != waiting.message) ? waiting.message : 'Please wait...'); 
    $("#loading").dialog('option', 'title', (waiting.title && '' != waiting.title) ? waiting.title : 'Loading'); 
    $("#loading").dialog('open'); 

    //}}}
}

function closeWaitingDialog() { 
    //{{{

    if (activeQueries > 0) {
        setTimeout(closeWaitingDialog,100);
    }
    else {

        if (! $('#wforms').hasClass("ui-helper-hidden") ) setPhases();

        $("#loading").dialog('close'); 
        $("#loading").empty(); 
    }

    //}}}
}

function build_calendars() { 
    //{{{

    // Build DATEPICKER
    $(".pickdate").datepicker({
        dateFormat: '@',
        beforeShowDay: function(test_date) { 

            diff = test_date.getTimezoneOffset();

            var found = true;

            //$.each(dates_allowed, function(key,value) {

            //    var option = new Date((value + (diff*60)) * 1000 );

            //    if (test_date.getTime() == option.getTime()) { found = true; }

            //});

            return found ? [true,'','Valid'] : [false,'','Not valid.']; 

        },
        onSelect: function(dateText, inst) {
            if (this.id == "end_time"){
                var old = $(".pickdate").not(this).val();
                $(".pickdate").not(this).datepicker("option", 'maxDate', dateText );
                $(".pickdate").not(this).val( old );
                $("#end_time").val( (dateText / 1000) + 86399 );
            } else {
                var old = $(".pickdate").not(this).val();
                $(".pickdate").not(this).datepicker("option", "minDate", dateText);
                $(".pickdate").not(this).val( old );
                $("#start_time").val( dateText / 1000 );
            }
        }
    });

    //
    // Set the max and min on datepicker to 
    // database max and min times on wfdisc
    //

    $.ajax({
        url: proxy + "/data/dates",
        success: function(json) {

            var max = 0;
            var min = 999999999999;

            if ( typeof(json) != "undefined" ) {

                $.each(json, function(key,value) {

                    if ( value[0] < min) { min = value[0]; }
                    if ( value[1] > max) { max = value[1]; }

                });

                $(".pickdate").datepicker("option", 'minDate', min*1000+''); 
                $(".pickdate").datepicker("option", 'maxDate', max*1000+''); 

                dates_allowed = json;

            }

        }
    });

    //}}}
}

function set_click_responses() { 
    //{{{

    $('#home').click( function(){ 
        //{{{
        closeSubnav();

        $('#list').empty();
        $('#event_list').empty();
        $('#wforms').addClass('ui-helper-hidden');
        $('#wforms').empty();

        openSubnav();
        //}}}
    });

    $('#openconfig').click( function(){ 
    //{{{ Get cookie values
        //
        // Look for cookie values and update elements
        //
        if ( show_phases ){
            $('#phases').attr('checked', true);
        } else {
            $('#phases').removeAttr('checked');
        }

        if ( show_points ){
            $('#points').attr('checked', true);
        } else{
            $('#points').removeAttr('checked');
        }

        if (timezone ==  'local'){
            $('#local').attr('checked', true);
            $('#utc').attr('checked', false);
        } else {
            $('#local').attr('checked', false);
            $('#utc').attr('checked', true);
        }

        if ( type  == 'coverage' ) {
            $('#coverage').attr('checked', true);
            $('#waveform').attr('checked', false);
        } else {
            $('#coverage').attr('checked', false);
            $('#waveform').attr('checked', true);
        }

        if ( size  == 'big' ) {
            $('#big').attr('checked', true);
            $('#medium').attr('checked', false);
            $('#small').attr('checked', false);
        } else if ( size  == 'medium' ) {
            $('#big').attr('checked', false);
            $('#medium').attr('checked', true);
            $('#small').attr('checked', false);
        } else {
            $('#big').attr('checked', false);
            $('#medium').attr('checked', false);
            $('#small').attr('checked', true);
        }

        if ( acceleration  == 'G' ) {
            $('#G').attr('checked', true);
            $('#SI').attr('checked', false);
        } else {
            $('#G').attr('checked', false);
            $('#SI').attr('checked', true);
        }

        if ( bg_top_color ){
            $('#bg_top_color').val(bg_top_color);
        } else {
            $('#bg_top_color').val('#D3D3D3');
        }

        if ( bg_bottom_color ){
            $('#bg_bottom_color').val(bg_bottom_color);
        } else {
            $('#bg_bottom_color').val('#FFFFFF');
        }

        if ( tick_color ){
            $('#tick_color').val(tick_color);
        } else {
            $('#tick_color').val('#808080');
        }

        if ( text_color ){
            $('#text_color').val(text_color);
        } else {
            $('#text_color').val('#808080');
        }

        if ( data_color ){
            $('#data_color').val(data_color);
        } else {
            $('#data_color').val('#808080');
        }

        if ( filter ) {
            $('#filter').val( filter) ;
        } else {
            $('#filter').val('none');
        }

        $("button, input:submit, input:checkbox").button('refresh');
        $("#time_zone").buttonset();
        $("#plot_type").buttonset();
        $("#plot_size").buttonset();
        $("#acceleration").buttonset();

        $("#configpanel").dialog('option', 'title','Configuration:'); 
        $("#configpanel").dialog('open'); 

    //}}} Get cookie values
    });

    $('#openhelp').click( function(){ 
    //{{{
        $("#helppanel").dialog('option', 'title','HELP:'); 
        $("#helppanel").dialog('open'); 
    //}}}
    });

    $('#load_events').click( function(){ 
    //{{{
        $('#event_list').empty();
        $.ajax({
            url: proxy + "/data/events",
            success: function(json) {
                //{{{
                sorted_e_list = [];
                table_headers = [];

                if ( typeof(json) == "undefined" ) {
                    $("#event_list").append('Error in AJAX query. Try using calendars.');
                } else {
                    $.each(json, function(key,value) {
                        sorted_e_list.push(key);
                        $.each( value, function(sKey,sVal) {
                            if( $.inArray(sKey,table_headers) == -1 ) { table_headers.push(sKey); }
                        });
                    });
                    sorted_e_list = sorted_e_list.sort();
                    table_headers = table_headers.sort();

                    tbl = '<table id="evsTbl" class="evListTable">';

                    tbl += '<thead><tr>\n';
                    tbl += '<th>time</th>\n';

                    $.each(table_headers, function(thi, thv) {
                        if( thv !== 'time' ) { tbl += '<th>'+thv+'</th>\n'; }
                    });

                    tbl += '</tr></thead><tbody>\n';

                    $.each(sorted_e_list, function(key, value) {
                        tbl += "<tr>";
                        var time  = json[value]['time'];
                        var tbl_date = new Date(time * 1000);
                        tbl += "<td><a class='add_events'href='#'id='";
                        tbl += json[value]['time'] * 1000 + "'>";
                        tbl += "<span style='display:none;'>";
                        tbl += json[value]['time'] * 1000 + "</span>" + tbl_date + "</a></td>";
                        $.each(table_headers, function(thi, thv) { 
                            if( thv !== 'time' ) { tbl += "<td>" + json[value][thv] + "</td>"; }
                        });
                        tbl += "</tr>";
                    });

                    tbl += '</tbody></table>';
                    $("#event_list").append(tbl);
                    $("#event_list #evsTbl").tablesorter( {sortList: [[0,0], [1,0]]} );

                    $('.add_events').click( function($e){
                        $('#event_list').dialog('close');
                        $e.preventDefault();
                        time = $(this).attr("id");
                        if ( typeof(time) != "undefined" ) {
                            time /=  1000;
                        }
                        $("#start_time").val(time);
                    });
                }
                $("#event_list").dialog('option', 'title','Events:'); 
                $("#event_list").dialog('open'); 
                //}}}
            }
        }); 
    //}}}
    });

    $('#clear').click( function(){
        //{{{
        ts = null;
        te = null;
        original_ts = null;
        original_te = null;
        sta = ['.*'];
        chan = ['.*'];
        closeSubnav();
        $("#station_string").val('.*');
        $("#channel_string").val('.*');
        $("#start_time").val('');
        $("#end_time").val('');
        $('#list').empty();
        $('#event_list').empty();
        $('#wforms').empty();
        $('#wforms').addClass('ui-helper-hidden');
        $("#errors p").remove();
        $('#errors').addClass('ui-helper-hidden');
        openSubnav();
        //}}}
    });

    $('#plot').click( function(){
        //{{{

        sta = ( $('#station_string').val() ) ? $("#station_string").val().split('-') : ['.*'];
        chan = ( $('#channel_string').val() ) ? $("#channel_string").val().split('-') : ['.*'];

        start = ( $('#start_time').val() ) ? $("#start_time").val() : null;

        end = ( $('#end_time').val() ) ? $("#end_time").val() : null;

        $('#list').empty();
        $('#event_list').empty();
        $('#wforms').empty();
        closeSubnav();

        setData();

        //}}}
    });

    $('#load_stas').click( function($e){
    //{{{
        $('#list').empty();
        $("#list").html("<ol></ol>");
        $.ajax({
            url: proxy + "/data/stations",
            async:false,
            success: function(json) {

                for (var i in json.sort()) {
                    $("#list ol").append('<li id="'+json[i]+'" class="ui-state-default">'+json[i]+'</li>');
                }

                $("#list").selectable();

            }
        });

        $("#list").dialog('option', 'title','Select Stations:'); 
        $("#list").dialog('open'); 

        //}}}
    });

    $('#load_chans').click( function($e){
        //{{{

        $('#list').empty();
        $("#list").html("<ol></ol>");

        $.ajax({
            url: proxy + "/data/channels",
            async:false,
            success: function(json) {
                for (var i in json.sort()) {
                    $("#list ol").append('<li id="'+json[i]+'" class="ui-state-default ui-selectee">'+json[i]+'</li>');
                }

                $("#list").selectable();

            }
        });

        $("#list").dialog('option', 'title','Select Channels:'); 
        $("#list").dialog('open'); 

        //}}}
    });

    $("#remove_error") .click(function() {
        $("#errors p").remove();
        $('#errors').addClass('ui-helper-hidden');
    })
    $('#remove_error').mouseenter(function() {
        $(this).addClass('ui-state-hover');
    })
    $('#remove_error').mouseleave(function() {
        $(this).removeClass("ui-state-hover");
    });
    //}}}
}

function setupUI(resp) {
//{{{

    if (resp) {
    //{{{

        if (typeof(resp.mode) != "undefined" ) {

            if (resp.mode == "simple") { 
                mode = 'simple';
                $("#toppanel").hide()
                $("#title").hide()
                $("#subnav").hide()
                $("#name_path").hide()
                $("#control_bar").hide()

                handleSelect = function() {};
                shiftPlot = function() {};
                flot_ops.selection = {mode:null}; 
            }
            else if (resp.mode == "limited") { 
                mode = 'limited';
                $("#toppanel").hide()
                $("#title").hide()
                $("#subnav").hide()
                $("#name_path").hide()
                $("#control_bar").hide()
            }

        }
    //}}}
    }

//}}}
}

function keyBinds(){
    // {{{ Set bindings for keys
        if (mode == "simple") return;


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
                isShiftPressed = true;
            }
        });

        $(document).keyup(function(e) {
            if (e.keyCode == '38') {
                // Up key
                e.preventDefault();
                shiftPlot('I');
            } else if (e.keyCode == '40') {
                // Down key
                e.preventDefault();
                shiftPlot('O');
            } else if (e.keyCode == '37') {
                // Left key
                e.preventDefault();
                shiftPlot('L');
            } else if (e.keyCode == '39') {
                // Right key
                e.preventDefault();
                shiftPlot('R');
            } else if (e.keyCode == '82') {
                // r for reset plot
                e.preventDefault();
                location.reload(true);
            } else if(e.which == 16) {
                // Shift key
                isShiftPressed = false;
            }
        });

    // }}} Set bindings for keys
}

function varSet(){
// {{{ Set vars for plots

    // Function to produce tick labels for X axis
    x_formatter =  function (val, axis) {
        //{{{
        if ( timezone == "local" ) {
            var lbl = '(UTC + ' + (diff/60)+')';
        }
        else {
            val += (new Date(val).getTimezoneOffset() * 60000);
            var lbl = 'UTC'
        }

        var newDate = new Date(val);

        //$('#errors').append('<p>Epoch:'+val+" date:"+ newDate + " diff:"+ diff + "</p>");
        //$('#errors').removeClass('ui-helper-hidden');
        return newDate.getFullYear()+'-'+newDate.getMonth()+'-'+newDate.getDate()+' '+newDate.getHours()+':'+newDate.getMinutes()+':'+newDate.getSeconds()+' '+lbl

        //}}}
    };

    // Function to produce tick labels for X axis
    y_formatter =  function (val, axis) {
        //{{{
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
        //}}}
    };

    // Set FLOT options
    canvasBgColor   = { colors: [bg_top_color, bg_bottom_color]};

    flot_ops = {
        hoverable: false,
        clickable: false,
        colors: [data_color], 
        selection: {mode:"x", color:text_color}, 
        grid: {hoverable:false,clickable:false, borderColor:tick_color, color:tick_color, tickColor:tick_color, backgroundColor:canvasBgColor},
        xaxis: {tickFormatter:x_formatter, ticks:5, mode:"time", timeformat:"%y-%m-%d %H:%M:%S UTC",labelWidth:130,labelHeight:0},
        yaxis: {tickFormatter:y_formatter, ticks:4, min:null, max:null ,labelWidth:0,labelHeight:0},
        points: {show:false},
        bars:  {show:false},
        lines: {show:false}
    };


    // For the text on the screen.
    NameCss = { color:text_color, 'font-size':'20px', position:'absolute', left:'5%', top:'8%'};

    // For the text on the screen.
    calibCss = { color:text_color, 'font-size':'15px', position:'absolute', left:'15%', top:'8%'};

    // For the exit icon
    IconCss = { cursor:'pointer', position:'absolute', right:'1%', top:'5%'};

    // {{{ Arrival flag CSS
    arrivalFlagCss = {
        'border':'1px solid #FFF',
        'background-color':'#F00',
        'font-weight':'bold',
        'font-size':'smaller',
        'color':'#FFF',
        'padding':'3px',
        'position':'absolute'
    };
    arrivalTailCss = {
        'position':'absolute',
        'border':'none',
        'border-left':'1px solid #FFF',
        'margin':'0',
        'padding':'0',
        'width':'1px'
    };
    // }}} Arrival flag CSS

// }}} Set vars for plots
}

function errorResponse(x,e) {
    // {{{ Report Errors to user

    if(x.status==0){

        //alert('You are offline!!\n Please Check Your Network.' + '\n\n' + e);
        $('#errors').append('<p>Problem in query. Reload browser.' + e +'</p>');

    }else if(x.status==404){

        //alert('Requested URL not found.' + '\n\n' + e);
        $('#errors').append('<p>Requested URL not found.' + e + '</p>');

    }else if(x.status==500){

        //alert('Internel Server Error.' + '\n\n' + e);
        $('#errors').append('<p>Internel Server Error.' + e +'</p>');

    }else if(e=='parsererror'){

        //alert('Error.\nParsing JSON Request failed.' + '\n\n' + e);
        $('#errors').append('<p>Error. Parsing JSON Request failed.' + e + '</p>');

    }else if(e=='timeout'){

        //alert('Request Time out.' + '\n\n' + e);
        $('#errors').append('<p>Request Time out.' + e + '</p>');

    }else {

        //alert('Error:'+ x + '\n\n' + e);
        $('#errors').append('<p>Error:'+ x + ': ' + e + '</p>');

    }

    $('#errors').removeClass('ui-helper-hidden');

    // }}}
}

function shiftPlot(evt) {
    // {{{ Future data

    var delta = te - ts ;

    delta /= 4;

    if (evt == 'L') { 
        ts -= delta;
        te -= delta;
    } else if (evt == 'R') {
        ts += delta;
        te += delta;
    } else if (evt == 'I') {
        ts += delta;
        te -= delta;
    } else if (evt == 'O') {
        ts -= delta;
        te += delta;
    }

    setData();

    // }}} Future data
}

function handleSelect(evt, pos){
    // {{{ Selection zoom functionality

    if (isShiftPressed) {
        var delta = 0;

        delta = parseInt( pos.xaxis.from, 10 )/1000 - ts ;

        ts -= delta;

        delta = te - parseInt( pos.xaxis.to, 10 )/1000;

        te += delta;

        if (mode == "limited") { 
            if (ts < original_ts) { ts = original_ts; }
            if (te > original_te) { te = original_te; }
        }

    }
    else { 

        ts = parseInt( pos.xaxis.from, 10 )/1000 ;
        te = parseInt( pos.xaxis.to, 10 )/1000 ;

    }

    setData();

    // }}} Selection zoom functionality
}

function buildWrappers(){
    //{{{

    //
    // Build each plot wrapper in order
    //

    //errorResponse('buildWrappers(): ','TEST ERROR STRING');

    var sta_array = [];
    var numerals = false;

    for ( var mysta in traces ) {
        if(isNaN(mysta)){
            sta_array.push(mysta);
        } else {
            numerals = true;
            sta_array.push( parseInt(mysta) );
        }
    }

    if (numerals) 
        sta_array.sort(function(a,b){return a - b});
    else
        sta_array.sort();

    for ( var s_key in sta_array ) {
        var chan_array = [];
        var s_val = sta_array[s_key];
        var numerals = false;

        for ( var mychan in traces[s_val]) { 
            if(isNaN(traces[s_val][mychan])){
                chan_array.push(traces[s_val][mychan]);
            } else {
                numerals = true;
                chan_array.push( parseInt(traces[s_val][mychan]) );
            }
        }

        if (numerals) 
            chan_array.sort(function(a,b){return a - b});
        else
            chan_array.sort();

        for ( var c_key in chan_array ) {
            var c_val = chan_array[c_key];
            var wpr = s_val + '_' + c_val + '_wrapper' ;
            // If we don't have div then build one...
            if ( $("#"+wpr).length == 0 ){
                $("#wforms").append( $("<div>").attr("id",wpr ).attr("class","wrapper") );
            }

            $("#"+wpr).empty();
            $("#"+wpr).width( $('#name_path').width() );
            $("#"+wpr).html(' <div class="ui-state-highlight ui-corner-all" style="width:100%;height:100%;margin:5px"><p><span class="ui-icon ui-icon-info" style="float:left"></span><strong>Loading plot ['+s_val+'_'+c_val+']</strong></p></div>');

            //if ( type == 'coverage') { 
            //    $("#"+wpr).height( 50 );
            //} else if (size == 'big') {
            //    $("#"+wpr).height( 200 );
            //} else if (size == 'medium') {
            //    $("#"+wpr).height( 150 );
            //} else {
            //    $("#"+wpr).height( 100 );
            //}
        }
    }

    //}}}
}

function setData(resp) {
//{{{
    waitingDialog({title: "Waveform Explorer:", message: "Plotting data."});

    getCookie();

    // 
    // If resp defined... update globals
    //
    if ( resp ) {
    //{{{

        // is define globally for app
        if (resp.error) {
            errorResponse('setData(): ',resp['error']);
            return;
        }

        if (typeof(resp['sta']) != "undefined" ) { sta = resp['sta']; }

        if (typeof(resp['chan']) != "undefined" ) { chan = resp['chan']; }

        if (typeof(resp['traces']) != "undefined" ) { traces = resp['traces']; }

        if (typeof(resp['time_start']) != "undefined" ) { time_start = resp['time_start']; }

        if (typeof(resp['time_end']) != "undefined" ) { time_end = resp['time_end']; }

        //if (resp.traces) traces = resp['traces'];

        //if (resp.time_start) ts = resp['time_start'];

        //if (resp.time_end) te = resp['time_end'];

        //if (resp.sta) sta = resp['sta'];

        //if (resp.chan) chan = resp['chan'];

    //}}}
    }

    if ( ! original_ts ) original_ts = ts;

    if ( ! original_te ) original_te = te;

    // Show plots and hide Controls
    closeSubnav();
    $('#wforms').removeClass('ui-helper-hidden');

    //
    // If we don't have traces defined, get them from server...
    //
    if ( traces.length == undefined ) {
    //{{{
        var sta_string = '.*';
        for (var i in sta ) {
            sta_string = (sta_string == '.*') ? sta[i] : sta_string+'-'+sta[i];
        }

        var chan_string = '.*';
        for (var i in chan ) {
            chan_string = (chan_string == '.*') ? chan[i] : chan_string+'-'+chan[i];
        }

        $.ajax({
            url: proxy + '/data/stations/' + sta_string + '/' + chan_string ,
            async: false,
            success: function(data) { traces = data; }
        });
    //}}}
    };

    //
    // Build each plot wrapper in order
    //
    buildWrappers();

    // Set max and min for plots
    if (ts) flot_ops.xaxis.min = ts*1000;
    if (te) flot_ops.xaxis.max = te*1000;

    if (type == 'coverage') {
    //{{{
        var sta_string = '.*';
        for (var i in sta ) {
            sta_string = (sta_string == '.*') ? sta[i] : sta_string+'-'+sta[i];
        }
        var chan_string = '.*';
        for (var i in chan ) {
            chan_string = (chan_string == '.*') ? chan[i] : chan_string+'-'+chan[i];
        }

        var url = proxy + '/data/coverage/' + sta_string + '/' + chan_string ;

        url += ( ts ) ? '/'+ts : '/-'; 

        url += ( te ) ? '/'+te : '/-'; 

        // Just 1 ajax call for all coverage data 
        // since all comes from the wfdisc table.
        activeQueries += 1; 
        $.ajax({ 
            url:url, 
            success: function(data){
            //{{{
                if (data['error']) {
                    errorResponse('buildWrappers(): ',data['error']);
                }
                sta = data['sta'];
                chan = data['chan'];

                // Coverage could be called without times... need update
                if (data['time_start']) ts = data['time_start'];
                if (data['time_end']) te = data['time_end'];

                for (var mysta in traces ) {
                    for (var k in traces[mysta] ) {
                        mychan = traces[mysta][k];

                        //alert('list: ['+mysta+':'+mychan+']');

                        var d = new Object();
                        d[mysta] = new Object();
                        d[mysta][mychan] = {};

                        if (typeof(data[mysta]) == "undefined" ) { 
                            plotData(d);
                        } else if (typeof(data[mysta][mychan]) == "undefined" ) { 
                            plotData(d);
                        } else{
                            d[mysta][mychan] = {'format':'coverage','data':data[mysta][mychan]['data']};
                            plotData(d);
                        }

                    }
                }
            //}}}
            }
        });
    //}}}
    } else if (type == 'waveform'){
    //{{{
        for (var mysta in traces ) {
            for (var k in traces[mysta] ) {
                mychan = traces[mysta][k];

                var url = proxy + '/data/wf/' + mysta + '/' + mychan ;

                url += ( ts ) ? '/'+ts : '/-'; 

                url += ( te ) ? '/'+te : '/-'; 

                url += ( filter ) ? '/'+filter : '/-'; 

                activeQueries += 1; 

                $.ajax({

                    url:url,
                    dataType:'json',
                    success: function(data) { plotData(data); }

                });

            };

        };

    //}}}
    } else {
    //{{{
        $('#wforms').addClass('ui-helper-hidden');
        openSubnav();
        errorResponse('setData(): ',' Problems detecting "type" for plot. Select (waveforms or coverage) in config panel');
        return;
    //}}}
    }

    closeWaitingDialog();
//}}}
}

function plotData(r_data){
//{{{

    for (var sta in r_data) {
        for (var chan in r_data[sta]) {

            var temp_flot_ops = flot_ops;
            var flot_data = [];
            var data = r_data[sta][chan];
            var name = sta + '_' + chan ;
            var wpr = name+"_wrapper";
            var plt = name+"_plot";
            var plot = $("<div>").attr("id", plt );
            var segtype = '-';
            var calib = 1;

            if (document.getElementById(wpr) == null) {
                errorResponse('plotData(): ','No wrapper div for ['+sta+':'+chan+']. Appending at bottom.');
                $("#wforms").append( $("<div>").attr("id",wpr ).attr("class","wrapper") );
            }

            $("#"+wpr).width( $('#name_path').width() );

            $("#"+wpr).empty();

            if ( type == 'coverage') { 
                $("#"+wpr).height( 50 );
            } else if (size == 'big') {
                $("#"+wpr).height( 200 );
            } else if (size == 'medium') {
                $("#"+wpr).height( 150 );
            } else {
                $("#"+wpr).height( 100 );
            }

            $("#"+wpr).append(plot);
            $("#"+plt).width( '100%' );
            $("#"+plt).height( '100%' );
            $("#"+plt).bind("plotselected", handleSelect);

            if ( ! ts && typeof(data['start']) != "undefined" ) ts = data['start'];
            if ( ! te && typeof(data['end']) != "undefined"   ) te = data['end'];
            if ( ! temp_flot_ops.xaxis.min ) temp_flot_ops.xaxis.min   = ts*1000;
            if ( ! temp_flot_ops.xaxis.max ) temp_flot_ops.xaxis.max   = te*1000;

            if ( typeof(data['data']) == "undefined" ) { 
            //{{{  If we don't have ANY data...

                $("#"+wpr).height( 50 );

                var canvas = $.plot($("#"+plt),[], temp_flot_ops);
                var arrDiv = $("<div>").css(NameCss);

                arrDiv.css({ color:text_color, left:'30%', top:'5%'});

                arrDiv.append('No data in time segment: ('+ts+','+te+').');

                $("#"+plt).append(arrDiv);

            //}}}
            } else if ( data['format'] == 'coverage') { 
            //{{{  Here we are plotting coverage bars

                $.each( data['data'], function(i,arr) {

                    var start_time = parseFloat(arr[0],10) *1000;
                    var end_time   = parseFloat(arr[1],10) *1000;
                    flot_data.push([start_time,1,end_time]);

                });

                // Set FLOT options
                // for coverage
                temp_flot_ops.yaxis.ticks = 0;
                temp_flot_ops.yaxis.min   = 1;
                temp_flot_ops.yaxis.max   = 2;
                temp_flot_ops.bars = {
                        show:true,
                        horizontal:true,
                        barWidth:1,
                        fill:true,
                        fillColor:data_color
                };

                temp_flot_ops.bars = {show:true,barWidth:0,align:'center'};
                temp_flot_ops.points  = {show:false};
                temp_flot_ops.lines = {show:false};

                var canvas = $.plot($("#"+plt),[ flot_data ], temp_flot_ops);

            //}}}
            } else if( data['format'] == 'bins' ) {
            //{{{  Plot bins

                if ( typeof(data['metadata']['segtype']) != "undefined" ) { 
                    var segtype = data['metadata']['segtype'];
                }

                if ( typeof(data['metadata']['calib']) != "undefined" ) { 
                    var calib = data['metadata']['calib'];
                    if ( calib == 0 || isNaN(calib)  ){ calib = 1; }
                }


                if ( typeof(datatypes[segtype]) != "undefined") {

                    if (segtype == 'A' ) {

                        if (acceleration == 'G') {
                            segtype = '(A) => acceleration (G)';
                            // "1 g = 9.80665 m/s2" 
                            calib = 1/9806;
                        }
                        else {
                            segtype = '(A) => ' + datatypes[segtype];
                        }
                    }
                    else {
                        segtype = '(' + segtype + ') => ' + datatypes[segtype];
                    }
                }

                for ( var i=0, len=data['data'].length; i<len; ++i ){
                    temp_data = data['data'][i];
                    if (temp_data[1] == temp_data[2]) { temp_data[2] += .1; }
                    flot_data[i] =  [temp_data[0]*1000,temp_data[2]*calib,temp_data[1]*calib];
                }

                temp_flot_ops.bars = {show:true,barWidth:0,align:'center'};
                temp_flot_ops.points  = {show:false};
                temp_flot_ops.lines = {show:false};

                var canvas = $.plot($("#"+plt),[ flot_data ], temp_flot_ops);

                $('#'+plt).append($("<div>").css(calibCss).append('[ calib:'+calib+',  segtype:'+segtype+' ]'));
            //}}}
            } else if( data['format'] == 'lines' ) {
            //{{{  Plot lines
                //alert('Plot data:' + plt );

                if ( typeof(data['metadata']['segtype']) != "undefined" ) { 
                    var segtype = data['metadata']['segtype'];
                }

                if ( typeof(data['metadata']['calib']) != "undefined" ) { 
                    var calib = data['metadata']['calib'];
                    if ( calib == 0 || isNaN(calib)  ){ calib = 1; }
                }

                if ( typeof(datatypes[segtype]) != "undefined") {
                    if (segtype == 'A' ) {

                        if (acceleration == 'G') {
                            segtype = '(A) => acceleration (G)';
                            // "1 g = 9.80665 m/s2" 
                            calib = 1/9806;
                        }
                        else { segtype = '(A) => ' + datatypes[segtype]; }
                    }
                    else {
                        segtype = '(' + segtype + ') => ' + datatypes[segtype];
                    }
                }

                for ( var i=0, len=data['data'].length; i<len; ++i ){
                    temp_data = data['data'][i];
                    flot_data[i] =  [temp_data[0]*1000,temp_data[1]*calib];
                }

                if ( show_points ) 
                    temp_flot_ops.points  = {show:true,lineWidth:1,shadowSize:0};
                else
                    temp_flot_ops.points  = {show:false};
                temp_flot_ops.lines = {show:true,lineWidth:1,shadowSize:0};
                temp_flot_ops.bars = {show:false};

                var canvas = $.plot($("#"+plt),[ flot_data ], temp_flot_ops);

                $('#'+plt).append($("<div>").css(calibCss).append('[ calib:'+calib+',  segtype:'+segtype+' ]'));
            //}}}
            } else {
            //{{{  If we don't have ANY data...

                errorResponse('plotData(): ','Error in json object for ['+sta+':'+chan+']');

                $("#"+wpr).height( 50 );

                var canvas = $.plot($("#"+plt),[], temp_flot_ops);
                var arrDiv = $("<div>").css(NameCss);

                arrDiv.css({ color:text_color, left:'30%', top:'5%'});

                arrDiv.append('Error in "format" of data.');

                $("#"+plt).append(arrDiv);

            //}}}
            }

            $(".tickLabel").css({'font-size':'5px'});

            $(".tickLabel").each(function(i,ele) {
                ele = $(ele);
                if (ele.css("text-align") == "center") { //x-axis
                    ele.css("bottom", '8%'); //move them up over graph
                    ele.css("top", ''); //move them up over graph
                } else {  //y-axis
                    ele.css("left", '1%'); //move them right over graph
                }
            });

            chan_plot_obj[name] = canvas;

            $('#'+plt).append( $("<div>").html(name).css(NameCss) );
            $('#'+plt).append($("<div>").attr("id","remove_"+name).css(IconCss).attr("class","icons ui-state-dfault ui-corner-all").append("<span class='ui-icon ui-icon-close'></span>"));

            $(function() {
                $("#remove_"+name) .click(function() {
                    $("#"+wpr).remove();
                    delete traces[sta][chan];
                })
                .mouseenter(function() {
                    $(this).addClass('ui-state-hover');
                })
                .mouseleave(function() {
                    $(this).removeClass("ui-state-hover");
                });
            });
        }
    }

    activeQueries -= 1; 


//}}}
}

function setPhases(){
//{{{
    if (! show_phases ) return; 
    if (! ts || ! te) return;
    $.ajax({
        url: proxy + "/data/events/"+ts+"/"+te,
        success: function(data) {
            if (typeof(data) == "undefined" ) { return; }
            if (data == "null" ) { return; }
            if (! data ) { return; }
            $.each(data, function(sta_chan,p){

                var pt = $('#' + sta_chan + '_plot'); 

                if ( pt.length != 0){

                    $.each(p, function(phaseTime,phaseFlag){

                        var plot_obj = chan_plot_obj[sta_chan]; 

                        var o = plot_obj.pointOffset( { x:(phaseTime*1000), y:1000 } ) ;

                        var flagTop = plot_obj.getPlotOffset() ;

                        var flagCss = arrivalFlagCss;

                        flagCss['left'] = o.left + "px" ;
                        flagCss['top'] = flagTop.top + "px" ;

                        var flagTail = arrivalTailCss;
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

