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
    
f = open("testyear2016.ics", 'rb')
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
    location_parsed=parseLocation(events[event])
    uid_parsed=parseUID(events[event])
    if (checkSeries(events[event]) == True):
        series=True
        serieslist.append((date_parsed, summary_parsed, notes_parsed, location_parsed, uid_parsed, strEvent))
    if series==False:
        eventlist.append((date_parsed, summary_parsed, notes_parsed, location_parsed, uid_parsed, strEvent))

eventlist.sort(key=lambda y: y[0])
serieslist.sort(key=lambda y: y[4])
# with open("compare1.txt", "wb") as write1:
#     for i in serieslist:
#         write1.write(i[5])
#     for i in eventlist:
#         write1.write(i[5])
#         
# write1.close()
manualReview=[]

listloop = 1
i = 0
while(listloop==1):
    if i == len(serieslist)-1:
        listloop=0 
        continue 
    a = serieslist[i]
    b = serieslist[i+1]
    if (a==null or b==null) or (a[4] != b[4]): #if times are different
        i+=1
        continue
    else: #if same UID
        if (isSameAs(b, a)==False): #if subject doesn't match
            i+=1
            continue
        else: #if subject does match
            x = a[2].strip()
            y = b[2].strip()
            if x == y : #if notes match
                serieslist[i] = null
                i+=1
                continue
            else:
                if x =="": #if one of the events has empty notes delete
                    serieslist[i] = null
                    i+=1
                    continue
                elif y =="":
                    serieslist[i+1] = null
                    i+=1
                    continue
                else:
                    manualReview.append(a);
                    manualReview.append(b);
                    i+=1
                    
#ADD CLEANED SERIES TO CLEANED LIST
cleanedSeries=[]
cleanedRecurr=[]
for i in serieslist:
    if i is not null:
        cleanedSeries.append(i)
        
        
        
for i in range(0, len(cleanedSeries)):
    if cleanedSeries[i] in manualReview:
        continue
    recurrence=[]
    a = cleanedSeries[i]
    for j in range(0, len(eventlist)):
        b = eventlist[j]
        if (a==null or b==null) or (a[4] != b[4]):
            continue
        else: #uid of series matches one in eventlist
            recurrence.append(b)
            eventlist[j] = null
    if (len(recurrence) > 1):
        listloop = 1
        p = 0
        while(listloop==1):
            if p == len(recurrence)-1:
                listloop=0 
                continue 
            a = recurrence[p]
            b = recurrence[p+1]
            if (a==null or b==null) or (a[0] > b[0]): #if times are different
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
                        manualReview.append(a)
                        manualReview.append(b)
                        p+=1
                    elif (isSameAs(b[2], a[2])==True): #if notes match
                        recurrence[p] = null
                        p+=1
                        continue
                    else:
                        if x =="": #if one of the events has empty notes delete
                            recurrence[p] = null
                            p+=1
                            continue
                        elif y =="":
                            recurrence[p+1] = null
                            p+=1
                            continue
                        else:
                            manualReview.append(a);
                            manualReview.append(b);
                            p+=1
    for l in recurrence: ## ADD CLEANED RECURR TO CLEANED LIST
        if l is not null:
            cleanedRecurr.append(l)                      

for i in eventlist:
    if i is not null:
        cleanedRecurr.append(i)      


cleanedEvents = cleanedSeries+cleanedRecurr
cleanedEvents.sort(key=lambda y: y[1])

listloop = 1
i = 0
while(listloop==1):
    if i == len(cleanedEvents)-1:
        listloop=0 
        continue 
    a = cleanedEvents[i]
    b = cleanedEvents[i+1]
    if (a==null or b==null) or (a[0] > b[0]): #if times are different
        i+=1
        continue
    else: #if same time
        if (isSameAs(b, a)==False): #if subject doesn't match
            i+=1
            continue
        else: #if subject does match
            x = a[2].strip()
            y = b[2].strip()
            if (a[3] != b[3]): #if location is different, add to manual review
                if a not in manualReview:
                    manualReview.append(a)
                if b not in manualReview:
                    manualReview.append(b)
                i+=1
            elif x == y : #if notes match
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
                    if a not in manualReview:
                        manualReview.append(a)
                    if b not in manualReview:
                        manualReview.append(b)
                    i+=1

with open("sortedfull2016.ics", "wb") as outfile:
    for i in preamble:
        outfile.write(i)
    for i in cleanedEvents:
        if(i!=null):
            outfile.write(i[5])
    outfile.write(ending)
     
outfile.close()

for i in manualReview:
    print i
    
with open("manualReview2016.ics", "wb") as manfile:
    for i in preamble:
        manfile.write(i)
    for i in manualReview:
        manfile.write(i[5])
    manfile.write(ending)
     
manfile.close()






















# manualReview = [] #items with same times and notes that need to be reviewed
# occurences=[]
# cleanedEvents=[]

# for k in range(0, len(serieslist)):
#     if (k > 0) and (serieslist[k] != null) and (serieslist[k-1] != null):
#         if (serieslist[k][3] == serieslist[k-1][3]):
#             serieslist[k] = null
#     if serieslist[k] == null:
#         continue
#     for j in eventlist:
#         if (serieslist[k][3] == j[3]):
#             occurences.append(j)
#             j=null
#     if len(occurences) == 0 or len(occurences) == 1:
#         continue
#     elif len(occurences) > 1:
#         listloop = 1
#         i = 0
#         while(listloop==1):
#             if i == len(occurences)-1:
#                 listloop=0 
#                 continue 
#             a = occurences[i]
#             b = occurences[i+1]
#             if (a==null or b==null) or (b[0] > a[0]): #if times are different
#                 i+=1
#                 continue
#             else: #if same time
#                 if (isSameAs(b, a)==False): #if subject doesn't match
#                     i+=1
#                     continue
#                 else: #if subject does match
#                     x = a[2].strip()
#                     y = b[2].strip()
#                     if x == y : #if notes match
#                         occurences[i] = null
#                         i+=1
#                         continue
#                     else:
#                         if x =="": #if one of the events has empty notes delete
#                             occurences[i] = null
#                             i+=1
#                             continue
#                         elif y =="":
#                             occurences[i+1] = null
#                             i+=1
#                             continue   
#     for i in occurences:
#         if (i!=null):
#             cleanedEvents.append(i)
# 
# for i in serieslist:
#     if i != null:
#         cleanedEvents.append(i)
#     
# for i in eventlist:
#     if i!= null:
#         cleanedEvents.append(i)
# 
# cleanedEvents.sort(key=lambda y: y[0])    
# listloop = 1
# i = 0
# while(listloop==1):
#     if i == len(cleanedEvents)-1:
#         listloop=0 
#         continue 
#     a = cleanedEvents[i]
#     b = cleanedEvents[i+1]
#     if (a==null or b==null) or (b[0] > a[0]): #if times are different
#         i+=1
#         continue
#     else: #if same time
#         if (isSameAs(b, a)==False): #if subject doesn't match
#             i+=1
#             continue
#         else: #if subject does match
#             x = a[2].strip()
#             y = b[2].strip()
#             if x == y : #if notes match
#                 cleanedEvents[i] = null
#                 i+=1
#                 continue
#             else:
#                 if x =="": #if one of the events has empty notes delete
#                     cleanedEvents[i] = null
#                     i+=1
#                     continue
#                 elif y =="":
#                     cleanedEvents[i+1] = null
#                     i+=1
#                     continue
#                 else:
#                     manualReview.append(a);
#                     manualReview.append(b);
#                     i+=1    
#     
# for i in cleanedEvents:
#     if i != null:
#         print i    
#  
#                      
# with open("sortedfull2016.ics", "wb") as outfile:
#     for i in preamble:
#         outfile.write(i)
#     for i in cleanedEvents:
#         if(i!=null):
#             outfile.write(i[4])
#     outfile.write(ending)
#     
# outfile.close()
# 
# with open("manualReview2016.ics", "wb") as manfile:
#     for i in preamble:
#         manfile.write(i)
#     for i in manualReview:
#         manfile.write(i[4])
#     manfile.write(ending)
#     
# manfile.close()
