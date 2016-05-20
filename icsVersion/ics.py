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
f = open("testcalendar.ics", 'rb')
fread=f.readlines()
preamble=[]
for i in fread:
    if (i=="BEGIN:VEVENT\r\n"):
        break
    else:
        preamble.append(i)
 
ending="END:VCALENDAR\r\n"
f.close()

f = open("testcalendar.ics", 'rb')

cal = Calendar.from_ical(f.read())
eventlist=[]
serieslist=[]
 
for event in cal.walk('VEVENT'):
    s = Event()
    if "SUMMARY" in event:
        s.summary = event.decode("SUMMARY")
    if "DESCRIPTION" in event:
        s.description = event.decode("DESCRIPTION")
    if "DTSTART" in event:
        x = event.decode("DTSTART").dt
        if isinstance(x, datetime.datetime):
            s.dtstart = event["DTSTART"].dt
        else:
            x = dt.combine(event["DTSTART"].dt, dt.min.time())
            s.dtstart=x.replace(tzinfo=EST)   
    if "DTEND" in event:
        s.dtend = event["DTEND"].dt
    if "UID" in event:
        s.uid = event["UID"].encode('utf-8')
    
    if "DTSTAMP" in event:
        s.dtstamp=event["DTSTAMP"].dt
    if s.summary==None and s.description==None:
        continue
    elif "RRULE" in event:
        serieslist.append(s)
    else:
        eventlist.append(s)
     
f.close()

# #sort list of events
serieslist.sort(key=lambda z: z.summary)
eventlist.sort(key=lambda y: y.dtstart);
# for i in eventlist:
#     i.event_Print()

# with open("checkfile.txt", "wb") as test:
#     for i in eventlist:
#         test.write(i.event_Print())
        
# # # # # #loop through list of sorted events
listloop = 1
i = 0
manualReview = [] #items with same times and notes that need to be reviewed
excludelist = [] #stores items uids that need to be skipped when writing
while(listloop==1):
    if i == len(eventlist)-1:
        listloop=0 
        break
    a = eventlist[i]
    b = eventlist[i+1]
    if (a==null or b==null) or (b.dtstart > a.dtstart): #if times are different
        i+=1
        continue
    else: #if same time
        if ((a.summary!=None and b.summary!=None) and b.isSameAs(a)==False): #if subject doesn't match
            i+=1
            continue
        else: #if subject does match
            if b.description == a.description : #if notes match
                excludelist.append([eventlist[i].uid, eventlist[i].dtstamp])
                eventlist[i] = null
                i+=1
                continue
            else:
                if b.description==None: #if one of the events has empty notes delete
                    excludelist.append([eventlist[i+1].uid, eventlist[i+1].dtstamp])
                    eventlist[i+1] = null
                    i+=1
                    continue
                elif a.description==None:
                    excludelist.append([eventlist[i].uid, eventlist[i].dtstamp])
                    eventlist[i] = null
                    i+=1
                    continue
                else:
                    manualReview.append(a);
                    manualReview.append(b);
                    i+=1
                
# # for i in excludelist:
# #     print i
# #           
# # print "\n\n\n"
# #   
for i in manualReview:
    i.event_Print()

print len(manualReview)    
print len(excludelist)
# with open('outputics.ics', 'wb') as outfile:  
#     for row in preamble:
#         outfile.write(row)
#     for event in cal.walk("VEVENT"):
#         if "DTSTAMP" not in event:
#             outfile.write(event.to_ical())
#         elif ([event["UID"].encode("utf-8"), event["DTSTAMP"].dt] in excludelist):
#                 continue
#         else:
#             outfile.write(event.to_ical())
#     outfile.write(ending)
#            
# outfile.close()

