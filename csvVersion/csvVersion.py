#!usr/bin/python
import csv
import time
from Event import Event
from pyasn1.compat.octets import null


#Sort events and store in list
with open('csvfullcalendar.CSV') as csvfile:
    reader = csv.DictReader(csvfile);
    eventlist=[];
    rownum=0
 
    for row in reader:
            x=Event(row['Subject'], row['Start Date'], row['Start Time'],
                     row['End Date'], row['End Time'], row['All day event'], 
                     row['Reminder on/off'], row['Reminder Date'], 
                     row['Reminder Time'], row['Meeting Organizer'], 
                     row['Required Attendees'], row['Optional Attendees'], 
                     row['Meeting Resources'], row['Billing Information'], 
                     row['Categories'], row['Description'],
                     row['Location'], row['Mileage'],
                     row['Priority'], row['Private'],
                     row['Sensitivity'], row['Show time as'])
            eventlist.append(x);
     
 
csvfile.close()
 
#sort list of events
eventlist.sort(key=lambda y: y.stimeanddate);
# for i in eventlist:
#     i.eventprint() 
#    
# #loop through list of sorted events
listloop = 1
i = 0
manualReview = [] #items with same times and notes that need to be reviewed
while(listloop==1):
    if i == len(eventlist)-1:
        listloop=0 
        continue 
    a = eventlist[i]
    b = eventlist[i+1]
    if (a==null or b==null) or (b.stimeanddate > a.stimeanddate): #if times are different
        i+=1
        continue
    else: #if same time
        if (b.isSameAs(a)==False): #if subject doesn't match
            i+=1
            continue
        else: #if subject does match
            a.description = a.description.strip()
            b.description = b.description.strip()
            if b.description == a.description : #if notes match
                eventlist[i] = null
                i+=1
                continue
            else:
                if a.description=="": #if one of the events has empty notes delete
                    eventlist[i] = null
                    i+=1
                    continue
                elif b.description=="":
                    eventlist[i+1] = null
                    i+=1
                    continue
                else:
                    manualReview.append(a);
                    manualReview.append(b);
                    i+=1
       
# for i in eventlist:
#     if(i!=null):
#         i.eventprint()    
#        
#write updated version to csv
# writeto = open("output.csv", "w")
# header = "Subject,Start Date,Start Time,End Date,End Time,All day event,Reminder on/off,Reminder Date,Reminder Time,Meeting Organizer,Required Attendees,Optional Attendees,Meeting Resources,Billing Information,Categories,Description,Location,Mileage,Priority,Private,Sensitivity,Show time as"
# header += "\n"
# writeto.write(header)
# for i in eventlist:
#     if(i!=null):
#         writeto.write(i.toString() + "\r")
# print "\n--------Manual Review--------" 
# for i in manualReview:  
#     print(i.toString())
# writeto.close()       
with open("manualReview.csv", "w") as writeto:
    writer = csv.writer(writeto, quotechar='"', quoting=csv.QUOTE_ALL)
    writer.writerow(["Subject","Start Date","Start Time","End Date","End Time","All day event","Reminder on/off","Reminder Date","Reminder Time","Meeting Organizer","Required Attendees","Optional Attendees","Meeting Resources","Billing Information","Categories","Description","Location","Mileage","Priority","Private","Sensitivity","Show time as"])
    for i in manualReview:
        writer.writerow(i.toString())
    
    writeto.close()
               
with open("output1.csv", "w") as writeto:
    writer = csv.writer(writeto, quotechar='"', quoting=csv.QUOTE_ALL)
    writer.writerow(["Subject","Start Date","Start Time","End Date","End Time","All day event","Reminder on/off","Reminder Date","Reminder Time","Meeting Organizer","Required Attendees","Optional Attendees","Meeting Resources","Billing Information","Categories","Description","Location","Mileage","Priority","Private","Sensitivity","Show time as"])
    for i in eventlist:
        if(i!=null):
            writer.writerow(i.toString())
    
    writeto.close()
    

       
       
      
      
         
