#!/usr/bin/python
#coding=utf-8
#filename: portTraffic.py
from collections import defaultdict
import telnetlib
import os,sys,commands,multiprocessing
import smtplib  
import time
from email.mime.multipart import MIMEMultipart  
from email.mime.text import MIMEText  
from email.mime.image import MIMEImage  

import sys
if not "/root/labroom" in sys.path:
    sys.path.append("/root/labroom")
import messageMode
#-------config--dir----------------
devicefile = '/root/alllogscan/alllogscan.ini'              #Attention use full path 
logfile_path = '/root/log/'
alllogscan_path = '/root/alllogscan/'
pythonlog =  '/root/mylog.txt'

#-------parameter-------
sms_off = 0    #if you want trun off sms ,please set to 1
mail_off = 0    #if you want trun off sms ,please set to 1
linecount = 0
MAX_process = 100         #mutiprocessing
once_line = 300           #every exec will read 300 line logs

#---init paramater------
device_idct = defaultdict(lambda:defaultdict(dict))
begintime =  time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

#---read file into idct-----------
file = open(devicefile)
for line in file.readlines():
    if (line.split()[0].find('#') >= 0)|(len(line) < 5): #jump the comments,jump short than 1.1.1.1
        #os.system("echo "+begintime+' '+" init device file error ! >> "+pythonlog)  # log to mylog.txt 
        #print 'init device file error'
        continue
    else:
        device_idct[linecount]['ip'] = line.split()[0]
        device_idct[linecount]['name']= line.split()[1]  
        device_idct[linecount]['muti_grep']= line.split()[2]
        device_idct[linecount]['muti_mail']= line.split()[3]
        device_idct[linecount]['muti_phone']= line.split()[4]
        linecount += 1    #line counter
file.close()
#print "linecount:",linecount
#print device_idct



def alllogscan(_fuc_ip,_fuc_name,_fuc_muti_grep,_fuc_muti_mail,_fuc_muti_phone):
    '''log scan 
    '''
    successful_flag = 'ok'
    mail_tmp_list = []
    newlogfile = ''
    newlogfile_bak = ''
    
    #print _fuc_ip,_fuc_name,_fuc_muti_grep,_fuc_muti_mail,_fuc_muti_phone

    log_path = logfile_path+_fuc_ip
    log_temp_path = alllogscan_path+_fuc_ip+'.logtmp'
    sendmail_temp_path = alllogscan_path+_fuc_ip+'.lasttmp'


    #--------read last mail to mail_tmp_list--------------
    if os.path.exists(sendmail_temp_path):
        last_mail = open(sendmail_temp_path)
        for lastmailline in last_mail.readlines():
            mail_tmp_list.append(lastmailline) 
        last_mail.close()
    print 'last mail line',len(mail_tmp_list)


    #-------creat new grep log to ip.logtmp------------
    for grep_index in range(0, len(_fuc_muti_grep.split(';'))): 
        every_grep =  _fuc_muti_grep.split(';')[grep_index]
        every_grep = every_grep.replace('_',' ')
        commandstr_os = 'tail -n '+str(once_line)+' '+log_path+' |egrep '+every_grep+ ' >> ' +log_temp_path
        print commandstr_os
        os.system(commandstr_os)

    #-----read the file ip.logtmp to MEM------
    Tmp_log_mem = open(log_temp_path)
    for line in Tmp_log_mem.readlines():
        newlogfile += line
    Tmp_log_mem.close()
    newlogfile_bak =  newlogfile
    print 'newlog lines:',newlogfile_bak.count('\n')

    #----delete every line of last mail in this newlogfile--find different content--
    for index_last in range(0,len(mail_tmp_list)):
        #print index_last
        #print newlogfile_bak.find(every_line)
        newlogfile_bak = newlogfile_bak.replace(mail_tmp_list[index_last],'')

    print 'diff lines:',newlogfile_bak.count('\n')
    print 'diff content will be send:',newlogfile_bak
    
    
    #-----write to lastlogtmp ------
    thistime_mail = open(sendmail_temp_path,'w')
    thistime_mail.write(newlogfile)
    thistime_mail.close()

    if newlogfile_bak != '':
        #print 'mail send ----------'
        #print _fuc_ip,_fuc_name,_fuc_muti_grep,_fuc_muti_mail,_fuc_muti_phone
        #-------send mail to receivers----------------


        messageMode.send_muti_sms(_fuc_muti_phone,sms_off,'Alllogscan '+_fuc_name,'log:' + _fuc_name+' '+newlogfile_bak)
        messageMode.sendtxtmail(_fuc_name +' '+' log scan',mail_off,newlogfile_bak,_fuc_muti_mail,begintime)

            

    return successful_flag


def func(_index):
    new_idct = device_idct
    fuc_index = _index
    fuc_ip = new_idct[_index]['ip']
    fuc_name = new_idct[_index]['name']
    fuc_muti_grep = new_idct[_index]['muti_grep']
    fuc_muti_mail = new_idct[_index]['muti_mail']
    fuc_muti_phone = new_idct[_index]['muti_phone']

    print '---',fuc_index,'/',linecount,'--',fuc_ip,'----',fuc_name,'----[',fuc_muti_grep,']-----'
    logscan_ret =  alllogscan(fuc_ip,fuc_name,fuc_muti_grep,fuc_muti_mail,fuc_muti_phone)
    if (logscan_ret != 'ok'):
        os.system("echo "+begintime+' '+fuc_ip+':'+"  logscan fail ! Code:"+logscan_ret+" >> "+pythonlog)
        print fuc_name +' '+fuc_ip+'  logscan   error...'
        return 'error'
    return 'not find this menu...'

def main(_linecount):
    os.system("echo "+begintime+"   all log Scan begin !  >> "+pythonlog)  # log to mylog.txt 
    pool = multiprocessing.Pool(processes=MAX_process)
    result = []
    for index in xrange(_linecount):
        result.append(pool.apply_async(func, (index, )))
        #time.sleep(1)
    pool.close()
    pool.join()

    for res in result:
        #print 'Mutiprocess ret:',res.get(),res.successful()
        if (res.successful() != True):
            print "Mutiprocess fail !"

    endtime =  time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    os.system("echo "+endtime+"  all log Scanned over !  >> "+pythonlog)  # log to mylog.txt 
    


if __name__ == "__main__":
   logtmpfilepath_cmd = "rm -f "+alllogscan_path + "*.logtmp"
   #print logtmpfilepath_cmd
   os.system(logtmpfilepath_cmd)
   #time.sleep(2)
   main(linecount)
