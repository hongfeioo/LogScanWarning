# AllLogScan

## 简介
通过过滤日志文件中的关键字，出现“感兴趣”的行，就会触发短信和邮件报警。


## 配置文件格式
```
| 日志文件名 | 设备描述|报警关键字|邮箱|手机号|
|10.22.1.2| IDC2_switch1 | failed;Power | yihf@lie.com | 135XXXXXX |
|127.0.0.1| mylinux  | Accepted.password | yihf@lie.com | 135XXXXXX |
|10.22.1.3| IDC2_switch2 | LINK.UPDOWN  | yihf@lie.com | 135XXXXXX |


解释：
1. 10.22.1.2   是idc2_switch1设备的日志文件名，第三个字段分别对失败，电源 这2个关键字信息感兴趣， 收件人邮箱和手机号.
2. 127.0.0.1   是上报本机日志的文件名，对本机的登陆日志感兴趣， 收件人邮箱和手机号.
3. 10.22.1.3   是IDC2_switch2设备的日志文件名，针对端口UPDOWN状态，  收件人邮箱和手机号.

** 第三个字段的感兴趣关键字提取自日志文件，多关键字使用分号分割，空格使用点代替。
```

## 主程序中的参数介绍
```
devicefile = '/root/alllogscan/alllogscan.ini'            #配置文件路径
logfile_path = '/root/log/'                               #日志文件的存放位置
alllogscan_path = '/root/alllogscan/'                     #本程序所在的位置
pythonlog =  '/root/mylog.txt'                            #本程序输出的日志

#-------parameter-------
sms_off = 0                                               #if you want trun off sms ,please set to 1
mail_off = 0                                              #if you want trun off mail ,please set to 1
MAX_process = 100                                         #多线程并发数
once_line = 300                                           #每次只过滤日志的最后300行，当日志产生的很快时可以增大这个数

```


## 原理解读
1. 本次的过滤结果存放在[IP].logtmp中，  上次的过滤结果存放在[IP].lasttmp 中，差异部分会被报警。
2. 本次程序运行结束前logtmp会覆盖lasttmp 。
3. 配置文件中的第四列，由于grep中的空格被替换成了_ ， 如果感兴趣的关键字中有_ , 需要变成.(通配符) ,这一点需要特别注意；
4. 同一个日志文件在配置文件中只能写一行，因为如果分开写两行，执行完第一行 lasttmp就会被修改，第二行执行的时候读取的lasttmp就不是上次过滤的感兴趣log了 。 
5. 当配置文件中条目比较多时候，请注意每次运行的时间，合理设置计划任务频率
6. 注意感兴趣关键字的前后顺序， 因为会造成输出日志的前后顺序不同，会影响管理员对故障的判断，例如对接口的闪断报警，一般先写Down，后写UP；


## once_line 参数
1. 本程序每次采集最后的300条日志进行分析。 问题就来了，如果在下次采集分析来临之前，由于设备中间出现了日志狂刷，把感兴趣日志刷出了300条之前，那么这次采集将漏掉敏感信息。 也就是说，如果程序两分钟一次运行，请确保2分钟之内设备产生的新日志在300条之内。  如果设备产生日志比较大，请加大这个数字。

## 邮件短信报警模块配置
[messagemodule](https://github.com/hongfeioo/messagemodule#%E9%82%AE%E7%AE%B1%E6%89%8B%E6%9C%BA%E5%8F%B7%E7%9F%AD%E4%BF%A1%E9%80%9A%E9%81%93%E9%85%8D%E7%BD%AE)</p>

## rsyslog 的设置

```
1.  如果没有rsyslog需要安装，并创建接受日志的文件夹
yum install rsyslog -y  
mkdir -pv /root/log

2.   rsyslog的配置文件需要修改
[root@c3]# grep -v "^#" /etc/rsyslog.conf | grep -v "^$"
$ModLoad imuxsock # provides support for local system logging (e.g. via logger command)
$ModLoad imjournal # provides access to the systemd journal
$ModLoad immark  # provides --MARK-- message capability
$ModLoad imudp
$UDPServerRun 514
$ModLoad imtcp
$InputTCPServerRun 514
$WorkDirectory /var/lib/rsyslog
$ActionFileDefaultTemplate RSYSLOG_TraditionalFileFormat
$template logfile,"/root/log/%fromhost-ip%.log"
*.*  ?logfile                             
$IncludeConfig /etc/rsyslog.d/*.conf
$OmitLocalLogging on
$IMJournalStateFile imjournal.state
*.info;mail.none;authpriv.none;cron.none                /var/log/messages
authpriv.*                                              /var/log/secure
mail.*                                                  -/var/log/maillog
cron.*                                                  /var/log/cron
*.emerg                                                 :omusrmsg:*
uucp,news.crit                                          /var/log/spooler
local7.*                                                /var/log/boot.log

 
3.systemctl restart  rsyslog                              #重启服务

4. 检查端口
[root@c3]# netstat -aulntp | grep rsyslog
tcp        0      0 0.0.0.0:514             0.0.0.0:*               LISTEN      20228/rsyslogd      
tcp6       0      0 :::514                  :::*                    LISTEN      20228/rsyslogd      
udp        0      0 0.0.0.0:514             0.0.0.0:*                           20228/rsyslogd      
udp6       0      0 :::514                  :::*                                20228/rsyslogd  

```



## 开发环境
Python 2.7.5 

## 作者介绍
yihongfei  QQ:413999317   

CCIE 38649


## 寄语
为网络自动化运维尽绵薄之力

