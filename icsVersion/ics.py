from collections import OrderedDict
from datetime import datetime as dt
import difflib
import re
from pyasn1.compat.octets import null


def isSameAs(a, b):
        seq=difflib.SequenceMatcher(None, a,b)
        d=seq.ratio()*100
        if (d > 40):
            return True
        else:
            return False
        
def parseDate(string):
    try:
        p = r'\bDTSTART;\D*(\d+).(\d+)'
        q = r'\bDTSTART:\D*(\d+).(\d+)'
        s = r'\bDTSTART;\D*(\d+)(\d+)'
        r = r'\bDTSTART;\S*:(\d+).(\d+)'
        t=re.search(p, string)
        u=re.search(q, string)
        v=re.search(s, string)
        w=re.search(r, string)
        if(t != None) and (len(t.group(1)+t.group(2))==14):
            return dt.strptime(t.group(1)+t.group(2), "%Y%m%d%H%M%S")
        elif (u != None) and (len(u.group(1)+u.group(2))==14):
            temp = dt.strptime(u.group(1)+u.group(2), "%Y%m%d%H%M%S")
            temp = temp.replace(hour=0, minute=0, second=0)
            return temp
        elif (w != None) and (len(w.group(1)+w.group(2))==14):
            return dt.strptime(w.group(1)+w.group(2), "%Y%m%d%H%M%S")
        else:
            temp = dt.strptime(v.group(1)+v.group(2), "%Y%m%d")
            temp = temp.replace(hour=0, minute=0, second=0)
            return temp
    except AttributeError:
        print string
def parseSummary(string):
    p = r'\bSUMMARY[^:]*:([^\n\r]*)'
    t = re.search(p, string)
    if (t==None):
        return null   
    else:
        return t.group(1)
    
def parseNotes(string):
    p = r'(DESCRIPTION:)([\S\s]*)(DTEND)'
    t = re.search(p, string)
    if (t==None):
        return null   
    else:
        return t.group(2)
    
def parseUID(string):
    p = r'\bUID:(\S*)'
    q = r'\bUID:(\S*\s*\S*)'
    t = re.search(p, string)
    v = re.search(q, string)
    if (t==None) or (len(t.group(1))>36):
        return v.group(1)
    else:
        return t.group(1)
    
def parseLocation(string):
    p = r'\bLOCATION\b:(.*\s*)\bPRIORITY\b'
    t = re.search(p, string)
    if (t==None):
        return null
    else:
        return t.group(1)  
      
def checkSeries(string):
    p = r'(RRULE:)'
    t = re.search(p, string)
    if (t!=None):
        return True
    else:
        return False

def parseRRULE(string):
    freq = r'\bFREQ=([^;|\s]*)'
    byday = r'\bBYDAY=([^;|\s]*)'
    bymonth = r'\bBYMONTH=([^;|\s]*)'
    bymonthday=r'\bBYMONTHDAY=([^;|\s]*)'
    bysetpos = r'\bBYSETPOS=([^;|\s]*)'
    p = re.search(freq, string)
    q = re.search(byday, string)
    r = re.search(bymonth, string)
    s = re.search(bymonthday, string)
    t = re.search(bysetpos, string)
    rrule = ""
    if p != None:
        rrule+=p.group(1)
    if q != None:
        rrule+=q.group(1)
    if r != None:
        rrule+=r.group(1)
    if s != None:
        rrule+=s.group(1)
    if t != None:
        rrule+=t.group(1)

    return rrule

def subUID(string, event):
    uid = string
    x = event[5]
    text, numreplaced = re.subn(r'\bUID:(\S*\s*\S*)', "UID:"+uid, x)
    if numreplaced:
        return text
    else:
        text2, numreplaced1 = re.subn(r'\bUID:(\S*)', "UID:"+uid, x)
        if numreplaced1:
            return text2
        else:
            raise NameError("Oops") 
           
f = open("testcalendarfull.ics", 'rb')
fread=f.readlines()
preamble=[]
i=-1
for line in fread:
    i+=1
    if (line=="BEGIN:VEVENT\n"):
        break
    else:
        preamble.append(line)
        
ending="END:VCALENDAR\r\n"      
eventstring=""
events=[]
eventBegin = False

while(i<len(fread)):
    if (fread[i] == "BEGIN:VEVENT\n"):
        eventBegin=True
    if (fread[i] == "END:VEVENT\n"):
        eventstring+=fread[i]
        events.append(eventstring)
        eventstring=""
        eventBegin=False
    elif eventBegin==True:
        eventstring+=fread[i]
    i+=1
 
serieslist = []
eventlist = []

###### PARSE EVENTS AND ADD TO LISTS (SERIES/OCCURENCE)
for event in range(0, len(events)):
    series=False
    strEvent=events[event]
    date_parsed=parseDate(events[event]) 
    summary_parsed=parseSummary(events[event])
    notes_parsed=parseNotes(events[event])
    location_parsed=parseLocation(events[event])
    uid_parsed=parseUID(events[event])
    if (checkSeries(events[event]) == True):
        series = True
        rrule_parsed=parseRRULE(events[event]) + date_parsed.strftime("%H%M%S")
        serieslist.append([date_parsed, summary_parsed, notes_parsed, location_parsed, uid_parsed, strEvent, rrule_parsed])
    if (series == False):
        eventlist.append([date_parsed, summary_parsed, notes_parsed, location_parsed, uid_parsed, strEvent])

eventlist.sort(key=lambda y: y[0]) #sort eventlist by date
serieslist.sort(key=lambda y: y[6]) #sort series list by rrule
manualReview = []

listloop = 1 ##CLEAN DUPLICATES IN EVENTLIST
p = 0
while(listloop==1):
    if p == len(eventlist)-1:
        listloop=0 
        continue 
    a = eventlist[p]
    b = eventlist[p+1]
    if (a==null or b==null): 
        p+=1
        continue
    if (a[0] < b[0]):
        p+=1
        continue
    else: #if same TIME
        if (isSameAs(b[1], a[1])==False): #if subject doesn't match
            p+=1
            continue
        else: #if subject does match
            x = a[2].strip()
            y = b[2].strip()
            if (a[3] != b[3]): #if location is different, add to manual review
                if a not in manualReview:
                        manualReview.append(a)
                if b not in manualReview:
                    manualReview.append(b)
                p+=1
            elif (isSameAs(b[2], a[2])==True): #if notes match
                eventlist[p] = null
                p+=1
                continue
            else:
                if x =="": #if one of the events has empty notes delete
                    eventlist[p] = null
                    p+=1
                    continue
                elif y =="":
                    eventlist[p+1] = null
                    p+=1
                    continue
                else:
                    if a not in manualReview:
                        manualReview.append(a)
                    if b not in manualReview:
                        manualReview.append(b)
                    p+=1


listloop=1
i=0
while(listloop):
    if i == len(serieslist)-1:
        listloop=0 
        continue 
    a = serieslist[i]
    b = serieslist[i+1]
    if a==null or b==null:
        i+=1
        continue
    if a[6] != b[6]:
        i+=1
        continue
    else:
        if isSameAs(a[1], b[1]) == False:
            i+=1
            continue
        else:
            if (a[3] != b[3]): #if locations are different
                if a not in manualReview:
                        manualReview.append(a)
                if b not in manualReview:
                    manualReview.append(b)
                i+=1
                continue
            else:
                if a[2] == "" or (isSameAs(a[2], b[2])):
                    for j in range(0, len(eventlist)):
                        c = eventlist[j]
                        if c==null or a[4] != c[4]:
                            continue
                        else:
                            eventlist[j][4]=subUID(b[4], c)
                    serieslist[i] = null
                    i+=1
                    continue
                elif b[2] == "":
                    for j in range(0, len(eventlist)):
                        c = eventlist[j]
                        if c==null or b[4] != c[4]:
                            continue
                        else:
                            eventlist[j][4]=subUID(a[4], c)
                    serieslist[i+1] = null
                    i+=1
                    continue
                else:
                    if a not in manualReview:
                        manualReview.append(a)
                    if b not in manualReview:
                        manualReview.append(b)
                    i+=1
                      
cleanedEvents=[]

for i in serieslist:
    if i is not null:
        cleanedEvents.append(i)
for i in eventlist:
    if i is not null:
        cleanedEvents.append(i)
        
curr = len(manualReview)
for i in cleanedEvents:
    a=i[4]
    for j in range(0, curr):
        if manualReview[j][4] == a:
            if i not in manualReview:
                manualReview.append(i)
    
with open("sortedfull.ics", "wb") as outfile:
    for i in preamble:
        outfile.write(i)
    for i in cleanedEvents:
        if(i!=null):
            outfile.write(i[5])
    outfile.write(ending)
       
outfile.close()
  
with open("manualReviewfull.ics", "wb") as manfile:
    for i in preamble:
        manfile.write(i)
    for i in manualReview:
        manfile.write(i[5])
    manfile.write(ending)
       
manfile.close()          
               
     
     
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
 