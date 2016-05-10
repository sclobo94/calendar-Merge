import time
class Event(object):
    
    def __init__(self, subject, startdate, starttime, enddate, endtime, alldayevent, remon, remdate, remtime, meetorg, reqatt, optatt, meetres, billinfo, categor, description, location, mileage, priority, private, sensitivity, showtimeas):
        self.subject = subject
        self.startdate = time.strptime(startdate, "%m/%d/%Y")
        self.starttime = time.strptime(starttime, "%I:%M:%S %p")
        self.enddate = time.strptime(enddate, "%m/%d/%Y")
        self.endtime = time.strptime(endtime, "%I:%M:%S %p")
        self.description = description
        s = startdate + " " + starttime
        self.stimeanddate = time.strptime(s, "%m/%d/%Y %I:%M:%S %p")
        self.alldayevent = alldayevent
        self.remon = remon
        self.remdate = remdate
        self.remtime = remtime
        self.meetorg = meetorg
        self.reqatt = reqatt
        self.optatt = optatt
        self.meetres = meetres
        self.billinfo = billinfo
        self.categor = categor
        self.location = location
        self.mileage = mileage
        self.priority = priority
        self.private = private
        self.sensitivity = sensitivity
        self.showtimeas = showtimeas
        
        
        
    def eventprint(self):
        print ('(%s, %s, %s, %s, %s, %s)' % (self.subject, time.strftime("%m/%d/%Y", self.startdate), time.strftime("%I:%M:%S %p", self.starttime), time.strftime("%m/%d/%Y", self.enddate), time.strftime("%I:%M:%S %p", self.endtime), self.description))
      
    def toString(self):
        return self.subject + "," + time.strftime("%m/%d/%Y", self.startdate) + "," + time.strftime("%I:%M:%S %p", self.starttime) + "," + time.strftime("%m/%d/%Y", self.enddate) + "," + time.strftime("%I:%M:%S %p", self.endtime) + "," + self.alldayevent + "," + self.remon + "," + self.remdate + "," + self.remtime + "," + '"%s"' % self.meetorg + "," + self.reqatt + "," + self.optatt + "," + self.meetres + "," + self.billinfo + "," + self.categor + "," + ''"%s"'' % self.description + "," + self.location + "," + self.mileage + "," + self.priority + "," + self.private + "," + self.sensitivity + "," + self.showtimeas