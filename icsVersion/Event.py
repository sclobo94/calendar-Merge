import difflib
import datetime





class Event(object):
    def __init__(self):
        self.summary = None
        self.description = None
        self.dtstart = None
        self.dtend = None
        self.uid = None
        self.dtstamp = None
        
        
    def event_Print(self):
        print (self.summary, self.dtstart, self.dtend, self.description, self.uid)
      
      
    def isSameAs(self, other):
        a=self.summary
        b=other.summary
        seq=difflib.SequenceMatcher(None, a,b)
        d=seq.ratio()*100
        if (d > 40):
            return True
        else:
            return False
        
    