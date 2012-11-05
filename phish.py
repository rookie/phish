#!/usr/bin/env python

import os, sys
import SimpleHTTPServer, SocketServer
import subprocess
import cgi


class ShellRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
	
	def do_GET(self):
		if self.path == '/favicon.ico':
			self.send_response(404)
		else:
			self.wfile.write(htmlfile)
	
	
	def do_POST(self):
		
		# Handle post variables
		ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
		if ctype == 'multipart/form-data':
			postvars = cgi.parse_multipart(self.rfile, pdict)
		elif ctype == 'application/x-www-form-urlencoded':
			length = int(self.headers.getheader('content-length'))
			postvars = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
		else:
			postvars = {}
			
		command = postvars['cmd'][0]
		
		if command.strip() == '':
			self.send_response(404)
			response = 'Error 404'
		elif command.startswith('cd'):
			if command.strip() == 'cd':
				command = 'cd ~'
			os.chdir(os.path.expanduser(command[2:].strip()))
			response = os.getcwd()
		else:
			proc = subprocess.Popen(command.strip(), shell = True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
			proc.wait()
			response = proc.communicate()[0]
		
		self.wfile.write('{}\n{}'.format(command, response))
	



class ReuseTCPServer(SocketServer.TCPServer):
	allow_reuse_address = True

	

def main():
	port = 8080
	if len(sys.argv) == 2:
		try:
			port = int(sys.argv[1])
		except ValueError:
			print "Invalid value for port number"
	httpd = ReuseTCPServer(("", port), ShellRequestHandler)
	print "Serving at port", port
	httpd.serve_forever()





# http://stackoverflow.com/questions/155188/trigger-a-button-click-with-javascript-on-the-enter-key-in-a-text-box
# http://stackoverflow.com/questions/1219860/javascript-jquery-html-encoding

htmlfile = '''
<!DOCTYPE html>
<html>
<head>
	<script>
	function getquerystring() {
		var form = document.forms['f1'];
		var word = form.word.value;
		form.word.value = "";
		qstr = escape(word);
		return qstr;
	}

	function searchKeyPress(e) {
		// look for window.event in case event isn't passed in
		e = e || window.event;
		if (e.keyCode == 13) {
			loadXMLDoc();
			e.returnValue=false;
			e.cancel=true;
		}else{
			//htmlresult = "<hr /><pre>&#36;&gt; " + e.keyCode + "</pre>"
			//document.getElementById("result").innerHTML = htmlresult + previous_results;
		}
	}
	
	function htmlEscape(str) {
		return String(str)
			.replace(/&/g, '&amp;')
			.replace(/"/g, '&quot;')
			.replace(/'/g, '&#39;')
			.replace(/</g, '&lt;')
			.replace(/>/g, '&gt;');
	}
	
	function loadXMLDoc(){
		var xmlhttp;
		if (window.XMLHttpRequest) {// code for IE7+, Firefox, Chrome, Opera, Safari
			xmlhttp=new XMLHttpRequest();
		} else {// code for IE6, IE5
			xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
		}
	
		xmlhttp.onreadystatechange=function() {
			if (xmlhttp.readyState==4 && xmlhttp.status==200) {
				previous_results = document.getElementById("result").innerHTML;
				htmlresult = "<hr /><pre><code>&#36;&gt; " + htmlEscape(xmlhttp.responseText) + "</code></pre>"
				document.getElementById("result").innerHTML = htmlresult + previous_results;
			}
		}
	
		xmlhttp.open("POST","/",true);
		xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
		xmlhttp.send("cmd="+getquerystring());
	}
</script>
</head>
<body>

<h2>The Python HTTP Insecure Shell</h2>

<form name="f1">
	<input name="word" type="text" id="commandTest" onkeypress="searchKeyPress(event)" />
</form>

<div id="result"></div>


</body>
</html>
'''




if __name__ == '__main__':
	main()



