function getCookie() {
    //{{{ Get cookie values
        // Vars
        //PlotSelect.show_points = true;
        //PlotSelect.show_phases = true;
        //PlotSelect.timezone = 'UTC';
        //PlotSelect.type = 'waveform';
        //PlotSelect.color = 'def';
        //PlotSelect.ts = 0;
        //PlotSelect.te = 0;
        //PlotSelect.filter = 'none';
        //PlotSelect.stations = '';
        //PlotSelect.channels = '';

        //
        // Look for cookie values and update elements
        //
        if ($.cookie('dbwfserver_phases') == 'false'){
            $('#phases').removeAttr('checked');
            PlotSelect.show_phases  = false;
        } else if ($.cookie('dbwfserver_phases') == 'true'){
            $('#phases').attr('checked', true);
            PlotSelect.show_phases  = true;
        }

        if ($.cookie('dbwfserver_points') == 'false'){
            $('#points').removeAttr('checked');
            PlotSelect.show_points  = false;
        } else if ($.cookie('dbwfserver_points') == 'true'){
            $('#points').attr('checked', true);
            PlotSelect.show_points  = true;
        }

        $('#time_zone_wrapper').empty();
        if ($.cookie('dbwfserver_time_zone') ==  'local'){
            PlotSelect.timezone  = 'local';
            $('#time_zone_wrapper').html('<div id="time_zone"> <input type="radio" id="utc" name="timezone" value="UTC"/><label for="utc">UTC</label> <input type="radio" id="local" name="timezone" checked="checked" value="local"/><label for="local">Local</label></div>');
        } else {
            PlotSelect.timezone  = 'UTC';
            $('#time_zone_wrapper').html('<div id="time_zone"> <input type="radio" id="utc" checked="checked" name="timezone" value="UTC"/><label for="utc">UTC</label> <input type="radio" id="local" name="timezone" value="local"/><label for="local">Local</label></div>');
        }

        $("#plot_type_wrapper").empty();
        if ($.cookie('dbwfserver_type') == 'coverage'){
            PlotSelect.type  = 'coverage';
            $('#plot_type_wrapper').html('<div class="controls" id="plot_type"> <input type="radio" id="waveform" name="wf_type" value="waveform"/><label for="waveform">Waveforms</label> <input type="radio" id="coverage" checked="checked" name="wf_type" value="coverage"/><label for="coverage">Coverage</label></div>');
        } else {
            PlotSelect.type  = 'waveforms';
            $('#plot_type_wrapper').html('<div class="controls" id="plot_type"> <input type="radio" id="waveform" checked="checked" name="wf_type" value="waveform"/><label for="waveform">Waveforms</label> <input type="radio" id="coverage" name="wf_type" value="coverage"/><label for="coverage">Coverage</label></div>');
        }

        $("#acceleration").empty();
        if ($.cookie('dbwfserver_acceleration') == 'SI'){
            PlotSelect.acceleration  = 'SI';
            $('#acceleration').html('<div class="controls" id="acceleration_type"> <input type="radio" id="G" name="accel_type" value="G"/><label for="G">G</label> <input type="radio" id="SI" checked="checked" name="accel_type" value="SI"/><label for="SI">nm/sec/sec</label></div>');
        } else {
            PlotSelect.acceleration  = 'G';
            $('#acceleration').html('<div class="controls" id="acceleration_type"> <input type="radio" id="G" checked="checked" name="accel_type" value="G"/><label for="G">G</label> <input type="radio" id="SI" name="accel_type" value="SI"/><label for="SI">nm/sec/sec</label></div>');
        }

        if ($.cookie('dbwfserver_color')){
            PlotSelect.color  =  $.cookie('dbwfserver_color');
            $('#cs').val($.cookie('dbwfserver_color'));
        } else {
            PlotSelect.color  =  'def';
            $('#cs').val('def');
        }

        if ($.cookie('dbwfserver_filter')){
            $('#filter').val($.cookie('dbwfserver_filter'));
            PlotSelect.filter  =  $.cookie('dbwfserver_filter');
        } else {
            PlotSelect.filter  =  'none';
            $('#filter').val('none');
        }

        $("button, input:submit, input:checkbox").button('refresh');
        $("#time_zone").buttonset();
        $("#plot_type").buttonset();
        $("#acceleration").buttonset();
    //}}} Get cookie values
}

function setCookie() {
    //{{{ Set cookie
        // Vars
        //PlotSelect.show_points = true;
        //PlotSelect.show_phases = true;
        //PlotSelect.timezone = 'UTC';
        //PlotSelect.type = 'waveform';
        //PlotSelect.color = 'def';
        //PlotSelect.ts = 0;
        //PlotSelect.te = 0;
        //PlotSelect.filter = 'none';
        //PlotSelect.stations = '';
        //PlotSelect.channels = '';

        // Set COOKIE global options
        COOKIE_OPTS = { path: '/', expiresAt: 99 };

        $.cookie('dbwfserver_time_zone', $("input[name='timezone']:checked").val(), COOKIE_OPTS);
        PlotSelect.timezone = $("input[name='timezone']:checked").val();

        $.cookie('dbwfserver_type', $("input[name='wf_type']:checked").val(), COOKIE_OPTS);
        PlotSelect.type = $("input[name='wf_type']:checked").val();

        $.cookie('dbwfserver_acceleration', $("input[name='accel_type']:checked").val(), COOKIE_OPTS);
        PlotSelect.type = $("input[name='accel_type']:checked").val();

        $.cookie('dbwfserver_color', $("#cs").val(), COOKIE_OPTS);
        PlotSelect.color = $("#cs").val();

        $.cookie('dbwfserver_filter', $("#filter").val(), COOKIE_OPTS);
        PlotSelect.filter = $("#filter").val();

        if ( $('#phases').is(':checked') ) {
            $.cookie('dbwfserver_phases', 'true', COOKIE_OPTS);
            PlotSelect.show_phases = true;
        } else { 
            $.cookie('dbwfserver_phases', 'false', COOKIE_OPTS);
            PlotSelect.show_phases = false;
        }

        if ( $('#points').is(':checked') ) {
            $.cookie('dbwfserver_points', 'true', COOKIE_OPTS);
            PlotSelect.show_points = true;
        } else { 
            $.cookie('dbwfserver_points', 'false', COOKIE_OPTS);
            PlotSelect.show_points = false;
        }

        // Not in use...
        //$.cookie('dbwfserver_stime', $("#start_time").val(), COOKIE_OPTS);

        //$.cookie('dbwfserver_etime', $("#end_time").val(), COOKIE_OPTS);

        //$.cookie('dbwfserver_sta', $("#station_string").val(), COOKIE_OPTS);

        //$.cookie('dbwfserver_chan', $("#channel_string").val(), COOKIE_OPTS);

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

                if ( selection ) {
                    target.val(selection);
                }

                $( this ).dialog( "close" );

            },
            Cancel: function() {
                $( this ).dialog( "close" );
            }
        }
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

                setCookie();

                if( $("#phases").attr('checked') ) { 
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

                PlotSelect.plotVarSet();

                $( this ).dialog( "close" );

                if (! $("#subnavcontent").is(":visible") ) { PlotSelect.setData(); }

            },
            Cancel: function() {
                $( this ).dialog( "close" );
                getCookie();
            }
        },
        close: function() { 
            getCookie(); 
        },
        open: function() { 
            getCookie(); 
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
        //}}}
    }); // end of dialog 

    //}}}
}

function waitingDialog(waiting) { 
    //{{{

    //<div class="ui-widget">
    //<div class="ui-state-error ui-corner-all" style="padding: 0 .7em;"> 
    //<p><span class="ui-icon ui-icon-alert" style="float: left; margin-right: .3em;"></span> 
    //<strong>Alert:</strong> Sample ui-state-error style.</p>

    //</div>
    //</div>

    $("#loading").html(waiting.message && '' != waiting.message ? waiting.message : 'Please wait...'); 
    //$("#loading").dialog('option', 'title', waiting.title && '' != waiting.title ? waiting.title : 'Loading').prev().addClass('ui-state-error'); 
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

function set_jquery_ui_theme() { 
    //{{{

    $("button, input:submit, input:checkbox").button();
    $("#home").button();
    $("#openconfig").button();

    //}}}
}

function build_calendars() { 
    //{{{

    // DATEPICKER
    // get tuple for min and max dates in database
    var dates = $(".datepicker").datepicker({showOn: 'button',
                            buttonImage: 'static/images/calendar.gif',
                            buttonImageOnly: true,
                            dateFormat: '@',
                            beforeShowDay: function(test_date) { 

                                diff = test_date.getTimezoneOffset();

                                var found = true;

                                //$.each(PlotSelect.dates_allowed, function(key,value) {

                                //    var option = new Date((value + (diff*60)) * 1000 );

                                //    if (test_date.getTime() == option.getTime()) { found = true; }

                                //});

                                if (found) {
                                    return [true, '', 'Valid date'];
                                }
                                else {
                                    return [false, '', 'No data for this date'];
                                }
                            },
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
        url: "/data/dates",
        success: function(json) {

            if ( typeof(json) != "undefined" ) {

                var max = 0;
                var min = 999999999999;

                $.each(json, function(key,value) {

                    if ( value[0] < min) { min = value[0]; }
                    if ( value[1] > max) { max = value[1]; }

                });

                var diff = new Date().getTimezoneOffset();

                var first = String((min + (diff*60))*1000);

                var last = String((max + (diff*60))*1000);


                dates.datepicker("option", 'minDate', first); 
                dates.datepicker("option", 'maxDate', last);

                PlotSelect.dates_allowed = json;

            }

        }
    });


    //}}}
}

function set_click_responses() { 
    //{{{

    //  Open the help panel
    $("#help_open").click( function() {
        //{{{
        $("#helppanel").slideToggle("slow", function() {
            if( $(this).is(":hidden") ) {
                $("#help_open").html('Show Help');
            } else {
                $("#help_open").html('Hide Help');
            }    
        });  
        //}}}
    });  

    $('#home').click( function(){ $(location).attr('href','/'); });

    $('#openconfig').click( function(){ 
        $("#configpanel").dialog('option', 'title','Configuration:'); 
        $("#configpanel").dialog('open'); 
    });

    //  On subnav panel
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
        setCookie();

        url = '/wf/'+sta+'/'+chan+'/'+start+'/'+end;
        $(location).attr('href',url);
        //}}}
    });

    $('#load_stas').click( function($e){
    //{{{
        $e.preventDefault();
        $('#list').empty();
        $("#list").html("<ol></ol>");
        waitingDialog({title: "Waveform Explorer:", message: "Loading station list."});
        $.ajax({
            url: "/data/stations",
            success: function(json) {

                $.each(json.sort(), function(i,item){
                    $("#list ol").append('<li id="'+item+'" class="ui-state-default">'+item+'</li>');
                });

                $(function() {
                    $("#list").selectable();
                });
                closeWaitingDialog();
                $("#list").dialog('option', 'title','Select Stations:'); 
                $("#list").dialog('open'); 
            }
        });
        //}}}
    });

    $('#load_chans').click( function($e){
        //{{{
        $e.preventDefault();
        $('#list').empty();
        $("#list").html("<ol></ol>");
        $.ajax({
            url: "/data/channels",
            success: function(json) {
                $("#list").dialog('option', 'title','Select Channels:'); 
                $("#list").dialog('open'); 
                
                $.each(json.sort(), function(i,item){
                    $("#list ol").append('<li id="'+item+'" class="ui-state-default ui-selectee">'+item+'</li>');
                });

                $(function() {
                    $("#list").selectable();
                });
            }
        });
        //}}}
    });

    $('#load_events').click( function($e){
        //{{{
        $e.preventDefault();
        $('#list').empty();
        waitingDialog({title: "Waveform Explorer:", message: "Loading event list."});
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
                $("#event_list").append(subnavcontent);
                $("#event_list").show('slow');
                $("#event_list #evsTbl").tablesorter( {sortList: [[0,0], [1,0]]} );
                $('.add_events').click( function($e){
                    $e.preventDefault();
                    $("#event_list").hide('slow');
                    $('#event_list').empty();
                    time = $(this).attr("id");
                    if ( typeof(time) != "undefined" ) {
                        time /=  1000;
                    }
                    $("#start_time").val(time);
                });
                closeWaitingDialog();
            }
        });
        //}}}
        });
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

        PlotSelect.mode = 'full';

        PlotSelect.dates_allowed = [];

        PlotSelect.show_points = true;
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

        set_click_responses();
        set_jquery_ui_theme();
        build_calendars();

        // Get the values and update buttons
        getCookie();


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

    setupUI: function(resp) {

//{{{

    if ( typeof(resp) != "undefined" ) {
    //{{{

        if (typeof(resp.mode) != "undefined" ) {

            if (resp.mode == "simple") { 
                PlotSelect.mode = 'simple';
                $("#toppanel").hide()
                $("#title").hide()
                $("#subnav").hide()
                $("#name_path").hide()
                $("#control_bar").hide()

                PlotSelect.handleSelect = function() {};
                PlotSelect.shiftPlot = function() {};
                PlotSelect.flot_ops.selection = {mode:null}; 
            }
            else if (resp.mode == "limited") { 
                PlotSelect.mode = 'limited';
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

    },

    keyBinds: function(){

    // {{{ Set bindings for keys
        if (PlotSelect.mode == "simple") { return; }


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

            if (PlotSelect.mode == "limited") { 
                if (PlotSelect.ts < PlotSelect.original_ts) { PlotSelect.ts = PlotSelect.original_ts; }
                if (PlotSelect.te > PlotSelect.original_te) { PlotSelect.te = PlotSelect.original_te; }
            }

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
        //$("#loading").show();
        waitingDialog({});

        //
        // Get type
        //
        PlotSelect.type = $("input[name='wf_type']:checked").val();

        if (! PlotSelect.type) {
            alert('Problems detecting "type" for plot. Select (waveforms or coverage).');
        }

        // 
        // If resp defined... update globals
        //
        if ( resp ) {
        //{{{

            // PlotSelect is define globally for app
            if (resp['error']) {
                PlotSelect.errorResponse('parsererror',resp['error']);
            }

            if (resp.traces) {
                PlotSelect.traces = resp['traces'];
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
            //console.log(PlotSelect.sta);
            //console.log(PlotSelect.chan);
            //console.log(PlotSelect.traces);
            //console.log(PlotSelect.ts);
            //console.log(PlotSelect.te);
        //}}}
        }

        // Hide Controls
        $('#subnavcontent').hide('fast');
        // Show plots
        $("#wforms").show('fast');
        $("#tools").show('fast');


        if (PlotSelect.type == 'coverage') {
        //{{{
            PlotSelect.keyBinds();

            //
            // Build URL for query
            //
            //{{{
            var url = '/data/coverage'

            if (PlotSelect.sta) {
                url += '/' + PlotSelect.sta.join("+");
            } else { 
                url += '/.*';
            }

            if (PlotSelect.chan) {
                url += '/' + PlotSelect.chan.join("+");
            } else { 
                url += '/.*';
            }

            if (PlotSelect.ts) {
                url += '/' + PlotSelect.ts / 1000;
            } 

            if (PlotSelect.te) {
                url += '/' + PlotSelect.te / 1000;
            }
            //}}}

            // Just 1 ajax call for all coverage data 
            // since all comes from the wfdisc table.
            PlotSelect.activeQueries += 1; 
            $.ajax({ 
                url:url, 
                success: function(data){
                //{{{
                    //
                    // Update Globals
                    //
                    
                    if (data['error']) {
                        PlotSelect.errorResponse('parsererror',data['error']);
                    }
                    PlotSelect.sta = data['sta'];
                    PlotSelect.chan = data['chan'];

                    // Coverage could be called without times... need update
                    PlotSelect.ts = data['time_start'] * 1000;
                    PlotSelect.te = data['time_end'] * 1000;

                    // Set max and min for plots
                    PlotSelect.flot_ops.xaxis.min = PlotSelect.ts;
                    PlotSelect.flot_ops.xaxis.max = PlotSelect.te;
                    

                    $.each(data.sta.sort(), function(sta_iterator,mysta){

                        $.each(data.chan.sort(), function(chan_iterator,mychan){

                            var wpr = mysta + '_' + mychan + '_wrapper' ;

                            if ( $("#"+wpr).length == 0 ){
                                $("#wforms").append( $("<div>").attr("id",wpr ).attr("class","wrapper") );
                                $("#"+wpr).width( $(window).width() );
                            }

                            if (typeof(data[mysta][mychan]) != "undefined" ) { 
                                PlotSelect.plotData(mysta,mychan,data[mysta][mychan]);
                            }

                        });

                    });
                //}}}
                }
            });
            PlotSelect.activeQueries -= 1; 
        //}}}
        } else if (PlotSelect.type == 'waveform'){
        //{{{
            PlotSelect.keyBinds();

            // Sort Stations
            var s_stations = []
            $.each(PlotSelect.traces, function(mysta,mysta_object ){
                s_stations.push(mysta);
            });

            s_stations.sort();

            // Start loop of stations
            $.each(s_stations, function(ii,mysta){

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
                                if (typeof(data[mysta]) == "undefined" ) { 
                                    PlotSelect.activeQueries -= 1; 
                                    //PlotSelect.traces.mysta.mychan = 'False';
                                }
                                else if (typeof(data[mysta][mychan]) == "undefined" ) { 
                                    PlotSelect.activeQueries -= 1; 
                                    //PlotSelect.traces.mysta.mychan = 'False';
                                } else { 
                                    PlotSelect.plotData(mysta,mychan,data[mysta][mychan]);
                                }

                            },

                        });

                    }

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
        //}}}
        } else {
        //{{{
            // Show plots
            $("#wforms").hide('fast');
            $("#tools").hide('fast');
            // Hide Controls
            $('#subnavcontent').show('slow');
        //}}}
        }

        if ($("#phases").is(':checked') == true) { 
            $(".flag").show();
            $(".flagTail").show();
        }

        closeWaitingDialog();
//}}}

    },

    plotData: function(sta,chan,data){

//{{{

        var flot_data = [];
        var name = sta + '_' + chan ;
        var wpr = name+"_wrapper";
        var plt = name+"_plot";
        var wrapper = $("<div>").attr("id",wpr ).attr("class","wrapper");
        var plot = $("<div>").attr("id", plt );
        var segtype = '-';
        var calib = 1;
        PlotSelect.flot_ops.points = {show:false};
        PlotSelect.flot_ops.bars   = {show:false};
        PlotSelect.flot_ops.lines  = {show:false};


        //
        // If we don't have plot, then we don't have wrapper div. Build one
        //
        if ( $("#"+plt).length == 0 ){
            $("#"+wpr).append(plot);
            $("#"+plt).bind("plotselected", PlotSelect.handleSelect);
        }


        if ( typeof(data['data']) == "undefined" ) { 
        //{{{  If we don't have ANY data...
            $("#"+plt).attr("class", "plot_cov");

            var canvas = $.plot($("#"+plt),[], PlotSelect.flot_ops);

            var arrDiv = $("<div>").css(PlotSelect.NameCss);

            arrDiv.css({ color:PlotSelect.canvasLineColor, left:'30%', top:'5%'});

            arrDiv.append('No data in time segment: ('+PlotSelect.ts/1000+','+PlotSelect.te/1000+').');

            $("#"+plt).append(arrDiv);
        //}}}
        } else {
        //{{{ We have some data to plot...

            if ( typeof(data['format']) == "undefined" || data['format'] == 'coverage') { 
            //{{{  Here we are plotting coverage bars

                $.each( data['data'], function(i,arr) {

                    var start_time = parseFloat(arr[0],10) *1000;
                    var end_time   = parseFloat(arr[1],10) *1000;
                    flot_data.push([start_time,1,end_time]);

                });

                // Set FLOT options
                // for coverage
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
                    if ( temp_data[1] == temp_data[2] ) { 
                        flot_data[i] = [temp_data[0]*1000,temp_data[2]*calib]; 
                    } else { 
                        flot_data[i] = [temp_data[0]*1000,temp_data[2]*calib,temp_data[1]*calib]; 
                    }
                    //if (temp_data[1] == temp_data[2]) { temp_data[2] += .1; }
                    //flot_data[i] =  [temp_data[0]*1000,temp_data[2]*calib,temp_data[1]*calib];
                }

                // Set FLOT options
                // for bars
                PlotSelect.flot_ops.yaxis.ticks = 4;
                PlotSelect.flot_ops.xaxis.min   = PlotSelect.ts;
                PlotSelect.flot_ops.xaxis.max   = PlotSelect.te;
                PlotSelect.flot_ops.bars        = {show:true,barWidth:0,align:'center'};
                PlotSelect.flot_ops.lines       = {show:true,lineWidth:1,shadowSize:0};

                $("#"+plt).attr("class", "plot");

                var canvas = $.plot($("#"+plt),[ flot_data ], PlotSelect.flot_ops);

                var arrDiv = $("<div>").css(PlotSelect.calibCss).append('[ calib:'+calib+',  segtype:'+segtype+' ]');
                $('#'+plt).append(arrDiv);
            //}}}
            } else {
            //{{{  Plot lines

                if ( typeof(data['metadata']['segtype']) != "undefined" ) { 
                    var segtype = data['metadata']['segtype'];
                }

                if ( typeof(data['metadata']['calib']) != "undefined" ) { 
                    var calib = data['metadata']['calib'];
                    if ( calib == 0 || isNaN(calib)  ){ calib = 1; }
                }

                if ( typeof(PlotSelect.datatypes[segtype]) != "undefined") {
                    if (segtype == 'A' ) {

                        if (PlotSelect.acceleration == 'G') {
                            segtype = '(A) => acceleration (G)';
                            // "1 g = 9.80665 m/s2" 
                            calib = 1/9806;
                        }
                        else { segtype = '(A) => ' + PlotSelect.datatypes[segtype]; }
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
                    PlotSelect.flot_ops.points  = {show:true,lineWidth:1,shadowSize:0};
                } 
                PlotSelect.flot_ops.lines       = {show:true,lineWidth:1,shadowSize:0};
                PlotSelect.flot_ops.yaxis.ticks = 4;
                PlotSelect.flot_ops.yaxis.min   = null;
                PlotSelect.flot_ops.yaxis.max   = null;

                $("#"+plt).attr("class", "plot");

                var canvas = $.plot($("#"+plt),[ flot_data ], PlotSelect.flot_ops);

                var arrDiv = $("<div>").css(PlotSelect.calibCss).append('[ calib:'+calib+',  segtype:'+segtype+' ]');
                $('#'+plt).append(arrDiv);
            //}}}
            }

        //}}}
        }

        PlotSelect.chan_plot_obj[name] = canvas;

        var arrDiv = $("<div>").css(PlotSelect.NameCss).append(name);

        $('#'+plt).append(arrDiv);

        var arrDiv = $("<div>").attr("id","remove_"+name).css(PlotSelect.IconCss).attr("class","icons ui-state-dfault ui-corner-all").append("<span class='ui-icon ui-icon-close'></span>");

        $('#'+plt).append(arrDiv);

        PlotSelect.activeQueries -= 1; 

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

    setPhases: function(start,end){

//{{{
        $.ajax({
            url:"/data/events/"+start+"/"+end,
            success: function(data) {
                if (typeof(data) == "undefined" ) { return; }
                if (data == "null" ) { return; }
                if (! data ) { return; }
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
