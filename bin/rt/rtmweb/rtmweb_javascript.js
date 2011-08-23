<script type="text/javascript">
    function getlog(proc){

        var new_id = proc + "_log";

        if ( document.getElementById(new_id) ) {
            // Remove log...
            document.getElementById(new_id).parentNode.removeChild(document.getElementById(new_id));
        }
        else {
            // AJAX query to server...
            xmlhttp =XMLHttpRequest();
            xmlhttp.open("GET","ajax/log?proc="+proc,false);
            xmlhttp.send();

            var _div = document.createElement("div");
            _div.id = new_id;
            _div.innerHTML = xmlhttp.responseText;
            document.getElementById(proc).appendChild(_div);
            var log_div = document.getElementById(new_id);
            log_div.style.backgroundColor = "white";
            log_div.style.margin = "5px";
            log_div.style.padding = "5px";
            log_div.style.border = "2px solid black";
        }
    }
    function cmd(proc){

        // AJAX query to server...
        xmlhttp =XMLHttpRequest();
        xmlhttp.open("GET","ajax/cmd?proc="+proc,false);
        xmlhttp.send();
        alert(xmlhttp.responseText);

    }
</script>
