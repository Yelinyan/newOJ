import subprocess
import redis
import pymongo
import json
import time

conn=pymongo.Connection("localhost",27017)
db=conn['newoj']
cache=redis.Redis(host="127.0.0.1",port=6379)


while True:
    submitinfo=json.loads(cache.blpop('diysubmitque',timeout=0)[1])
    rst=''
    tim=''
    memory=''
    lang=submitinfo['lang']
    user=submitinfo['who']
    submittime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
    title=submitinfo['pname']
 
    code=submitinfo['code']
    code.replace('','\r\n')
    if submitinfo['lang']=='JAVA':
        sourcecode=open('Main.java','w')
        sourcecode.write(code)
        sourcecode.close() 
	compileinfo=subprocess.Popen('javac Main.java',shell=True,stdout=subprocess.PIPE).stdout.readlines()
        subprocess.call('chmod 777 Main.class',shell=True)
        if not compileinfo:
            info=subprocess.Popen('lrun --max-real-time %s --max-memory %s --max-output 1048575 bash -c \'cat %s.in | java Main > out\' 3>&1'%(int(submitinfo['time'])/500,int(submitinfo['memory'])*2048,int(submitinfo['pid'])),stdout=subprocess.PIPE,shell=True).stdout.readlines()
        else:
            rst='Compile Error'
    elif submitinfo['lang']=='C':
        sourcecode=open('Main.c','w')
        sourcecode.write(code)
        sourcecode.close() 
	compileinfo=subprocess.Popen('gcc Main.c',shell=True,stdout=subprocess.PIPE).stdout.readlines()
        subprocess.call('chmod 777 a.out',shell=True)
        if not compileinfo:
            info=subprocess.Popen('lrun --max-real-time %s --max-memory %s --max-output 1048575 bash -c \'cat %s.in | ./a.out > out\' 3>&1'%(int(submitinfo['time'])/1000,int(submitinfo['memory'])*1024,int(submitinfo['pid'])),stdout=subprocess.PIPE,shell=True).stdout.readlines()
        else:
            rst='Compile Error'
    else:
        sourcecode=open('Main.cpp','w')
        sourcecode.write(code)
        sourcecode.close() 
	child=subprocess.Popen('g++ Main.cpp',shell=True,stdout=subprocess.PIPE)
	child.wait()
	compileinfo=child.returncode
        subprocess.call('chmod 777 a.out',shell=True)
        if not compileinfo:
            info=subprocess.Popen('lrun --max-real-time %s --max-memory %s --max-output 1048575 bash -c \'cat %s.in | ./a.out > out\' 3>&1'%(int(submitinfo['time'])/1000,int(submitinfo['memory'])*1024,int(submitinfo['pid'])),stdout=subprocess.PIPE,shell=True).stdout.readlines()
        else:
            rst='Compile Error'

    if not rst:
        ninfo=[]
        for x in info:
            ninfo.append(x.split())
        for x in xrange(len(ninfo)):
            ninfo[x][1].replace('','\n')

        if ninfo[6][1]=='MEMORY':
            rst='Memory Limit'
        elif ninfo[6][1]=='OUTPUT':
            rst='Output Limit'
        elif ninfo[6][1]=='REAL_TIME':
            rst='Time Limit'
        else:
            result=subprocess.Popen('diff --ignore-all-space out %s.out'%submitinfo['pid'],stdout=subprocess.PIPE,shell=True).stdout.readlines()
            if not result:
                rst='Accepted'
                tim=ninfo[1][1]
                memory=ninfo[0][1]
            else:
                rst='Wrong answer'
    result_={}
    result_['User']=user
    result_['Problem']=title
    result_['Result']=rst
    if tim:
        result_['Time']=str(float(tim)*1000)+'MS'
    else:
        result_['Time']=tim
    if memory:
        result_['Memory']=str(int(memory)/1024)+'KB'
    else:
        result_['Memory']=memory
    result_['Submit Time']=submittime
    result_['Language']=lang
    cname=submitinfo['cname']

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
        if db.board.find_one({"cname":cname,"nickname":submitinfo['who']})['subinfo'][submitinfo['whatpid']]['haveaced']!=1:
            db.board.update({"cname":cname,"nickname":submitinfo['who']},{"$set":{"subinfo.%d.haveaced"%submitinfo['whatpid']:1,"subinfo.%s.subtimes"%submitinfo['whatpid']:times+1,"solved":solvedn+1,"time":timen+1}})
        if int(submitinfo['pid']) not in db.users.find_one({"nickname":submitinfo['who']})['solved']:
            db.users.update({"nickname":submitinfo['who']},{"$push":{"solved":int(submitinfo['pid'])}})
    else:
        db.board.update({"cname":cname,"nickname":submitinfo['who']},{"$set":{"subinfo.%d.subtimes"%submitinfo['whatpid']:times+1,"time":timen+1}})

