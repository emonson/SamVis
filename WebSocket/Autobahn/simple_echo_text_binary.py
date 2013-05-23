<!DOCTYPE html>
<html>
   <head>
      <script type="text/javascript">
         var sock = null;
         var ellog = null;
         var r = null;

         window.onload = function() {

            ellog = document.getElementById('log');

            var wsuri;
            if (window.location.protocol === "file:") {
               wsuri = "ws://localhost:9000";
            } else {
               wsuri = "ws://" + window.location.hostname + ":9000";
            }

            if ("WebSocket" in window) {
               sock = new WebSocket(wsuri);
               // Testing binary
               sock.binaryType = 'arraybuffer';
            } else if ("MozWebSocket" in window) {
               sock = new MozWebSocket(wsuri);
            } else {
               log("Browser does not support WebSocket!");
               window.location = "http://autobahn.ws/unsupportedbrowser";
            }

            if (sock) {
               sock.onopen = function() {
                  log("Connected to " + wsuri);
               }

               sock.onclose = function(e) {
                  log("Connection closed (wasClean = " + e.wasClean + ", code = " + e.code + ", reason = '" + e.reason + "')");
                  sock = null;
               }

               sock.onmessage = function(e) {
               		var logdata;
                  if (typeof(e.data) == "string") {
                  	logdata = e.data;
                  } else {
                  	// NOTE: assuming Int16
                  	var arr = new Int16Array(e.data);
                  	console.log(e);
                  	logdata = arr2str(arr);
                  }
                  log("Got echo: " + logdata);
               }
            }
         };
         
         function arr2str(arr) {
						var str = "[ ";
						for (var ii = 0; ii < arr.length; ii++) {
							str += arr[ii].toString() + " ";
						}
						str += "]";
						
						return str
         };

         function send_txt() {
            var msg = document.getElementById('message').value;
            actually_send(msg);
         };
         function send_bin() {
            // Testing binary w/Int16
            var msg = new Int16Array([1000, 2, 3000, 4, -5, 23, -10000]);
            actually_send(msg);
         };
         function actually_send(msg) {
         	if (sock) {
               sock.send(msg);
               log("Sent: " + msg);
            } else {
               log("Not connected.");
            }
        	};


         function log(m) {
            ellog.innerHTML += m + '\n';
            ellog.scrollTop = ellog.scrollHeight;
         };
      </script>
   </head>
   <body>
      <h1>Autobahn WebSocket Echo Test</h1>
      <noscript>You must enable JavaScript</noscript>
      <form>
         <p>Message: <input id="message" type="text" size="50" maxlength="50" value="Hello, world!"></p>
      </form>
      <button onclick='send_txt();'>Send String Message</button>
      <button onclick='send_bin();'>Send Binary Message</button>
      <pre id="log" style="height: 20em; overflow-y: scroll; background-color: #faa;"></pre>
   </body>
</html>
