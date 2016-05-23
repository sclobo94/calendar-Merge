from collections import OrderedDict
from datetime import datetime as dt
import difflib
import re
from pyasn1.compat.octets import null

def isSameAs(a, b):
        a=a[1]
        b=b[1]
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
    
f = open("testcalendar.ics", 'rb')
fread=f.readlines()
preamble=[]
i=-1
for line in fread:
    i+=1
    if (line=="BEGIN:VEVENT\n"):
        break
    else:
        preamble.append(line)
        
ending="END:VCALENDAR\n"      
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
 
print len(events)

for event in range(0, len(events)):
    strEvent=events[event]
    date_parsed=parseDate(events[event]) 
    summary_parsed=parseSummary(events[event])
    notes_parsed=parseNotes(events[event])
    events[event]=(date_parsed, summary_parsed, notes_parsed, strEvent)
     
events.sort(key=lambda y: y[0])
 
listloop = 1
i = 0
manualReview = [] #items with same times and notes that need to be reviewed
while(listloop==1):
    if i == len(events)-1:
        listloop=0 
        continue 
    a = events[i]
    b = events[i+1]
    if (a==null or b==null) or (b[0] > a[0]): #if times are different
        i+=1
        continue
    else: #if same time
        if (isSameAs(b, a)==False): #if subject doesn't match
            i+=1
            continue
        else: #if subject does match
            x = a[2].strip()
            y = b[2].strip()
            if x == y : #if notes match
                events[i] = null
                i+=1
                continue
            else:
                if x =="": #if one of the events has empty notes delete
                    events[i] = null
                    i+=1
                    continue
                elif y =="":
                    events[i+1] = null
                    i+=1
                    continue
                else:
                    manualReview.append(a);
                    manualReview.append(b);
                    i+=1    

                    
with open("sortedfull.ics", "wb") as outfile:
    for i in preamble:
        outfile.write(i)
    for i in events:
        if(i!=null):
            outfile.write(i[3])
    outfile.write(ending)
   
outfile.close()

