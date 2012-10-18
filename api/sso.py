import ldap
from datetime import datetime, timedelta
from flask import Flask, url_for, request, Response, json
app = Flask(__name__)

@app.route('/api/user/<username>', methods = ['GET'])
def user_info(username):
        global sessions
        if username in sessions:
                print "Seguimos get"
                ret = []
                for ip, timestamp in sessions[username].items():
                        if datetime.now()-timestamp < timedelta(seconds=60):
                                ret.append(ip)
                return json.dumps(ret)
        else:
                return 'KO'

@app.route('/api/login', methods = ['POST'])
def login():
        global sessions
        username = request.form['username']
        user_dn = "uid=%s,ou=Users,ou=auth,dc=guifibages,dc=net" % username
        password = request.form['password']
        print "Datos: %s %s" % (user_dn, password)
        try:
                l = ldap.initialize("ldaps://aaa.guifibages.net:636")
                l.simple_bind_s(user_dn,password)
        except ldap.INVALID_CREDENTIALS:
                return Response('Invalid credentials' ,status=401)
        except ldap.SERVER_DOWN:
                return Response("Can't connect to server",status=500)
        except ldap.LDAPError, error_message:
                print "Excepcion"
                return Response('LDAPError: %s' % error_message ,status=500)

        print request.headers
        if not request.headers.getlist("X-Forwarded-For"):
           ip = request.remote_addr
        else:
           ip = request.headers.getlist("X-Forwarded-For")[0]

        print "Llegamos al final %s" % ip

        if not username in sessions:
                sessions[username] = {}
        print "Por ahora bien %s" % datetime.now()
        sessions[username][ip] = datetime.now()
        print "Seguimos %s" % sessions[username]

        return 'OK'

if __name__ == "__main__":
        global sessions
        sessions = dict()
        app.run()
