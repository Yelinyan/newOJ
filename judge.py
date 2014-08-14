import urllib
import urllib2
import cookielib
import re
import logging
import sys
import redis
import json
import pymongo
from time import sleep
from BeautifulSoup import BeautifulSoup

used=[0]
username=['NE1729']
password=['3676006']
conn=pymongo.Connection("localhost",27017)
class POJ:
    URL_HOME = 'http://poj.org/'
    URL_LOGIN = URL_HOME + 'login?'
    URL_SUBMIT = URL_HOME + 'submit?'
    URL_STATUS = URL_HOME + 'status?'
    INFO =['RunID','User','Problem','Result','Memory','Time','Language','Code Length','Submit Time']
    LANGUAGE = {
            'G++':'0',
            'GCC':'1',
            'JAVA':'2',
            'PASCAL':'3',
            'C++':'4',
            'C':'5',
            'FORTRAN':'6',
            }

    def __init__(self, user_id, password):
        self.user_id = user_id
        self.password = password
        cj = cookielib.LWPCookieJar()
        self.opener =urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        urllib2.install_opener(self.opener)

    def login(self):
        data = dict(
                user_id1 = self.user_id,
                password1 = self.password,
                B1 = 'login',
                url = '.')
        postdata = urllib.urlencode(data)
        try:
            req = urllib2.Request(POJ.URL_LOGIN,postdata)
            res = self.opener.open(POJ.URL_LOGIN,postdata).read()
            if res.find('loginlog')>0: 
                logging.info("login successful!")
                return True
            else:
                logging.error('login failed')
                return False
        except:
            logging.error('login failed')
            return False

    def submit(self,pid,language,src):
        submit_data = dict(
                problem_id = pid,
                language = POJ.LANGUAGE[language.upper()],
                source = src,
                submit = 'Submit',)
        postdata2 = urllib.urlencode(submit_data)
        try:
            req2 = urllib2.Request(POJ.URL_SUBMIT,data = postdata2)
            res = self.opener.open(POJ.URL_SUBMIT,postdata2).read()
            logging.info('submit successful')
            return True
        except:
            logging.error('submit error')
            return False

    def result(self,user_id,submitinfo,x):
        global used,conn
        cname=submitinfo['cname']
        url = POJ.URL_STATUS + urllib.urlencode({'user_id':user_id})
        page = urllib2.urlopen(url)
        soup = BeautifulSoup(page)
        table = soup.findAll('tr',{'align':'center'}) 
        tr=table[0]
        children=tr.findChildren()
        db=conn['newoj']
        if str(children[5].text)!='Compile Error':
            result=[str(children[0].text),str(children[1].text),str(children[3].text),str(children[5].text),str(children[7].text),str(children[8].text),str(children[9].text),str(children[11].text),str(children[12].text)]
        else:
            result=[str(children[0].text),str(children[1].text),str(children[3].text),str(children[5].text),str(children[8].text),str(children[9].text),str(children[10].text),str(children[12].text),str(children[13].text)]
        wait = ['Running & Judging','Compiling','Waiting']
        for i in range(3):
            if str(children[5].text)==wait[i] or str(children[5].text) == '':
                logging.info(str(children[5].text))
                return False
        result_={}
        for i in range(3,9):
            result_[POJ.INFO[i]]=result[i]
        result_['User']=submitinfo['who']
        result_['Problem']=submitinfo['pname']
        used[x]=0
        contest=db.contest.find_one({"name":cname})
        length=len(contest['problems'])
        boarditem=db.board.find_one({"nickname":submitinfo['who'],"cname":cname})
        if not boarditem:
            subinfo=[]
            for x in range(length):
                subinfo.append({"haveaced":0,"subtimes":0})
            db.board.insert({"cname":cname,"nickname":submitinfo['who'],"subinfo":subinfo,"solved":0,"time":0})

        db.results.insert(result_)
        times=db.board.find_one({"cname":cname,"nickname":submitinfo['who']})['subinfo'][submitinfo['whatpid']]['subtimes']
        solvedn=db.board.find_one({"cname":cname,"nickname":submitinfo['who']})['solved']
        timen=db.board.find_one({"cname":cname,"nickname":submitinfo['who']})['time']
        if result_['Result']=="Accepted":
<<<<<<< HEAD
            if db.board.find_one({"cname":cname,"nickname":submitinfo['who']})['subinfo'][submitinfo['whatpid']]['haveaced']!=1 :
		db.board.update({"cname":cname,"nickname":submitinfo['who']},{"$set":{"subinfo.%d.haveaced"%submitinfo['whatpid']:1,"subinfo.%s.subtimes"%submitinfo['whatpid']:times+1,"solved":solvedn+1,"time":timen+1}})
=======
            if db.board.find_one({"cname":cname,"nickname":submitinfo['who']})['subinfo'][submitinfo['whatpid']]['haveaced']!=1:
                db.board.update({"cname":cname,"nickname":submitinfo['who']},{"$set":{"subinfo.%d.haveaced"%submitinfo['whatpid']:1,"subinfo.%s.subtimes"%submitinfo['whatpid']:times+1,"solved":solvedn+1,"time":timen+1}})
>>>>>>> f70c447cd8481b93bcb678629fb88436473e6b0c
            if int(submitinfo['pid']) not in db.users.find_one({"nickname":submitinfo['who']})['solved']:
                db.users.update({"nickname":submitinfo['who']},{"$push":{"solved":int(submitinfo['pid'])}})
        else:
            db.board.update({"cname":cname,"nickname":submitinfo['who']},{"$set":{"subinfo.%d.subtimes"%submitinfo['whatpid']:times+1,"time":timen+1}})
        return True

def submit2poj(poj,submitinfo,i):
    if poj.login():
        logging.info("submiting")
        if poj.submit(submitinfo['pid'],submitinfo['lang'],submitinfo['code']):
            logging.info('getting result')
            status=poj.result(poj.user_id,submitinfo,i)
            while status!=True:
                status=poj.result(poj.user_id,submitinfo,i)

cache=redis.Redis(host="127.0.0.1",port=6379)
while True:
    for x in range(0,len(used)):
        if not used[x]:
            i=x
            break
    submitinfo=json.loads(cache.blpop('submitque',timeout=0)[1]) 
    poj = POJ(username[i],password[i])
    used[i]=1
  #  pool.spawn(submit2poj,poj,submitinfo,i)
    submit2poj(poj,submitinfo,i)



