import smtplib
import os
import sys
import requests
import ftplib
import pdfkit

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime


class TurboSx:
    def __init__(self,from_address,to,subject,body,pwd,smtp_server,smtp_port,smtp_con,mail_type="mail",body_type="html"):
        self.from_address=from_address
        self.to=to
        self.subject=subject
        self.body=body
        self.pwd=pwd
        self.mail_type=mail_type
        self.body_type=body_type
        self.smtp_server=smtp_server
        self.smtp_port=smtp_port
        self.smtp_con=smtp_con
        self.send_mail()

    def display(self):
        print(self.from_address)

    def compose_mail(self):
        #print(self.mail_type)
        #print(self.body_type)

        msg = MIMEMultipart('alternative')
        msg['Subject'] = self.subject
        msg['From'] = self.from_address
        msg['To'] = self.to

        # Create the body of the message (a plain-text and an HTML version).
        body = self.body

        # Record the MIME types of both parts - text/plain and text/html.
        if(self.body_type=="text"):
            part=MIMEText(self.body, 'plain')
        elif(self.body_type=="html"):
            part=MIMEText(self.body, 'html')
        else:
            print("Error in loading Body Type!!!")
   
        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        msg.attach(part)
        return msg


    def choose_mail(self):
        if(self.mail_type=="gmail"):
            self.send_gmail()
        elif(self.mail_type=="mail"):
            self.send_mail(self.smtp_server,int(self.smtp_port))
        else:
            print("Error in Loading Mail Type")


    def send_gmail(self):
        msg=self.compose_mail()
        
        # Send the message via local SMTP server. 
        #s = smtplib.SMTP('smtp.gmail.com', 587)
        #s.connect('smtp.gmail.com', 587)
        #s.ehlo()
        #s.starttls()
        #s.ehlo()
        s.login(self.from_address, self.pwd) #login with mail_id and password
        # sendmail function takes 3 arguments: sender's address, recipient's address
        # and message to send - here it is sent as one string.
        s.sendmail(self.from_address, self.to, msg.as_string())
        #s.quit()
        

    def send_mail(self):
        msg=self.compose_mail()
        
        # Send the message via local SMTP server. 
        #s = smtplib.SMTP(self.smtp_server, self.smtp_port)
        #s.connect(self.smtp_server, self.smtp_port)
        #s.ehlo()
        #s.starttls()
        #s.ehlo()
        self.smtp_con.login(self.from_address, self.pwd) #login with mail_id and password
        # sendmail function takes 3 arguments: sender's address, recipient's address
        # and message to send - here it is sent as one string.
        self.smtp_con.sendmail(self.from_address, self.to, msg.as_string())
        #s.quit()

       


class Shoot:
    def __init__(self,inbound_path=sys.argv[1]+"\inbound",outbound_path=sys.argv[1]+"\outbound\\"+datetime.now().strftime("%Y%m%d"),builds_path=sys.argv[1]+"\\builds"):        
        self.inbound_path=inbound_path
        self.outbound_path=outbound_path
        self.builds_path=builds_path
        if not os.path.exists(self.outbound_path):
            os.makedirs(self.outbound_path)

        ls=os.listdir(self.inbound_path)
        t_count=len(ls)
        ndate=datetime.now().strftime("%Y%m%d")
        ftpTransfer(self.outbound_path,ids+"_"+ndate+".csv")
        wpath_up=self.outbound_path+"\\"+ids+"_"+ndate+".csv"
        if(len(ls)>0):
            print("Total Files:",len(ls))
            f_count=1
            for i in os.listdir(self.inbound_path):
                now = datetime.now()
                fpath=self.inbound_path+"\\"+i
                wpath=self.outbound_path+"\\"+now.strftime("%H%M%S")+"_"+i
                wpath_f=self.outbound_path+"\\fail_"+now.strftime("%H%M%S")+"_"+i
                print("Preparing File "+str(f_count)+" of "+str(t_count))
                f_count=f_count+1
                if(i.endswith('.csv')):                    

                    
                    print("File name: "+fpath)
                    #print(wpath)
                    
                    file= open(fpath,'r')
                    
                    file_write = open(wpath_up, 'a+')
                    file_write_f =  open(wpath_f, 'a+')
                    count=0
                    fcount=0
                    for line in file:
                        if(count==0):
                            ln=line.strip().split(',')
                            try:
                            
                                from_address=ln[0]
                                pwd=ln[1]
                                smtp_server=ln[2]
                                smtp_port=ln[3]
                                #file_write.write(ln[0]+","+ln[1]+","+ln[2]+","+ln[3]+"\n")
                                try:
                                    s = smtplib.SMTP(smtp_server, smtp_port)
                                    s.connect(smtp_server, smtp_port)
                                    s.ehlo()
                                    s.starttls()
                                    s.ehlo()
                                except Exception as e:
                                    print(e)
                                    print("Unable to Connect to the smtp server: "+smtp_server+" at port: "+smtp_port)
                            except Exception as e:
                                print("Error in First line Configs for File {file}!!!".format(file=fpath))
                        else:
                            ln=line.strip().split(',')
                            print(count, end="::")
                            print(ln,end="")
                            subject=self.readBuildFiles(self.builds_path+"\\subject\\"+ln[2]).format(name=ln[0])
                            #print("Subject :"+subject)
                            body=self.readBuildFiles(self.builds_path+"\\body\\"+ln[3]).replace("{name}", ln[0]).replace("{email}", ln[1])
                            #print("Body :"+body)
                            
                            try:
                                TurboSx(from_address,ln[1],subject,body,pwd,smtp_server,smtp_port,s)
                                
                                print("-> Success", end=" : ")
                                print(smtp_server)
                                file_write.write(ln[0]+","+ln[1]+","+ln[2]+","+ln[3]+"\n")
                            except Exception as e:
                                print("-> Fail ", end=" : ")
                                print(smtp_server, end=" \n ")
                                print(e)
                                fcount=fcount+1
                                
                                file_write_f.write(ln[0]+","+ln[1]+","+ln[2]+","+ln[3]+","+smtp_server+","+from_address+"\n")
                                
                        count=count+1
                    file_write.close()
                    file_write_f.close()
                    file.close()
                    os.remove(fpath)
                    if(fcount==0):
                        os.remove(wpath_f)
                    try:
                        s.quit()
                    except Exception as e:
                        print(e)
                else:
                    print("Invalid File Extension "+i)
                    os.remove(fpath)
            ftpTransfer(self.outbound_path,ids+"_"+ndate+".csv")
        else:
            print("No Files To Process in inbound")

    def readBuildFiles(self,path):
        file= open(path,'r')
        str=""
        for line in file:
            str=str+line.strip()
        return str

class TurboSx_slow:
    def __init__(self,from_address,to,subject,body,pwd,smtp_server,smtp_port,mail_type="mail",body_type="html"):
        self.from_address=from_address
        self.to=to
        self.subject=subject
        self.body=body
        self.pwd=pwd
        self.mail_type=mail_type
        self.body_type=body_type
        self.smtp_server=smtp_server
        self.smtp_port=smtp_port
        
        self.send_mail()

    def display(self):
        print(self.from_address)

    def compose_mail(self):
        #print(self.mail_type)
        #print(self.body_type)

        msg = MIMEMultipart('alternative')
        msg['Subject'] = self.subject
        msg['From'] = self.from_address
        msg['To'] = self.to

        # Create the body of the message (a plain-text and an HTML version).
        body = self.body

        # Record the MIME types of both parts - text/plain and text/html.
        if(self.body_type=="text"):
            part=MIMEText(self.body, 'plain')
        elif(self.body_type=="html"):
            part=MIMEText(self.body, 'html')
        else:
            print("Error in loading Body Type!!!")
   
        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        msg.attach(part)
        return msg


    def choose_mail(self):
        if(self.mail_type=="gmail"):
            self.send_gmail()
        elif(self.mail_type=="mail"):
            self.send_mail(self.smtp_server,int(self.smtp_port))
        else:
            print("Error in Loading Mail Type")


    def send_gmail(self):
        msg=self.compose_mail()
        
        # Send the message via local SMTP server. 
        #s = smtplib.SMTP('smtp.gmail.com', 587)
        #s.connect('smtp.gmail.com', 587)
        #s.ehlo()
        #s.starttls()
        #s.ehlo()
        s.login(self.from_address, self.pwd) #login with mail_id and password
        # sendmail function takes 3 arguments: sender's address, recipient's address
        # and message to send - here it is sent as one string.
        s.sendmail(self.from_address, self.to, msg.as_string())
        #s.quit()
        

    def send_mail(self):
        #try:
            
            msg=self.compose_mail()

            # Send the message via local SMTP server. 
            s = smtplib.SMTP(self.smtp_server, self.smtp_port)
            s.connect(self.smtp_server, self.smtp_port)
            s.ehlo()
            s.starttls()
            s.ehlo()
            s.login(self.from_address, self.pwd) #login with mail_id and password
            # sendmail function takes 3 arguments: sender's address, recipient's address
            # and message to send - here it is sent as one string.
            s.sendmail(self.from_address, self.to, msg.as_string())
            s.quit()
        #except Exception as e:
            #print(e)
            
class TurboSx_Attach:
    def __init__(self,from_address,to,subject,body,pwd,smtp_server,smtp_port,path,mail_type="mail",body_type="text"):
        self.from_address=from_address
        self.to=to
        self.subject=subject
        self.body=body
        self.pwd=pwd
        self.mail_type=mail_type
        self.body_type=body_type
        self.smtp_server=smtp_server
        self.smtp_port=smtp_port
        self.path=path
        
        
        self.send_mail()

    def display(self):
        print(self.from_address)

    def htmltopdf(self):
        htmlPath=self.path
        exldfilenamExt=self.path[self.path.rindex("\\"):len(self.path)].strip('\\').split('.')[0]
        pdfPath=self.path[0:self.path.rindex("\\")]+"\\"+exldfilenamExt+".pdf"
        pdfkit.from_file(htmlPath, pdfPath)
        return [pdfPath,exldfilenamExt+".pdf"]

    def compose_mail(self):
        #print(self.mail_type)
        #print(self.body_type)

        pdfPath=self.htmltopdf()
        msg = MIMEMultipart('alternative')
        msg['Subject'] = self.subject
        msg['From'] = attach_etag+" "+self.from_address
        msg['To'] = self.to

        # Create the body of the message (a plain-text and an HTML version).
        body = self.body

        # Record the MIME types of both parts - text/plain and text/html.
        if(self.body_type=="text"):
            part=MIMEText(self.body, 'plain')
        elif(self.body_type=="html"):
            part=MIMEText(self.body, 'html')
        else:
            print("Error in loading Body Type!!!")
   
        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        msg.attach(part)
        
        #add atachment
        filename = pdfPath[1]
        attachment = open(pdfPath[0], "rb") 
          
        # instance of MIMEBase and named as p 
        p = MIMEBase('application', 'octet-stream') 
          
        # To change the payload into encoded form 
        p.set_payload((attachment).read()) 
          
        # encode into base64 
        encoders.encode_base64(p) 
           
        p.add_header('Content-Disposition', "attachment; filename= %s" % filename) 
          
        # attach the instance 'p' to instance 'msg' 
        msg.attach(p)
        
        return msg


    def choose_mail(self):
        if(self.mail_type=="gmail"):
            self.send_gmail()
        elif(self.mail_type=="mail"):
            self.send_mail(self.smtp_server,int(self.smtp_port))
        else:
            print("Error in Loading Mail Type")


    def send_gmail(self):
        msg=self.compose_mail()
        
        # Send the message via local SMTP server. 
        #s = smtplib.SMTP('smtp.gmail.com', 587)
        #s.connect('smtp.gmail.com', 587)
        #s.ehlo()
        #s.starttls()
        #s.ehlo()
        s.login(self.from_address, self.pwd) #login with mail_id and password
        # sendmail function takes 3 arguments: sender's address, recipient's address
        # and message to send - here it is sent as one string.
        s.sendmail(self.from_address, self.to, msg.as_string())
        #s.quit()
        

    def send_mail(self):
        #try:


            
            msg=self.compose_mail()

            # Send the message via local SMTP server. 
            s = smtplib.SMTP(self.smtp_server, self.smtp_port)
            s.connect(self.smtp_server, self.smtp_port)
            s.ehlo()
            s.starttls()
            s.ehlo()
            s.login(self.from_address, self.pwd) #login with mail_id and password
            # sendmail function takes 3 arguments: sender's address, recipient's address
            # and message to send - here it is sent as one string.
            s.sendmail(self.from_address, self.to, msg.as_string())
            s.quit()
        #except Exception as e:
            #print(e)            
       


class Shoot_slow:
    def __init__(self,inbound_path=sys.argv[1]+"\inbound",outbound_path=sys.argv[1]+"\outbound\\"+datetime.now().strftime("%Y%m%d"),builds_path=sys.argv[1]+"\\builds"):        
        self.inbound_path=inbound_path
        self.outbound_path=outbound_path
        self.builds_path=builds_path
        if not os.path.exists(self.outbound_path):
            os.makedirs(self.outbound_path)

        ls=os.listdir(self.inbound_path)
        t_count=len(ls)
        ndate=datetime.now().strftime("%Y%m%d")
        ftpTransfer(self.outbound_path,ids+"_"+ndate+".csv")
        wpath_up=self.outbound_path+"\\"+ids+"_"+ndate+".csv"
        if(len(ls)>0):
            print("Total Files:",len(ls))
            f_count=1
            for i in os.listdir(self.inbound_path):
                now = datetime.now()
                fpath=self.inbound_path+"\\"+i
                wpath=self.outbound_path+"\\"+ids+"_"+now.strftime("%H%M%S")+"_"+i
                wpath_f=self.outbound_path+"\\fail_"+now.strftime("%H%M%S")+"_"+i
                
                print("Preparing File "+str(f_count)+" of "+str(t_count))
                f_count=f_count+1
                if(i.endswith('.csv')):                    

                    
                    print("File name: "+fpath)
                    #print(wpath)
                    
                    file= open(fpath,'r')
                    file_write = open(wpath, 'a+')
                    file_write_f =  open(wpath_f, 'a+')
                    file_write_up =  open(wpath_up, 'a+')
                    count=0
                    fcount=0
                    for line in file:
                        
                        if(count==0):
                            ln=line.strip().split(',')
                            try:
                            
                                from_address=ln[0]
                                pwd=ln[1]
                                smtp_server=ln[2]
                                smtp_port=ln[3]
                                file_write.write(ln[0]+","+ln[1]+","+ln[2]+","+ln[3]+"\n")
#                                 try:
#                                     s = smtplib.SMTP(smtp_server, smtp_port)
#                                     s.connect(smtp_server, smtp_port)
#                                     s.ehlo()
#                                     s.starttls()
#                                     s.ehlo()
#                                 except Exception as e:
#                                     print(e)
#                                     print("Unable to Connect to the smtp server: "+smtp_server+" at port: "+smtp_port)
                            except Exception as e:
                                print("Error in First line Configs for File {file}!!!".format(file=fpath))
                        else:
                            ln=line.strip().split(',')
                            print(count, end="::")
                            print(ln,end="")
                            subject=self.readBuildFiles(self.builds_path+"\\subject\\"+ln[2]).format(name=ln[0])
                            #print("Subject :"+subject)
                            body=self.readBuildFiles(self.builds_path+"\\body\\"+ln[3]).replace("{name}", ln[0]).replace("{email}", ln[1])
                            
                            #print("Body :"+body)
                            
                            try:
                                TurboSx_slow(from_address,ln[1],subject,body,pwd,smtp_server,smtp_port)
                                
                                print("-> Success", end=" : ")
                                print(smtp_server)
                                file_write.write(ln[0]+","+ln[1]+","+ln[2]+","+ln[3]+"\n")
                                file_write_up.write(ln[0]+","+ln[1]+","+ln[2]+","+ln[3]+"\n")
                            except Exception as e:
                                
                                print("-> Fail ", end=" : ")
                                print(smtp_server, end=" \n ")
                                print(e)
                                fcount=fcount+1
                                
                                file_write_f.write(ln[0]+","+ln[1]+","+ln[2]+","+ln[3]+","+smtp_server+","+from_address+"\n")
                                
                        count=count+1
                    file_write.close()
                    file_write_f.close()
                    file_write_up.close()
                    file.close()
                    os.remove(fpath)
                    if(fcount==0):
                        os.remove(wpath_f)
                    
                else:
                    print("Invalid File Extension "+i)
                    os.remove(fpath)
            ftpTransfer(self.outbound_path,ids+"_"+ndate+".csv")
        else:
            print("No Files To Process in inbound")
    def readBuildFiles(self,path):
        file= open(path,'r')
        str=""
        for line in file:
            str=str+line.strip()
        return str

class Shoot_attach:
    def __init__(self,inbound_path=sys.argv[1]+"\inbound",outbound_path=sys.argv[1]+"\outbound\\"+datetime.now().strftime("%Y%m%d"),builds_path=sys.argv[1]+"\\builds"):        
        self.inbound_path=inbound_path
        self.outbound_path=outbound_path
        self.builds_path=builds_path
        attachment_path=self.outbound_path+"\\body\\"
        
        if not os.path.exists(self.outbound_path):
            os.makedirs(self.outbound_path)
            
        if not os.path.exists(attachment_path):
            os.makedirs(attachment_path)

        ls=os.listdir(self.inbound_path)
        t_count=len(ls)
        ndate=datetime.now().strftime("%Y%m%d")
        ftpTransfer(self.outbound_path,ids+"_"+ndate+".csv")
        wpath_up=self.outbound_path+"\\"+ids+"_"+ndate+".csv"
        if(len(ls)>0):
            print("Total Files:",len(ls))
            f_count=1
            for i in os.listdir(self.inbound_path):
                now = datetime.now()
                fpath=self.inbound_path+"\\"+i
                wpath=self.outbound_path+"\\"+ids+"_"+now.strftime("%H%M%S")+"_"+i
                wpath_f=self.outbound_path+"\\fail_"+now.strftime("%H%M%S")+"_"+i
                
                print("Preparing File "+str(f_count)+" of "+str(t_count))
                f_count=f_count+1
                if(i.endswith('.csv')):                    

                    
                    print("File name: "+fpath)
                    #print(wpath)
                    
                    file= open(fpath,'r')
                    file_write = open(wpath, 'a+')
                    file_write_f =  open(wpath_f, 'a+')
                    file_write_up =  open(wpath_up, 'a+')
                    count=0
                    fcount=0
                    for line in file:
                        
                        if(count==0):
                            ln=line.strip().split(',')
                            try:
                            
                                from_address=ln[0]
                                pwd=ln[1]
                                smtp_server=ln[2]
                                smtp_port=ln[3]
                                file_write.write(ln[0]+","+ln[1]+","+ln[2]+","+ln[3]+"\n")
#                                 try:
#                                     s = smtplib.SMTP(smtp_server, smtp_port)
#                                     s.connect(smtp_server, smtp_port)
#                                     s.ehlo()
#                                     s.starttls()
#                                     s.ehlo()
#                                 except Exception as e:
#                                     print(e)
#                                     print("Unable to Connect to the smtp server: "+smtp_server+" at port: "+smtp_port)
                            except Exception as e:
                                print("Error in First line Configs for File {file}!!!".format(file=fpath))
                        else:
                            ln=line.strip().split(',')
                            print(count, end="::")
                            print(ln,end="")
                            subject=self.readBuildFiles(self.builds_path+"\\subject\\"+ln[2]).format(name=ln[0])
                            #print("Subject :"+subject)
                            body=self.readBuildFiles(self.builds_path+"\\body\\"+ln[3]).replace("{name}", ln[0]).replace("{email}", ln[1])
                            #print("Body :"+body)
                            body_path=self.writeAttachmentFiles(attachment_path,ln[0],ln[1],body,now)
                            attach_text=attach_text_bkp
                            attach_text=attach_text.replace("{name}", ln[0]).replace("{email}", ln[1])
                            
                            attach_etag=attach_etag_bkp
                            attach_etag=attach_etag.replace("{name}", ln[0]).replace("{email}", ln[1])
                            try:
                                TurboSx_Attach(from_address,ln[1],subject,attach_text,pwd,smtp_server,smtp_port,body_path,attach_text)
                                
                                print("-> Success", end=" : ")
                                print(smtp_server)
                                file_write.write(ln[0]+","+ln[1]+","+ln[2]+","+ln[3]+"\n")
                                file_write_up.write(ln[0]+","+ln[1]+","+ln[2]+","+ln[3]+"\n")
                            except Exception as e:
                                
                                print("-> Fail ", end=" : ")
                                print(smtp_server, end=" \n ")
                                print(e)
                                fcount=fcount+1
                                
                                file_write_f.write(ln[0]+","+ln[1]+","+ln[2]+","+ln[3]+","+smtp_server+","+from_address+"\n")
                                
                        count=count+1
                    file_write.close()
                    file_write_f.close()
                    file_write_up.close()
                    file.close()
                    os.remove(fpath)
                    if(fcount==0):
                        os.remove(wpath_f)
                    
                else:
                    print("Invalid File Extension "+i)
                    os.remove(fpath)
            ftpTransfer(self.outbound_path,ids+"_"+ndate+".csv")
        else:
            print("No Files To Process in inbound")
    def readBuildFiles(self,path):
        file= open(path,'r')
        str=""
        for line in file:
            str=str+line.strip()
        return str
    def writeAttachmentFiles(self,path,name,email,body,now):
        bpath=path+name+now.strftime("%H%M%S")+".html"
        file_write =  open(bpath, 'a+')
        file_write.write(body)
        file_write.close()
        return bpath
        

            
class splitFeeds:
    def __init__(self,feeds_path=sys.argv[1]+"\\feeds",inbound_path=sys.argv[1]+"\\inbound"):
        self.feeds_path=feeds_path
        self.inbound_path=inbound_path
        try:
            self.performSplit()
        except Exception as e:
            print("Error!!! please Review data.csv and email.csv in Feeds Path!")
        print("Split Operation Exit!")

    def performSplit(self):
        file_data= open(self.feeds_path+"\\data.csv",'r')
        file_email= open(self.feeds_path+"\\email.csv",'r')
        count=0
        k=0
        n=int(input("Enter The Data File Record Limit:"))
        ls=file_email.readlines()
        for line_data in file_data:
            
            if(count%(n)==0):
                curr_path=self.inbound_path+"\\"+str(count)+"_"+datetime.now().strftime("%H%M%S")+"_email.csv"
                file_write = open(curr_path, 'a+')
                
                
                
                file_write.write(ls[k].strip()+"\n")
                print(ls[k])
                
                ln=line_data.strip().split(',')
                file_write.write(ln[0]+","+ln[1]+","+ln[2]+","+ln[3]+"\n")
                
                k=(k+1)%len(ls)
                
                
            else:
                file_write = open(curr_path, 'a+')
                ln=line_data.strip().split(',')
                file_write.write(ln[0]+","+ln[1]+","+ln[2]+","+ln[3]+"\n")
            count=count+1
            file_write.close()



x=True
usr=input("Enter User Name:")
ids=input("Enter ID:")
pwd=input("Enter Password:")
#code= requests.get("https://www.rankingsquad.website/smtp_verify.php?NAME={usr}&PWD={pwd}&ID={ids}".format(usr=usr,ids=ids,pwd=pwd)).json()['code']
code='001'

class ftpTransfer:
    def __init__(self,outbound_path,ofile): 
        
        self.outbound_path=outbound_path
        self.ofile=ofile
        

        
#         if os.path.exists(self.outbound_path+"\\"+self.ofile):
#             now = datetime.now()
#             opath=self.outbound_path+"\\"+self.ofile
#             if(self.ofile.endswith('.csv') and self.ofile.startswith(ids) ):
#                 session = ftplib.FTP('82.180.175.90','u692443236.turbo','Rankingsquadisbest@1')
# #                 session.cwd('domains')
# #                 session.cwd('boxyinsider.com')
# #                 session.cwd('public_html')
#                 session.cwd('TurboSx')
#                 ftpflag=0
#                 ftpflag1=0
#                 try:
#                     session.mkd(datetime.now().strftime("%Y%m%d"))
#                 except Exception as e:
#                     ftpflag=1
#                     #print(e)
                
#                 try:
#                     session.cwd(datetime.now().strftime("%Y%m%d"))
#                 except Exception as e:
#                     ftpflag1=1
#                     print(e)
                
#                 if(ftpflag1 == 0):
#                     #print("Finishing File :",self.ofile)
#                     file = open(opath,'rb')
#                     try:
#                         session.storbinary('STOR '+self.ofile, file)
#                     except Exception as e:
#                         print("unFinished File :",self.ofile)
#                     file.close()  
#                 else:
#                     print("Exception has Occurred!")
#                 session.close()



try:

    if (code == '001'):    
        while x:
            print("Select Option:")
            print("Press 1 to Split Files (Feeds -> inbound):")
            print("Press 2 to Shoot(Fast) (inbound -> outbound):")
            print("Press 3 to Shoot(Stable/Slow) (inbound -> outbound):")
            print("Press 4 to Shoot(with Attachments) (inbound -> outbound):")
            print("Press 5 to logout")
            val=input("Enter Option:")

            if (val == "1"):
                print("Option 1")
                splitFeeds()
            elif (val == "2"):
                print("Option 2")
                Shoot()
            elif (val == "3"):
                print("Option 3")
                Shoot_slow()
            elif (val == "4"):
                print("Option 4")
                attach_text=input("Enter Mail Body:")
                attach_text_bkp=attach_text
                attach_etag=input("Enter Sender eMailID Tag:")
                attach_etag_bkp=attach_etag
                Shoot_attach()
            elif(val == "5"):
                print("Option 5")
                #code= requests.get("https://www.rankingsquad.website/smtp_verify.php?NAME={usr}&ID={ids}".format(usr=usr,ids=ids,pwd=pwd)).json()['code']
                x=False
                
                
                
            else:
                print("Invalid Selection")
    elif (code == '002'):
        print("User Already Signed In!")
    elif (code == '009'):
        print("Invalid Credentials!")
    else:
        print("Error Code:"+code)
    
except Exception as e:
    print(e)
    #code= requests.get("https://www.rankingsquad.website/smtp_verify.php?NAME={usr}&ID={ids}".format(usr=usr,ids=ids,pwd=pwd)).json()['code']
        
