#!/usr/bin/env python3

import os
import posixpath
import http.server
import urllib.request, urllib.parse, urllib.error
import html
import shutil
import mimetypes
import re
from io import BytesIO

css = """
<style>
body{background-color:#262A33;text-align:center;color:#fff;font-family:"Helvetica Neue", Helvetica, Arial, sans-serif}.item{background-color:#3E4149;margin-top:10px;margin-bottom:10px;width:60%;padding:15px 15px 15px 15px;list-style-type:none;border:none;border-radius:7px}a{color:#fff}.header{color:#fff;width:100%;padding-top:10px;padding-bottom:10px}.title{font-size:25px;font-weight:bold}.headerline{width:50%;margin-bottom:20px}hr{width:50%}.upload{padding:15px 30px 15px 30px;border:none;border-radius:7px;font-weight:700;color:#fff;cursor:pointer;background-color:#5CBC7C}.upload:active{background:#9fa1a0}label.label input[type="file"]{display:none}.label{cursor:pointer;border-radius:7px;font-weight:700;border:none;font-size:14px;padding:14px 30px 15px 30px;background:#15b0e9;color:#fff;margin-right:10px}.label:active{background:#9fa1a0}.label:invalid+span{color:#000000}.label:valid+span{color:#ffffff}.fileicon{width:25px;margin-right:10px;margin-bottom:-5px}footer{margin-top:20px;opacity:50%}.success{font-size:large;color:#5CBC7C}.failure{font-size:large;color:rgb(155, 42, 42)}.backbutton{font-weight:700;padding:15px 30px 15px 30px;background-color:#3E4149;text-decoration:none;border-radius:7px}
</style>
"""

def geticon(file):
    if file[-1] == "/":
        return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAAAXNSR0IArs4c6QAABKhJREFUeF7tm81rE0EUwN9s0qRYC22taKUtngzoQWOrjRfx5Fnw0hy8CVIQvPkP9KJXTx68i2CgNw8SqIhoi6GNglLwI0JFtGhbbMFNmqxsk002u9mZ92Zn0pZkLy3ZN+/j9958ZsKgwx/W4fFDF0C3AjqcQLcLdHgBBA6CxsTp3tFINB7xAeoFgH90bFs/Ntc+rMEWvaXeFr4ucOPqkanZW+OvASwGiicJs1h5k0jnL+kNiabdB6CQSe4AQFPmbSELrdeWDB5azFJlOTGdT6LVaRb0etpTyCSL6my6YTT+N4uVpUQ6f16dHXlNXgCxQiZpBqrjJ5fkhVmq5BLT+UlSIw3CKAC0LoD30iyW3ybS7y7gW6iXRAFQb7ah0SxWFhPp/JROGzzdKACOUPNAiO0PYrmdMny8ef/T5fnc33WFIMoYXSgAbkW6ugPGWYoMAzDvPvpy5smzzc+hK8CrIDwECxgwwtRKCb1JtnLy+lKUN4vjK0BcyXXLgYAQOhptEcIILtdmvw4uL29sBImiAEQjBsRjPYKFYfi6cDupJnyAufk/t7//Lm2+fL/9PLvw62eranZ/5lsHDA30QX9fXMzaiV8tB7FdkYTLnxdLG3euzOQeeMe0QADMABgfGRKZ2FfvBZVjsVTWQAMwDAZjI4PKAhSVtei9CkcmU9lYDqDk6OKOAaoB7O6R8LuqkPG2xslSWbs/1/c7bQMgm12nHb69Q7j1jnTPAIRMJ7F5MC4xgKdJ09nO211gdGRQ7lik5foZn0duxLWuJKNNDCBzznQmfN4YIGOcmEYJcbFXCACN84DQg6Br0BO7VotX80CpDkALR9FBuucgz6xA1kGsE3UAiIalxREVQYG2NwAQQZABSepsCwBKRuzAxfKtD1fJ0OzzatJCiDEYO0FcCnMyY0H1HED3EwjU/qZjSrAS/JZJms64FHoW4EQqzroeTLQKkNkMCfqmysBldJEBSK8EET1bT475WvkATkOsMKtwIYSI0JtFmawizNRFyBWg8jyA4ihfVh6TGIBnM4QHIO9Uc7De7awqvVUrYgC73w1WjaqZBdQGELaKkACq+0EmmAXkQ5Nv2R4ANf/UVECQy/yTm7CBBrVHV4CtQC8AXSFW9QbVGA1A4FKYUMKSmxbRLCC7qMYBCOgChLD9/geB0AKoVgOM+U6hcQBq7mvrAr6gcWjrUsyq3uGSePYHAAnH8U34MJUD4JvDZRYTnCpN8gDIfVWVy8F4ZCzIA/D5gTBPhiaoBWl9DV+lAPBCbQxMbfreTxoCaS9QFVY6C3gcR9QPZmggy0hVgNuKPsf1aXb7HxoAGfleNbDXQJb/Vg9LZWPAuR8QLWSSJadaIxEDRo8PiEOQ7pdO1mt/pfU0u8ippTJLZe1bY/XHt5xaeXx2IR4zLtoSx4b7oTfes79O9+QhWTP3VlIP51YXuQDslxOn+of7DseOOoIG50ofKzErbppgNt2jikNpt41z79p+2fjfYMXaXtj9uTPwtr5DYjBm2b/TsH+v4X2KRvC9k0MmWNs9RvlVbn0VACretnILanGnODASXQAHJlWaHO1WgCawB0ZttwIOTKo0OfofIM/BUAzd5bYAAAAASUVORK5CYII="
    else:
        return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAAAXNSR0IArs4c6QAABLlJREFUeF7tm9tLFFEYwL/xklmEmpfKykuiSYGRDz2FvVkG0tpbf0CaL0JPRv0jRauU9hSUEVJU2AUJSUJJMFJBzVBTV3fVlF13ZyaOzurs7plzm52L6IAP6ved/b7fdzmXOSvBHn+kPe4/7APYz4A9TkC0BKTevoGPxSVnrgCIlhH6aNUQ/52mxuY3r58/tDo+QgBGxmfnMjMzC9iNIzuLG+fD13540eG1HAI3gKqqS6Xd796Pszuvl8SDwP0VAUCP1RC4AVy9Xn/jcVvnKzEA7FpRAFZD4AZQW+fxeNufdLG7wiu5lQ96AGiErg5vc7cFPUEAQL3H295JBoB6G/fIsaDiAViVCdxm1tYxAOANOkYeB8AKCKYA8Pd2jKfx2aL9bgQg2RBMAYi6IwKCpkMCkEwISQEglvFkBDQAyYLgIABtIWhgAQuAZEDgBlBXV+95RJsFWFKCMlN86R+EjXCYZSRTiyVuAEmZBeKcxxWDLMvw6dsAqKrxfiFKB0m8FFw22wKA1vBIYV5YCsCCfxnCsoKvGR3MB3ebaoYG+nuZ0kYTsgBArLvMzlNKwreyDuGITPSttaWx4XPPW65lenIAkIw3vSrcQUiD4ByAzbgYx5pcx8aEJCkxPiQIDgPAb3tHJ6bg98xfnrLcli0uPA4VpUUJukYQXARgx+aNcATGJqfIAHDJIwGUFxfBgfQ0rC4Ogq0AmJubUOzZlGIhqNDa0uRME7QKBsu4egi2ZgA+RsYm052hSxi12oXlNYjICrgAgJn9IVva46SQ8wiCiwCIOyOiKSsKzAdcACC0EYbJ6VlGH0gpb/y/kpMnIONAum4hq4JrAPz4NQbzi35GAGJiBbk5cKGyPEbZXgC19R7vU+NDUUW3e2Nra3wgUjZXh7EjRwHcb2ls6HFkL6Dfl24auLOFNQchqk0exd4MsOlUOCYvKBsqewFoJSCpAGpctCOyDDNzC3w5zSldeCwf0lJTt7Q0MPYCIGTA4M9R8PkDnC7xrR3ycrLh4rkKB5sgpQQilEMLQTrbamlpWvR1A6EMmAuswT3HDkTivWI48zMLQq/vcAmY6/NUEEYNUAWInpdEHFsJxhmnKAr4/MtUn8wI5OVkQUpKitM94FkX7nrLwPAILAbMANBnEz6zcrOzoPr8WR0ACWRFdsdeAFkVDIXMBJioi5BkZGQkyDjcAyzzl3lgVwKwuDUm9ABXTIPo+Ht1bZ05ciKCRw4fgvjjctdkgL4JqiCBRLgHKOI80klsguCe8wDbM8CpvUBbe2cX/Z2taIwJegaLIteUAN3l6KuuJOFzKgO2rsnh+zz7OiA2nAe1+V1k9rA3AwhHYoPDI+AjrQQx3kUxlBWdgrLThUJt014A2nYYFynevcD2gZcEkH80h15BBhKOAEC2iKSrsJcERccA8DpjFbBdA4AXWIK8G6ZBu67L88CyNQN4vjDB/YZAlQDQcbPhE1dEWkasrAdhLRiG27caKoeGvo/wwEu8hMOgrf/KDKLv/xdkus/HMDSfiASgKOrmTygUXKqpLs/lG0D8Vv/2l6Zml1aFIPIaSpKf/jPRd/NazWUAQJcJuR7Hjeey1gLhfQAWQN1VQ+5nwK4KlwXG/gfPM5Nujg7x7AAAAABJRU5ErkJggg=="
 
class UploadServerHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        """Serve a GET request."""
        f = self.send_head()
        if f:
            self.copyfile(f, self.wfile)
            f.close()
 
    def do_HEAD(self):
        """Serve a HEAD request."""
        f = self.send_head()
        if f:
            f.close()
 
    def do_POST(self):
        """Serve a POST request."""
        r, info = self.deal_post_data()
        print((r, info, "by: ", self.client_address))
        f = BytesIO()
        f.write(b'<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
        f.write(b'<html>\n<head><title>File Upload</title>\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n</head>')
        f.write(bytes(css, 'utf-8'))
        f.write(b'<body>\n<center><div class="header"><p class=\"title\">File Upload</p></div>\n')
        f.write(b"<hr class=\"headerline\">\n")
        if r:
            f.write(b"<strong class=\"success\">File has been uploaded succesfully.</strong><br><br>")
        else:
            f.write(b"<strong class=\"failure\">File couldn't be uploaded.</strong><br><br>")
        f.write(info.encode())
        f.write(("<br><br><br><a class=\"backbutton\" href=\"%s\">Go Back</a><br><br>" % self.headers['referer']).encode())
        f.write(b"<hr>\n<footer>Made with <span style=\"color: #FF0000;\">&#10084</span> by <a href=\"https://github.com/akatiggerx04\">akatiggerx04</a>.</footer></center></body>\n</html>\n")
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(length))
        self.end_headers()
        if f:
            self.copyfile(f, self.wfile)
            f.close()
        
    def deal_post_data(self):
        content_type = self.headers['content-type']
        if not content_type:
            return (False, "Content-Type header doesn't contain boundary")
        boundary = content_type.split("=")[1].encode()
        remainbytes = int(self.headers['content-length'])
        line = self.rfile.readline()
        remainbytes -= len(line)
        if not boundary in line:
            return (False, "Content NOT begin with boundary")
        line = self.rfile.readline()
        remainbytes -= len(line)
        fn = re.findall(r'Content-Disposition.*name="file"; filename="(.*)"', line.decode())
        if not fn:
            return (False, "Can't find out file name...")
        path = self.translate_path(self.path)
        fn = os.path.join(path, fn[0])
        line = self.rfile.readline()
        remainbytes -= len(line)
        line = self.rfile.readline()
        remainbytes -= len(line)
        try:
            out = open(fn, 'wb')
        except IOError:
            return (False, "Can't create write file, do you have enough permissions to write?")
                
        preline = self.rfile.readline()
        remainbytes -= len(preline)
        while remainbytes > 0:
            line = self.rfile.readline()
            remainbytes -= len(line)
            if boundary in line:
                preline = preline[0:-1]
                if preline.endswith(b'\r'):
                    preline = preline[0:-1]
                out.write(preline)
                out.close()
                return (True, "%s" % fn)
            else:
                out.write(preline)
                preline = line
        return (False, "Unexpect Ends of data.")
 
    def send_head(self):
        path = self.translate_path(self.path)
        f = None
        if os.path.isdir(path):
            if not self.path.endswith('/'):
                self.send_response(301)
                self.send_header("Location", self.path + "/")
                self.end_headers()
                return None
            for index in "index.html", "index.htm":
                index = os.path.join(path, index)
                if os.path.exists(index):
                    path = index
                    break
            else:
                return self.list_directory(path)
        ctype = self.guess_type(path)
        try:
            f = open(path, 'rb')
        except IOError:
            self.send_error(404, "File not found")
            return None
        self.send_response(200)
        self.send_header("Content-type", ctype)
        fs = os.fstat(f.fileno())
        self.send_header("Content-Length", str(fs[6]))
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.end_headers()
        return f
 
    def list_directory(self, path):
        try:
            list = os.listdir(path)
        except os.error:
            self.send_error(404, "Not enough permissions to list directory.")
            return None
        list.sort(key=lambda a: a.lower())
        f = BytesIO()
        displaypath = html.escape(urllib.parse.unquote(self.path))
        f.write(b'<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
        f.write(("<html>\n<head><title>Directory listing for %s</title>\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n</head>" % displaypath).encode())
        f.write(bytes(css, 'utf-8'))
        f.write(("<body>\n<center><div class='header'><p class=\"title\">Directory listing for %s</p></div>\n" % displaypath).encode())
        f.write(b"<hr class=\"headerline\">\n")
        f.write(b"<form ENCTYPE=\"multipart/form-data\" method=\"post\">")
        f.write(b"<label class=\"label\"><input name=\"file\" type=\"file\" required/><span>Select a file</span></label>")
        f.write(b"<input class=\"upload\" type=\"submit\" value=\"Upload File\"/></form>\n")
        f.write(b"\n<ul>\n")
        for name in list:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            if os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"
            if os.path.islink(fullname):
                displayname = name + "@"
            f.write(('<li class="item"><img class="fileicon" src=%s><a href="%s">%s</a>\n'
                    % (geticon(html.escape(displayname)), urllib.parse.quote(linkname), html.escape(displayname))).encode())
        f.write(b"</ul>\n<hr>\n<footer>Made with <span style=\"color: #FF0000;\">&#10084</span> by <a href=\"https://github.com/akatiggerx04\">akatiggerx04</a>.</footer></center></body>\n</html>\n")
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(length))
        self.end_headers()
        return f
 
    def translate_path(self, path):
        path = path.split('?',1)[0]
        path = path.split('#',1)[0]
        path = posixpath.normpath(urllib.parse.unquote(path))
        words = path.split('/')
        words = [_f for _f in words if _f]
        path = os.getcwd()
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir): continue
            path = os.path.join(path, word)
        return path
 
    def copyfile(self, source, outputfile):
        shutil.copyfileobj(source, outputfile)
 
    def guess_type(self, path):
        base, ext = posixpath.splitext(path)
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        ext = ext.lower()
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        else:
            return self.extensions_map['']
 
    if not mimetypes.inited:
        mimetypes.init()
    extensions_map = mimetypes.types_map.copy()
    extensions_map.update({'': 'application/octet-stream', '.py': 'text/plain', '.c': 'text/plain', '.h': 'text/plain', '.html': 'text/plain', '.htm': 'text/plain',})

def awesomeserver(HandlerClass = UploadServerHandler, ServerClass = http.server.HTTPServer):
    http.server.test(HandlerClass, ServerClass)
 
if __name__ == '__main__':
    awesomeserver()