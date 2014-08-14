import os.path
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import pymongo
import redis
import json
import tornado.httpclient
from tornado.template import Template

import uimodules
import random
import time
import subprocess
import sys
from BeautifulSoup import BeautifulSoup

from tornado.options import define, options
define("port",default=8000,help="run on the given port",type=int)

class Application(tornado.web.Application):
	def __init__(self):
		handlers=[(r"/",IndexHandler),
				  (r"/signup",SignupHandler),
				  (r"/dealup",DealSignUpHandler),
				  (r"/dealin",DealSignInHandler),
				  (r"/logout",DealLogOutHandler),
				  (r"/contests",ContestsHandler),
				  (r"/problems",ProblemsHandler),
				  (r"/create",CreateHandler),
				  (r"/creatediy",DiyHandler),
				  (r"/countdown",CountDownHandler),
				  (r"/submit",SubmitHandler),
				  (r"/submission",SubmissionHandler),
				  (r"/board",BoardHandler),
				  (r"/howtouse",HowHandler),
				  (r"/problem",ProblemHandler)
				 ]
		settings={
			"template_path": "templates",
			"static_path": "static",
			"cookie_secret": "bZJc2sWbQLKos6GkHn/VB9oXwQt8S0R0kRvJ5/xJ89E=",
			"ui_modules": uimodules,
			'debug': True,
		}
		conn=pymongo.Connection("localhost",27017)
		self.cache=redis.Redis(host="127.0.0.1",port=6379)
		self.db=conn["newoj"]
		self.user="passerby"
		tornado.web.Application.__init__(self, handlers,**settings)

class HowHandler(tornado.web.RequestHandler):
	def get(self):
		cookie=self.get_secure_cookie("username")
		self.render("howtouse.html",cookie=cookie)
<<<<<<< HEAD
=======
		
>>>>>>> f70c447cd8481b93bcb678629fb88436473e6b0c

class BoardHandler(tornado.web.RequestHandler):
	def get(self):
		cookie=self.get_secure_cookie("username")
		name=self.get_argument("name")
		coll=self.application.db.board
		contest=self.application.db.contest.find_one({"name":name})
		board=list(coll.find({"cname":name}).sort([("solved",-1),("time",1)]))
		length=len(contest["problems"])
		self.render("board.html",board=board,length=length,cookie=cookie)


<<<<<<< HEAD
		
=======
>>>>>>> f70c447cd8481b93bcb678629fb88436473e6b0c

class SubmissionHandler(tornado.web.RequestHandler):
	def get(self):
		pagen=self.get_argument("page","1")
		coll=self.application.db.results
		tmp=list(coll.find().sort([("Submit Time",-1)]))
		length=len(tmp)
		results=[]
		for i in range(15):
			if (int(pagen)-1)*15+i <length:
				results.append(tmp[(int(pagen)-1)*15+i])
		cookie=self.get_secure_cookie("username")
		if not cookie:
			self.redirect("/")
		else :
			self.render('submission.html',state=0,cookie=cookie,results=results,length=length,pagen=int(pagen))

class SubmitHandler(tornado.web.RequestHandler):
	def post(self):
		lang=self.get_argument("lang")
		code=self.get_argument("code")
		cname=self.get_argument("cname")
		if len(code)<20:
			self.write("<html><head></head><body><p>Your code is too short or too long</p></body></html>")
		else:
			pid=self.get_argument("pid")
			coll=self.application.db.problems
			problem=coll.find_one({"problemid":int(pid)})
			user=self.application.db.users.find_one({'username':self.get_secure_cookie('username')})
			who=user['nickname']
			whatpid=0
			contest=self.application.db.contest.find_one({"name":cname})
			pset=contest['problems']
			for x in range(len(pset)):
				if int(pid)==pset[x]:
					whatpid=x
<<<<<<< HEAD
			if int(pid)<5000:	
				self.application.cache.rpush('submitque',json.dumps({u"lang":lang,u"code":code,u"pid":pid,u"who":who,u"pname":problem['title'],u"cname":cname,u"whatpid":whatpid}))
			else:
				self.application.cache.rpush('diysubmitque',json.dumps({u"lang":lang,u"code":code,u"pid":pid,u"who":who,u"pname":problem['title'],u"cname":cname,u"whatpid":whatpid,u"time":problem['timeinfo'],u"memory":problem['meminfo']}))
=======
			self.application.cache.rpush('submitque',json.dumps({u"lang":lang,u"code":code,u"pid":pid,u"who":who,u"pname":problem['title'],u"cname":cname,u"whatpid":whatpid}))
>>>>>>> f70c447cd8481b93bcb678629fb88436473e6b0c
			self.redirect('/problem?id='+str(pid)+'&contest='+cname)

class CountDownHandler(tornado.web.RequestHandler):
	def get(self):
		name=self.get_argument("where")
		coll=self.application.db.contest
		contest=coll.find_one({"name":name})
		starttime=contest["starttime"]
		starttimearray=time.strptime(starttime,"%Y-%m-%d %H:%M:%S")
		cookie=self.get_secure_cookie("username")
		if not cookie:
			self.redirect("/")
		else :
			self.render('countdown.html',state=0,cookie=cookie,timestruct=starttimearray)

class DiyHandler(tornado.web.RequestHandler):
	def get(self):
		cookie=self.get_secure_cookie("username")
		if not cookie:
			self.redirect("/")
		else :
			user=self.application.db.users.find_one({'username':cookie})
			if 'Admin' in user['role']:
				self.render('diycreate.html',state=0,cookie=cookie)
			else :
				self.redirect("/contests")
	def post(self):
		id=self.get_argument('Id')
		title=self.get_argument('Title')
		time=self.get_argument('Time')
		memory=self.get_argument('Memory')
		dcrp=self.get_argument('Dcrp')
		indcrp=self.get_argument('Indcrp')
		oudcrp=self.get_argument('Oudcrp')
		si=self.get_argument('Si')
		so=self.get_argument('So')
		sti=self.get_argument('Sti')
		sto=self.get_argument('Sto')

		infile=open('%s.in'%id,'w')
		infile.write(sti)
		infile.close()
		outfile=open('%s.out'%id,'w')
		outfile.write(sto)
		outfile.close()
		subprocess.call('chmod 777 %s.in'%id,shell=True)
		subprocess.call('chmod 777 %s.out'%id,shell=True)

		coll=self.application.db.problems
		coll.insert({"problemid":int(id),"title":title,"timeinfo":time,"meminfo":memory,"dcrp":dcrp,"sampleinput":si,"sampleoutput":so,"inputdcrp":indcrp,"outputdcrp":oudcrp})

		self.redirect('/creatediy')
		
		

class CreateHandler(tornado.web.RequestHandler):
	def get(self):
		cookie=self.get_secure_cookie("username")
		if not cookie:
			self.redirect("/")
		else :
			user=self.application.db.users.find_one({'username':cookie})
			if 'Admin' in user['role']:
				self.render('create.html',state=0,cookie=cookie)
			else :
				self.redirect("/contests")

	def post(self):
		Name=self.get_argument('Name')
		problemset=[]
		tmp=self.get_argument('Problems')
		if tmp:
			tmp=tmp.split(' ')
			for x in tmp:
				problemset.append(int(x))
		else:
			for i in xrange(7):
				t=random.randint(1000,4054)
				while t in problemset:
					t=random.randint(1000,4054)
				problemset.append(t)

		coll=self.application.db.problems
		for x in problemset:
			if x>5000:
				continue
			if coll.find_one({"problemid":x}):
				continue
			url = 'http://poj.org/problem?id=%d' % x
			req=urllib2.Request(url)
			response=urllib2.urlopen(req);
			soup=BeautifulSoup(response.read())
			contents=soup.findAll('pre',attrs={'class':'sio'})

			sampleinput=contents[0]
			sampleoutput=contents[1]

			for img in soup.findAll('img'):
				img['src']='http://poj.org/'+img['src']

			contents=soup.findAll('div',attrs={'class':'ptx'})
			description=contents[0]
			description['class']=''

			inputdcrp=contents[1]
			inputdcrp['class']=''
			outputdcrp=contents[2]
			outputdcrp['class']=''

			title=soup.findAll('div',attrs={'class':'ptt'})[0].text

			info=soup.findAll('td',attrs={'width':'10px'})[0]
			meminfo=info.nextSibling.text
			timeinfo=info.previousSibling.text

			coll.insert({"problemid":x,"title":title,"timeinfo":timeinfo,"meminfo":meminfo,"dcrp":str(description),"sampleinput":str(sampleinput),"sampleoutput":str(sampleoutput),"inputdcrp":str(inputdcrp),"outputdcrp":str(outputdcrp)})

		howlongh=4
		starttime=self.get_argument("Starttime")	
		coll=self.application.db.contest
		coll.insert({"name":Name,"problems":problemset,"howlong":howlongh,"starttime":starttime})
		self.redirect("/contests")

class ProblemsHandler(tornado.web.RequestHandler):
	def get(self):
		cookie=self.get_secure_cookie("username")
		name=self.get_argument("name")
		coll=self.application.db.contest
		contest=coll.find_one({"name":name})
		starttime=contest["starttime"]
		starttimearray=time.strptime(starttime,"%Y-%m-%d %H:%M:%S")
		starttimestamp=int(time.mktime(starttimearray))
		if time.time()<starttimestamp and cookie!='Admin':
			self.redirect("/countdown?where="+name)
		if time.time()>starttimestamp+14400 and cookie!='Admin':
			self.redirect("/contests")
		problems=contest["problems"]
		problemname=[]
		coll=self.application.db.problems
		for x in problems:
			problemname.append(coll.find_one({"problemid":x}))
		nickname=self.application.user
		if not cookie:
			self.redirect("/")
		else :
			solved=self.application.db.users.find_one({"username":cookie})['solved']
			self.render('problems.html',state=0,cookie=cookie,problemnames=problemname,timestruct=starttimearray,solved=solved,name=name)

class ProblemHandler(tornado.web.RequestHandler):

	def get(self):
		problemid=self.get_argument('id')
		cname=self.get_argument('contest')
		coll=self.application.db.problems
		problem=coll.find_one({"problemid":int(problemid)})

		sampleinput=problem["sampleinput"]
		sampleoutput=problem["sampleoutput"]
		description=problem["dcrp"]
		inputdcrp=problem["inputdcrp"]
		outputdcrp=problem["outputdcrp"]
		title=problem["title"]
		meminfo=problem["meminfo"]
		timeinfo=problem["timeinfo"]
		cookie=self.get_secure_cookie("username")
		if int(problemid)>5000:
			timeinfo='Time Limit: '+timeinfo+'MS'
			meminfo='Memroy Limit: '+meminfo+'KB'
			sampleinput='<pre class="sio">'+sampleinput+'</pre>'
			sampleoutput='<pre class="sio">'+sampleoutput+'</pre>'
		if not cookie:
			self.redirect("/")
		else :
			self.render('problem.html',state=0,cookie=cookie,timeinfo=timeinfo,meminfo=meminfo,title=title,dcrp=description,inputdcrp=inputdcrp,outputdcrp=outputdcrp,sampleoutput=sampleoutput,sampleinput=sampleinput,problemid=problemid,cname=cname)
		
class ContestsHandler(tornado.web.RequestHandler):
	def get(self):
		pagen=self.get_argument("page","1")
		cookie=self.get_secure_cookie("username")
		coll=self.application.db.contest
		tmp=list(coll.find().sort([("starttime",-1)]))
		length=len(tmp)
		contests=[]
		for i in range(5):
			if (int(pagen)-1)*5+i <length:
				contests.append(tmp[(int(pagen)-1)*5+i])
		curtime=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()-14400))
		self.render('contests.html',state=0,cookie=cookie,contests=contests,pagen=int(pagen),length=length,curtime=curtime)


class IndexHandler(tornado.web.RequestHandler):
	def get(self):
		cookie=self.get_secure_cookie("username")
		self.render('home521.html',state=0,cookie=cookie)

class DealSignInHandler(tornado.web.RequestHandler):
	def post(self):
		username=self.get_argument('username')
		password=self.get_argument('password')
		coll=self.application.db.users
		tmp=coll.find_one({"username":username,"password":password})
		if not tmp:
			self.render('home.html',state=1,cookie="")
		else :
			self.set_secure_cookie("username",username)
			self.application.user=tmp["nickname"]
			self.redirect("/")

class DealLogOutHandler(tornado.web.RequestHandler):
	def get(self):
		self.clear_cookie("username")
		self.redirect("/")
			

class SignupHandler(tornado.web.RequestHandler):
	def get(self):
		self.render('signup.html',state='info',describe='Welcome to join us.')
		
class DealSignUpHandler(tornado.web.RequestHandler):
	def post(self):
		username=self.get_argument('username')
		password=self.get_argument('password')
		cpassword=self.get_argument('cpassword')
		nickname=self.get_argument('nickname')
		coll=self.application.db.users
		if len(str(username))>20 or len(str(username))<8 or len(str(password))>20 or len(str(password))<8 or len(str(nickname))>20 or len(str(nickname))<8:
<<<<<<< HEAD
			self.render('signup.html',state='danger',describe='username&password&nickname should less than 20 and longer than 8')
=======
			self.render('signup.html',state='danger',describe='username&nickname&password should less than 20 and langer than 8')
>>>>>>> f70c447cd8481b93bcb678629fb88436473e6b0c
		elif coll.find_one({"username":username}):
			self.render('signup.html',state='danger',describe='username have existed')
		elif password!=cpassword:
			self.render('signup.html',state='danger',describe='twice inputs are not eaual')
		elif coll.find_one({"nickname":nickname}):
			self.render('signup.html',state='danger',describe='nickname have existed')
		else:
			if str(username)=='Admin':
				coll.insert({"username":username,"password":password,"nickname":nickname,"solved":[],"role":['Admin']})
			else :
				self.set_secure_cookie("username",username)
				coll.insert({"username":username,"password":password,"nickname":nickname,"solved":[],"role":[]})
			self.redirect('/')


if __name__=="__main__":
	tornado.options.parse_command_line()
	http_server=tornado.httpserver.HTTPServer(Application())
	http_server.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()


