#!usr/bin/python
from icalendar import Calendar
from Event import Event
import datetime 
from datetime import date
from datetime import datetime as dt
import pytz
from pytz import timezone
from pyasn1.compat.octets import null
from icalendar.parser import tzid_from_dt
import re


def summary_Parse(summary):
        p = re.compile('/\(([^)]+)\)/')
        x=p.search(summary)
        return x
    
EST = timezone('US/Eastern')


#Sort events and store in list
f = open("Goldbart Paul M Smaller.ics", 'rb')
cal = Calendar.from_ical(f.read())
eventlist=[]

for event in cal.walk('VEVENT'):
    s = Event()
    if "SUMMARY" in event:
        s.summary = event["SUMMARY"]
    if "DESCRIPTION" in event:
        s.description = str(event["DESCRIPTION"])
    if "DTSTART" in event:
        x = event["DTSTART"].dt
        if isinstance(x, datetime.datetime):
            s.dtstart = event["DTSTART"].dt
        else:
            x = dt.combine(event["DTSTART"].dt, dt.min.time())
            s.dtstart=x.replace(tzinfo=EST)
#         
    if "DTEND" in event:
            s.dtend = event["DTEND"].dt
 
    eventlist.append(s)
    
    
f.close()

# #sort list of events
eventlist.sort(key=lambda y: y.dtstart);
for i in eventlist:
    i.event_Print()
      
# # #loop through list of sorted events
listloop = 1
i = 0
manualReview = [] #items with same times and notes that need to be reviewed
while(listloop==1):
    if i == len(eventlist)-1:
        listloop=0 
        break
    a = eventlist[i]
    b = eventlist[i+1]
    if b.dtstart > a.dtstart: #if times are different
        i+=1
        continue
    else: #if same time
        if ((a.summary!=None and b.summary!=None) and b.isSameAs(a)==False): #if subject doesn't match
            i+=1
            continue
        else: #if subject does match
            if b.description == a.description : #if notes match
                eventlist[i] = null
                i+=1
                continue
            else:
                if b.description==None: #if one of the events has empty notes delete
                    eventlist[i+1] = null
                    i+=1
                    continue
                elif a.description==None:
                    eventlist[i] = null
                    i+=1
                    continue
                else:
                    manualReview.append(a);
                    manualReview.append(b);
                    i+=1
         
for i in manualReview:
    i.event_Print
      
# #                
# # with open("output1.csv", "w") as writeto:
# #     writer = csv.writer(writeto, quotechar='"', quoting=csv.QUOTE_ALL)
# #     writer.writerow(["Subject","Start Date","Start Time","End Date","End Time","All day event","Reminder on/off","Reminder Date","Reminder Time","Meeting Organizer","Required Attendees","Optional Attendees","Meeting Resources","Billing Information","Categories","Description","Location","Mileage","Priority","Private","Sensitivity","Show time as"])
# #     for i in eventlist:
# #         if(i!=null):
# #             writer.writerow(i.toString())
# #     
# #     writeto.close()
# #     
# # print "\n--------Manual Review--------" 
# # for i in manualReview:  
# #     print(i.toString())      
# #            
# #         
# #        
# #        
# #        
# #       
# #       
# #          
