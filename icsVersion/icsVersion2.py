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
    
def parseUID(string):
    p = r'\bUID:(\S*)'
    q = r'\bUID:(\S*\s*\S*)'
    t = re.search(p, string)
    v = re.search(q, string)
    if (t==None) or (len(t.group(1))>36):
        return v.group(1)
    else:
        return t.group(1)
    
def checkSeries(string):
    p = r'(RRULE:)'
    t = re.search(p, string)
    if (t!=None):
        return True
    else:
        return False
    
f = open("Goldbart Paul M Smaller.ics", 'rb')
fread=f.readlines()
preamble=[]
i=-1
for line in fread:
    i+=1
    if (line=="BEGIN:VEVENT\r\n"):
        break
    else:
        preamble.append(line)
        
ending="END:VCALENDAR\r\n"      
eventstring=""
events=[]
eventBegin = False

while(i<len(fread)):
    if (fread[i] == "BEGIN:VEVENT\r\n"):
        eventBegin=True
    if (fread[i] == "END:VEVENT\r\n"):
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
    uid_parsed=parseUID(events[event])
    if (checkSeries(events[event]) == True):
        series=True
        serieslist.append((date_parsed, summary_parsed, notes_parsed, uid_parsed, strEvent))
    if series==False:
        eventlist.append((date_parsed, summary_parsed, notes_parsed, uid_parsed, strEvent))

eventlist.sort(key=lambda y: y[3])
serieslist.sort(key=lambda y: y[0])        
print len(eventlist)     
print len(serieslist)

manualReview = [] #items with same times and notes that need to be reviewed
occurences=[]
cleanedEvents=[]

for k in range(0, len(serieslist)):
    if (k > 0) and (serieslist[k] != null) and (serieslist[k-1] != null):
        if (serieslist[k][3] == serieslist[k-1][3]):
            serieslist[k] = null
    if serieslist[k] == null:
        continue
    for j in eventlist:
        if (serieslist[k][3] == j[3]):
            occurences.append(j)
    if len(occurences) == 0 or len(occurences) == 1:
        continue
    elif len(occurences) > 1:
        listloop = 1
        i = 0
        while(listloop==1):
            if i == len(occurences)-1:
                listloop=0 
                continue 
            a = occurences[i]
            b = occurences[i+1]
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
                        occurences[i] = null
                        i+=1
                        continue
                    else:
                        if x =="": #if one of the events has empty notes delete
                            occurences[i] = null
                            i+=1
                            continue
                        elif y =="":
                            occurences[i+1] = null
                            i+=1
                            continue   
    for i in occurences:
        if (i!=null):
            cleanedEvents.append(i)

for i in serieslist:
    if i != null:
        cleanedEvents.append(i)
    

listloop = 1
i = 0
while(listloop==1):
    if i == len(cleanedEvents)-1:
        listloop=0 
        continue 
    a = cleanedEvents[i]
    b = cleanedEvents[i+1]
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
                cleanedEvents[i] = null
                i+=1
                continue
            else:
                if x =="": #if one of the events has empty notes delete
                    cleanedEvents[i] = null
                    i+=1
                    continue
                elif y =="":
                    cleanedEvents[i+1] = null
                    i+=1
                    continue
                else:
                    manualReview.append(a);
                    manualReview.append(b);
                    i+=1    
    
for i in cleanedEvents:
    if i != null:
        print i    
 
                     
with open("sortedfull.ics", "wb") as outfile:
    for i in preamble:
        outfile.write(i)
    for i in cleanedEvents:
        if(i!=null):
            outfile.write(i[4])
    outfile.write(ending)
    
outfile.close()

with open("manualReview.ics", "wb") as manfile:
    for i in preamble:
        manfile.write(i)
    for i in manualReview:
        manfile.write(i[4])
    manfile.write(ending)
    
manfile.close()
