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
var page = null;
var last_page = null;
var load_all = false;

var filter = 'None';
var calibrate = true;
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

// Set data conversion table
//{{{
datatypes = {
    'A': 'accel (Nm/sec/sec)',
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
    'c': 'dimensionless integer(counts)',
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
            load_all = true;
            TO = setTimeout('setData();', 2000);
            waitingDialog("Waveform Explorer:", "Resize detected. Refresh screen in 2 secs.");
        }
    });
    //}}} Automatic canvas resize

    build_dialog_boxes();

    waitingDialog("Waveform Explorer:", "Initializing client.");

    //  Setup AJAX defaults
    $.ajaxSetup({
        type: 'get',
        dataType: 'json',
        timeout: 30000,
        error:errorResponse
    });

    getCookie();

    $('#load_next').live('click', function() { page += 1; setData(); });

    $('#link').live('click', function() { makeLink(); });

    $('#clean').live('click', function() { $(".remove").remove(); });

    $('#home').live('click', function() {
        //{{{
        closeSubnav();

        $('#list').empty();
        $('#event_list').empty();
        $('#wforms').addClass('ui-helper-hidden');
        $('#wforms').empty();

        openSubnav();
        //}}}
    });

    $('#openconfig').live('click', function() {
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

    $('#openhelp').live('click', function() {
    //{{{
        $("#helppanel").dialog('option', 'title','HELP:'); 
        $("#helppanel").dialog('open'); 
    //}}}
    });

    $('#openlog').live('click', function() {
    //{{{
        $("#openlog").removeClass('ui-state-error');
        $("#logpanel").dialog('option', 'title','LOG:'); 
        $("#logpanel").dialog('open'); 
    //}}}
    });

    $('#load_events').live('click', function() {
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

    $('#clear').live('click', function() {
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

    $('#plot').live('click', function() {
        //{{{

        sta = ( $('#station_string').val() ) ? $("#station_string").val() : '.*';
        chan = ( $('#channel_string').val() ) ? $("#channel_string").val() : '.*';

        ts = ( $('#start_time').val() > 0 ) ? $("#start_time").val()*1000 : null;
        te = ( $('#end_time').val()  > 0) ? $("#end_time").val()*1000 : null;

        ts = parseInt(ts);
        te = parseInt(te);

        $("#logpanel").append('<p>Plot['+sta+'] ['+chan+'] ['+ts+'] ['+te+']</p>'); 

        $('#list').empty();
        $('#event_list').empty();
        $('#wforms').empty();
        closeSubnav();

        setData();

        //}}}
    });

    $('#load_stas').live('click', function() {
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

    $('#load_chans').live('click', function() {
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

    $('#remove_error').live('click', function() {
        $("#errors p").remove();
        $('#errors').addClass('ui-helper-hidden');
    })
    $('#remove_error').mouseenter(function() {
        $(this).addClass('ui-state-hover');
    })
    $('#remove_error').mouseleave(function() {
        $(this).removeClass("ui-state-hover");
    });
    

    varSet();

    keyBinds();

    $("button, input:submit, input:checkbox").button();

    $("#logpanel").append('<p>Done initializing server.</p>'); 

    closeWaitingDialog();

    // }}} Set defaults
}

// For App GUI
function openSubnav() {
    // {{{ open subnav div

    waitingDialog("Waveform Explorer:", "Open Control Window.");

    //{{{ Build DATEPICKERS

    // Build DATEPICKER
    $(".pickdate").datepicker({
        dateFormat: '@',
        beforeShow: function() { 

            if ( $(this).val() > 0 ) $(this).val($(this).val()*1000);  
            return {};

        },
        beforeShowDay: function(test_date) { 

            //diff = test_date.getTimezoneOffset();

            var found = true;

            //$.each(dates_allowed, function(key,value) {

            //    var option = new Date((value + (diff*60)) * 1000 );

            //    if (test_date.getTime() == option.getTime()) { found = true; }

            //});

            return found ? [true,'','Valid'] : [false,'','Not valid.']; 

        },
        onSelect: function(dateText, inst) {
            var old = $(".pickdate").not(this).val();

            if (this.id == "end_time")
                $(".pickdate").not(this).datepicker("option", 'maxDate', dateText );
            else
                $(".pickdate").not(this).datepicker("option", "minDate", dateText);

            if ( old ) 
                $(".pickdate").not(this).val( old );
            else 
                $(".pickdate").not(this).val( null );

            if (this.id == "end_time")
                $("#end_time").val( (dateText / 1000) + 86399 );
            else
                $("#start_time").val( dateText / 1000 );
        }
    });

    //
    // Set the max and min on datepicker to 
    // database max and min times on wfdisc
    //

    $.ajax({
        url: proxy + "/data/dates",
        success: function(json) {

            $("#logpanel").append('<p>Got dates for calendar.</p>'); 
            if ( json ) {
                var max = 0;
                var min = 0;

                min = json[0] * 1000;
                max = json[1] * 1000;

                var newDate = new Date(min);
                min += parseInt(newDate.getTimezoneOffset() * 60000);

                var newDate = new Date(max);
                max += parseInt(newDate.getTimezoneOffset() * 60000);

                $(".pickdate").datepicker("option", 'minDate', min+''); 
                $(".pickdate").datepicker("option", 'maxDate', max+''); 

                dates_allowed = json;

            }

        }
    });

    //}}}

    $("#station_string").val(sta);

    $("#channel_string").val(chan);

    temp = ( ts > 0 ) ? ts/1000 : null;
    $("#start_time").val(temp);
    temp = ( te > 0 ) ? te/1000 : null;
    $("#end_time").val(temp);

    $('#link').hide();
    $('#clean').hide();
    $('#load_bar').empty();
    $('#load_bar').addClass('ui-helper-hidden');
    $('#subnav').removeClass('ui-helper-hidden');

    closeWaitingDialog();

    // }}}
}
// For App GUI
function closeSubnav() {
    // {{{ close subnav div

    $('#subnav').addClass('ui-helper-hidden');

    // }}}
}

function makeLink(){
//{{{
    var path = String(window.location).split('/')
    var url = path[0] + '//' + path[2] + '/' + proxy + '/wf/' + sta + '/' + chan ;
    url += ( ts ) ? '/'+ts/1000 : '/-'; 
    url += ( te ) ? '/'+te/1000 : '/-'; 
    url += ( filter ) ? '/'+filter : '/-'; 
    url += ( calibrate ) ? '/True' : '/False'; 
    url += '/'+page ; 
    $("#logpanel").append('<p>makeLink()=>'+url+'</p>'); 
    alert(url);
//}}}
}

function getCookie() {
    //{{{ Get cookie values
        //
        // Look for cookie values and update elements
        //

        $("#logpanel").append('<p>Get COOKIE.</p>'); 

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

        $("#logpanel").append('<p>Set COOKIE.</p>'); 

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
        modal: true,
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
                        selection = selection + '|' + $( this ).text();
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
        modal: true,
        resizable: true,
        minWidth:  600, 
        //}}}
    }); // end of dialog 

    //Set loading dialog box
    $("#configpanel").dialog({ 
        //{{{
        autoOpen: false,
        modal: true,
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

                load_all = true;

                $( this ).dialog( "close" );

                if (! $("#subnav").is(":visible") ) { setData(); }

            },
            Cancel: function() {
                $( this ).dialog( "close" );
            }
        },
        //}}}
    }); // end of dialog 

    //Set log dialog box
    $("#logpanel").dialog({ 
        //{{{
        autoOpen: false,
        draggable: true, 
        resizable: true,
        buttons: {
            Clear: function() {
                $('#logpanel').empty();
            },
            OK: function() {
                $( this ).dialog( "close" );
            }
        }
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
        //dialogClass: "ui-state-error", 
        dialogClass: "ui-widget-overlay", 
        draggable: false, 
        modal:true,
        resizable: false,
        open: function(event, ui) { isPlotting = true; },
        close: function(event, ui) { isPlotting = false; }
        //}}}
    }); // end of dialog 

    //}}}
}

function waitingDialog(title,message) { 
    //{{{

    $("#logpanel").append('<p>'+message+'</p>'); 

    $("#loading").html( (message && '' != message) ? '<h1>'+message+'</h1>' : '<h1>Please wait...</h1>'); 
    $("#loading").dialog('option', 'title', (title && '' != title) ? title : 'Loading'); 
    $("#loading").dialog('open'); 

    //}}}
}

function closeWaitingDialog() { 
    //{{{

    if (activeQueries == 0) {
        if (! $('#wforms').hasClass("ui-helper-hidden") ) setPhases();
        $("#loading").dialog('close'); 
        $("#loading").empty(); 
    }

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
            //if (e.keyCode == '38') {
            //    // Up key
            //    e.preventDefault();
            //} else if (e.keyCode == '40') {
            //    // Down key
            //    e.preventDefault();
            //} else if (e.keyCode == '37') {
            //    // Left key
            //    e.preventDefault();
            //} else if (e.keyCode == '39') {
            //    // Right key
            //    e.preventDefault();
            //} else if (e.keyCode == '82') {
            //    // r for reset plot
            //    e.preventDefault();
            //} else if(e.which == 16) {
            if(e.which == 16) {
                // Shift key
                isShiftPressed = true;
            }
        });

        $(document).keyup(function(e) {
            //if (e.keyCode == '38') {
            //    // Up key
            //    e.preventDefault();
            //    shiftPlot('I');
            //} else if (e.keyCode == '40') {
            //    // Down key
            //    e.preventDefault();
            //    shiftPlot('O');
            //} else if (e.keyCode == '37') {
            //    // Left key
            //    e.preventDefault();
            //    shiftPlot('L');
            //} else if (e.keyCode == '39') {
            //    // Right key
            //    e.preventDefault();
            //    shiftPlot('R');
            //} else if (e.keyCode == '82') {
            //    // r for reset plot
            //    e.preventDefault();
            //    location.reload(true);
            //} else if(e.which == 16) {
            if(e.which == 16) {
                // Shift key
                isShiftPressed = false;
            }
        });

    // }}} Set bindings for keys
}

function varSet(){
// {{{ Set vars for plots

    // Function to produce tick labels for X axis
    x_formatter =  function (val, axis) { return convertTime(val); };

    // Function to produce tick labels for X axis
    y_formatter =  function (val, axis) {
        //{{{
        var range = Math.abs(axis.max - axis.min)

        if (val == 0) {
            return 0
        } 

        if (Math.abs(val) < 0.001) {
            return val.toFixed(4);
        }

        if (Math.abs(val) < 0.1) {
            return val.toFixed(2);
        }

        if (Math.abs(val) < 1) {
            return val.toFixed(1);
        }

        if (range < 100) {
            return val.toPrecision(3);
        }
        if (range < 1000) {
            return val.toPrecision(4);
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
        //grid: {hoverable:false,clickable:false, borderColor:tick_color, color:tick_color, tickColor:tick_color, backgroundColor:canvasBgColor},
        grid: {hoverable:false,clickable:false, borderColor:tick_color, color:text_color, tickColor:tick_color, backgroundColor:canvasBgColor},
        xaxis: {tickFormatter:x_formatter, ticks:4, mode:"time", timeformat:"%y-%m-%d %H:%M:%S UTC",labelWidth:200,labelHeight:0},
        //yaxis: {tickFormatter:y_formatter, ticks:3, min:null, max:null ,labelWidth:0,labelHeight:0},
        yaxis: {ticks:3, min:null, max:null ,labelWidth:0,labelHeight:0},
        points: {show:false},
        bars:  {show:false},
        lines: {show:false}
    };


    // For the text on the screen.
    NameCss = { color:text_color, 'font-size':'20px', position:'absolute', left:'10%', top:'8%'};

    // For the text on the screen.
    calibCss = { color:text_color, 'font-size':'15px', position:'absolute', right:'5%', top:'8%'};

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

    $("#logpanel").append('<p>ERROR: '+x+': '+e+'</p>'); 

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

        delta = parseInt( pos.xaxis.from, 10 ) - ts ;

        ts -= delta;

        delta = te - parseInt( pos.xaxis.to, 10 );

        te += delta;

        if  ( ts < original_ts || te > original_te )
            alert('Cannot zoom-out more than original query!');

        if (ts < original_ts) { ts = original_ts; }
        if (te > original_te) { te = original_te; }

    }
    else { 

        ts = parseInt( pos.xaxis.from, 10 ) ;
        te = parseInt( pos.xaxis.to, 10 ) ;

    }

    load_all = true;
    setData();

    // }}} Selection zoom functionality
}

function convertTime(time){
//{{{
        var newDate = new Date(time);

        var diff = newDate.getTimezoneOffset();

        if ( timezone == "local" ) {
            var lbl = '(UTC + ' + (diff/60)+')';
        }
        else {
            time += (newDate.getTimezoneOffset() * 60000);
            newDate = new Date(time);
            var lbl = 'UTC'
        }



        return newDate.getFullYear()+'-'+(newDate.getMonth()+1)+'-'+newDate.getDate()+' '+newDate.getHours()+':'+newDate.getMinutes()+':'+newDate.getSeconds()+' '+lbl
//}}}
}

function setData(resp) {
//{{{
    waitingDialog("Waveform Explorer:", "Waiting for data from server.");

    getCookie();

    // If resp defined... 
    // update globals
    if ( resp ) {
    //{{{

        if (resp.error) {
            errorResponse('setData(): ',resp['error']);
            closeWaitingDialog();
            return;
        }

        if (resp.sta) sta = resp['sta'];

        if (resp.chan) chan = resp['chan'];

        if (resp.time_start) ts = resp['time_start']*1000;

        if (resp.time_end) te = resp['time_end']*1000;

        if (resp.filter) filter = resp['filter'];

        if (resp.calib) calibrate = resp['calib'];

        if (resp.page) page = resp['page'];

        if ( (parseInt(page) > 0) ? parseInt(page) : 0 ) {
            last_page = parseInt(page);
            load_all = true;
        } else {
            page = 0;
        }

        ts = parseInt(ts);
        te = parseInt(te);

    //}}}
    }

    $("#logpanel").append('<p>Get: ['+sta+'] ['+chan+'] ['+ts+'] ['+te+']</p>'); 

    // Set max time window
    // This will prevent the user
    // to zoom-out away from this 
    // segment later.
    if ( ! original_ts ) original_ts = ts;
    if ( ! original_te ) original_te = te;


    // Show plots and hide Controls
    closeSubnav();
    $('#wforms').removeClass('ui-helper-hidden');
    $('#link').show();
    $('#clean').show();

    //
    // Get the data... 
    //  coverage and waveforms 
    //  now are combined...
    sta = (sta) ? sta : '.*';
    chan = (chan) ? chan : '.*';

    // Page to load
    page = (parseInt(page) > 0) ? parseInt(page) : 1;
    last_page = (parseInt(last_page) > 0) ? parseInt(last_page) : 1;

    //if ( page > 1) page += 1;

    if (page > last_page) page = last_page;

    if (load_all) 
        var first_page = 1;
    else
        var first_page = page;

    load_all = false;

    for( i=first_page;i<=page;i++) {

        var url = proxy ;

        if ( type == 'coverage')
            url += '/data/coverage/' + sta + '/' + chan ;
        else
            url += '/data/wf/' + sta + '/' + chan ;

        url += ( ts ) ? '/'+ts/1000 : '/-'; 

        url += ( te ) ? '/'+te/1000 : '/-'; 

        url += ( filter ) ? '/'+filter : '/-'; 

        url += ( calibrate ) ? '/True' : '/False'; 

        url += '/'+i ; 

        $("#logpanel").append('<p>AJAX: ['+url+']</p>'); 
        //waitingDialog("Waveform Explorer:", '<p>Query: ['+url+']</p>');

        activeQueries += 1; 

        $.ajax({ 
            url:url, 
            error:function(error) { 
                errorResponse('Query(): ['+url+'] ','Error: '+error); 
                activeQueries -= 1; 
            },
            success: function(data){
                plotData(data);
                closeWaitingDialog();
            }
        });

    }


//}}}
}

function plotData(r_data){
//{{{

    if ( ! r_data ) errorResponse('plotData(): ','ERROR in returned object from server!');

    var flot_data = [];
    var temp_flot_ops = flot_ops;
    var calib = 'false';
    var filter = 'none';
    // "1 g = 9.80665 m/s2" 
    var conv = 1/9806.65;

    if ( typeof(r_data['page']) != "undefined" ){ 
        if ( parseInt(r_data['page']) > page ) page = r_data['page'];
    }

    if ( typeof(r_data['last_page']) != "undefined"   ) last_page = r_data['last_page'];
    if ( typeof(r_data['time']) != "undefined" ) ts = r_data['time'];
    if ( typeof(r_data['endtime']) != "undefined"   ) te = r_data['endtime'];
    if ( ts ) temp_flot_ops.xaxis.min   = ts;
    if ( te ) temp_flot_ops.xaxis.max   = te;

    if ( typeof(r_data['calib']) != "undefined" ) calib = r_data['calib'];

    if ( typeof(r_data['filter']) != "undefined" ) filter = r_data['filter'];

    $('#load_bar').hide();
    $('#load_bar').empty();

    if ( page < last_page ) {
        $("#load_bar").html( "<p>Page " + page + " of " + last_page + "       <button id=load_next>Load Next</div></p>" );
        $('#load_bar').show();
    }

    for (var sta in r_data) {
        if ( sta == 'page') continue; 
        if ( sta == 'last_page') continue; 
        if ( sta == 'time' ) continue;
        if ( sta == 'endtime' ) continue;
        if ( sta == 'filter' ) continue;
        if ( sta == 'calib' ) continue;

        for (var chan in r_data[sta]) {

            //$("#loading").html('<p>Plotting: '+sta+'-'+chan+'</p>'+$("#loading").html()); 

            var name = sta + '_' + chan ;
            var wpr = name+"_wrapper";
            var plt = name+"_plot";
            var data = r_data[sta][chan];
            var plot = $("<div>").attr("id", plt );

            // If we have no data in object
            if ( typeof(data['ERROR']) != "undefined" ) { 
            //{{{
                $("#logpanel").append('<h3>'+name+':'+data['ERROR']+'</h3>'); 
                $("#openlog").addClass('ui-state-error');
                //var text = name + ' => ' + data['ERROR'] + ' [ ' + convertTime(ts) + ' - ' + convertTime(te) + ' ]';
                //$("#"+wpr).height( 20 );
                //$("#"+wpr).css( "border", "1px solid black" );
                //$("#"+wpr).css( "margin", "2px" );
                //$('#'+wpr).append( $("<div style='padding:1px'>" + text + "</div>") );
                //$("#"+wpr).addClass('remove');
                //$('#'+wpr).append($("<div>").css(IconCss).attr("class","remove icons ui-state-dfault ui-corner-all").append("<span class='ui-icon ui-icon-close'></span>")).append( $("<div style='padding:1px'>" + text + "</div>") );
                continue;
            //}}}
            } 
            // If we have no data in object
            if ( typeof(data['data']) == "undefined" ) { 
            //{{{
                $("#logpanel").append('<h3>'+name+': No data object in JSON</h3>'); 
                $("#openlog").addClass('ui-state-error');
                //var text = name + ' => No data object returned for: [ ' + convertTime(ts) + ' - ' + convertTime(te) + ' ]';
                //$("#"+wpr).height( 20 );
                //$("#"+wpr).css( "border", "1px solid black" );
                //$("#"+wpr).css( "margin", "2px" );
                //$('#'+wpr).append( $("<div style='padding:1px'>"+text+"</div>") );
                //$("#"+wpr).addClass('remove');
                //$('#'+wpr).append($("<div>").css(IconCss).attr("class","remove icons ui-state-dfault ui-corner-all").append("<span class='ui-icon ui-icon-close'></span>"));
                continue;
            //}}}
            } 

            if (document.getElementById(wpr) == null) {
                $("#wforms").append( $("<div>").attr("id",wpr ).attr("class","wrapper") );
            }

            if ( type == 'coverage') { 
                $("#"+wpr).height( 50 );
            } else if (size == 'big') {
                $("#"+wpr).height( 200 );
            } else if (size == 'medium') {
                $("#"+wpr).height( 150 );
            } else {
                $("#"+wpr).height( 100 );
            }

            $("#"+wpr).width( $('#name_path').width() );
            $("#"+wpr).empty();

            $("#"+wpr).append(plot);
            $("#"+plt).width( '100%' );
            $("#"+plt).height( '100%' );


            $("#"+plt).bind("plotselected", handleSelect);

            var segtype = '-';
            if ( typeof(data['segtype']) != "undefined" ) segtype = data['segtype'];

            // Setup for Coverage Bars
            if ( data['type'] == 'coverage') { 
            //{{{
                $.each( data['data'], function(i,arr) {

                    var start_time = parseFloat(arr[0],10);
                    var end_time   = parseFloat(arr[1],10);
                    flot_data.push([start_time,1,end_time]);

                });
                data['data'] = flot_data;

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

                //temp_flot_ops.bars = {show:true,barWidth:0,align:'center'};
                temp_flot_ops.points  = {show:false};
                temp_flot_ops.lines = {show:false};

            //}}}
            // Setup for bins
            } else if( data['format'] == 'bins' ) {
            //{{{
                temp_flot_ops.bars = {show:true,barWidth:0,align:'center'};
                temp_flot_ops.points  = {show:false};
                temp_flot_ops.lines = {show:true};

            } else if( data['format'] == 'lines' ) {

                if ( show_points ) 
                    temp_flot_ops.points  = {show:true,lineWidth:1,shadowSize:0};
                else
                    temp_flot_ops.points  = {show:false};

                temp_flot_ops.lines = {show:true,lineWidth:1,shadowSize:0};
                temp_flot_ops.bars = {show:false};

            }
            //}}}

            // Add units label
            if ( typeof(datatypes[segtype]) != "undefined") {
            //{{{
                // Convert to G if needed
                if (segtype == 'A' ) {

                    if (acceleration == 'G') {
                        segtype = 'accel (mG)';

                        flot_data = [];
                        for ( var i=0, len=data['data'].length; i<len; ++i ){
                            if ( typeof(data['data'][i][2]) != "undefined") 
                                flot_data[i] =  [data['data'][i][0],data['data'][i][1]*conv,data['data'][i][2]*conv];
                            else
                                flot_data[i] =  [data['data'][i][0],data['data'][i][1]*conv];
                        }

                        data['data'] = flot_data;
                    } else {
                        segtype = datatypes[segtype];
                    }
                } else {
                    segtype = datatypes[segtype];
                }
            //}}}
            }

            // PLot data
            var canvas = $.plot($("#"+plt),[ data['data'] ], temp_flot_ops);
            $('#'+plt).append( $("<div>").html(name).css(NameCss) );

            $(".tickLabel").css({'font-size':'15px'});

            $(".tickLabel").each(function(i,ele) {
                ele = $(ele);
                if (ele.css("text-align") == "center") { //x-axis
                    ele.css("bottom", '8%'); //move them up over graph
                    ele.css("top", ''); //move them up over graph
                } else {  //y-axis
                    ele.css("left", '1%'); //move them right over graph
                    ele.css("width", '50px');
                    ele.css("text-align",'left');
                }
            });

            chan_plot_obj[name] = canvas;

            if ( type == 'waveform') { 
                $('#'+plt).append($("<div>").css(calibCss).append('[ calib: "'+calib+'",  type: "'+segtype+'", filter: "'+filter+'" ]'));
                //$('#'+plt).append($("<div>").css(IconCss).attr("class","remove icons ui-state-dfault ui-corner-all").append("<span class='ui-icon ui-icon-close'></span>"));
            }
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
        url: proxy + "/data/events/"+ts/1000+"/"+te/1000,
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

//$('.remove').live('click', function() {
//    $(this).parentsUntil('#wforms').remove();
//});
//
//$(".remove").live("mouseover mouseout", function(event) {
//  if ( event.type == "mouseover" ) {
//    $(this).addClass('ui-state-hover');
//  } else {
//    $(this).removeClass("ui-state-hover");
//  }
//});
