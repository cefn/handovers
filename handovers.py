from math import floor
import datetime
from dateutil import parser
import calendar

'''
Basic principle: Calculate number of nights between start and end.

Calculate rounded half of nights (rounding down for odd numbers).

Count rounded half forward from start date.
Count rounded half backward from end date.

If the dates are the same, there is only one candidate date.
If the dates are different, there are two candidate dates.
'''

weekdays = list(calendar.day_name)

def sorteditems(holidaymap):
    return sorted(holidaymap.items(), key=lambda entry: entry[1]["termstart"])

def holidaybounds(holidaymap):
    items = sorteditems(holidaymap)
    for pos, (name, holiday) in enumerate(items):
        yield (name + " Half Term", holiday["halfstart"], holiday["halfend"])
        if pos < len(items) - 1:
            nextname, nextholiday = items[pos + 1]
            yield (name + " Holiday", holiday["termend"], nextholiday["termstart"])

def noon(moment):
    return datetime.datetime(moment.year, moment.month, moment.day, hour=12, minute=0)

def prettify(date):
    return date.strftime("%a, %d %b %Y")

'''
        else:
            nextnoon = startnoon
            sequence = []
            for offset in (14,14,7,7):
                nextnoon += datetime.timedelta(offset)
                sequence.append(nextnoon)            
            yield prefix " handovers; " startnoon +     
'''


def countnights(starttime, endtime):
    startnoon = noon(starttime)
    endnoon = noon(endtime)
    diff = endnoon - startnoon
    return diff.days

def midpoints(starttime, endtime):
    startnoon = noon(starttime)
    endnoon = noon(endtime)
    nights = countnights(starttime, endtime)
    half = nights / 2
    roundeddelta = datetime.timedelta(days=floor(half))
    earlynoon = startnoon + roundeddelta
    latenoon = endnoon - roundeddelta
    return sorted((set((earlynoon, latenoon))))
    
def trimcandidates(candidates):
	"""selects according to earliest in alphabet (selects by weekday name, earliest alphabetically wins)"""
	if len(candidates) == 1:
		return candidates
	elif len(candidates) == 2:
		# create pairs containing the weekday name in first position, and the candidate date in the second position
		pairs = [(weekdays[candidate.weekday()], candidate) for candidate in candidates]
		sortedpairs = sorted(pairs)		# sort by the first entry in the list (the name of the weekday)
		selectedpair = sortedpairs[0] 	# selected pair should be the first in the alphabetical sort
		candidate = selectedpair[1] 	# candidate date is second item in pair
		return [candidate] 				# trim list to contain just this candidate 
	else:
		raise Error("Midpoint has at most two candidate dates")
	
    
def generatecandidates(starttime, endtime):
	return trimcandidates(midpoints(starttime, endtime))
#	return midpoints(starttime, endtime)

def formatcandidates(candidates):
    if len(candidates) > 1:
        return "either " + " or ".join([prettify(candidate.date()) for candidate in candidates])
    else:
        return prettify(candidates[0].date())

def parentSequence(holidayName, start, end):
        if  (   ("Autumn" in holidayName and "Holiday" in holidayName and start.year % 2 != 0) or 
                ("Summer" in holidayName and "Holiday" in holidayName)  ):
            return "Mum", "Dad"
        else:
            return "Dad", "Mum"

def dateSequence(holidayName, start, end):
    sequenceDates = []
    sequenceDates.append(start)
    
    if not("Summer" in holidayName and "Holiday" in holidayName): # handover splitting whole holiday
        sequenceDates.append(generatecandidates(start, end)[0])
    else: # handover splitting into week each, fortnight each, split remainder
        nextnoon = noon(start)
        # for offset in (14,14,7,7):
        for offset in (7,7,14,14): # week and fortnight handovers
            nextnoon += datetime.timedelta(offset)
            sequenceDates.append(nextnoon.date())
        sequenceDates.append(generatecandidates(nextnoon, end)[0]) #handover splitting remaining time
    
    sequenceDates.append(end)
    
    return sequenceDates
    
def writeical(holidaymap):
    
    from icalendar import Calendar, Event, vCalAddress, vText

    cal = Calendar()

    organizer = vCalAddress('MAILTO:cefn@cefn.com')
    location = vText('Handovers from school or at Wetherspoons')
    
    for holidayName, start, end in holidaybounds(holidaymap):
        start = parser.parse(start)
        end = parser.parse(end)
        
        parents = parentSequence(holidayName, start, end)
        sequenceDates = dateSequence(holidayName, start, end)
        
        for beginIndex in range(len(sequenceDates) - 1):
            parent = parents[beginIndex % 2]    
            beginDate, endDate = sequenceDates[beginIndex:beginIndex + 2]
            
            event = Event()
            event.add('summary', 'Holiday with ' + parent)
            event.add('dtstart', beginDate)
            event.add('dtend', endDate)
            #event.add('location', "The other side of the moon")
            #event.add('organizer', organizer)
            #event['uid'] = '20050115T101010/27346262376@mxm.dk'

            cal.add_component(event)

    return cal

def holidaynights(holidaymap):
    for holidayName, start, end in holidaybounds(holidaymap):
        start = parser.parse(start)
        end = parser.parse(end)
        
        sequenceDates = dateSequence(holidayName, start, end)

        # figure out pattern
        pattern = "{holidayName}: ({totalNights} nights) {firstParent} has first period starting {startString} "
        
        if len(sequenceDates) == 3: # Normal holiday
            handoverSummary = formatcandidates([sequenceDates[1]])
            pattern += "with handover {handoverSummary}. "        
        else:
            handoverSummary = ", ".join([prettify(date) for date in sequenceDates[1:-2]])
            surplusNights = countnights(sequenceDates[-3], sequenceDates[-1])
            finalHandover = formatcandidates([sequenceDates[-2]])
            pattern += "with handovers {handoverSummary} then half of remaining {surplusNights} nights with {secondParent} until handover {finalHandover}. "

        pattern += "Holiday ends {endString}"
        
        # populate local calculated values
        totalNights = countnights(start, end)
        startString, endString = prettify(start), prettify(end)
        firstParent, secondParent = parentSequence(holidayName, start, end)
        
        # use local values to populate pattern
        yield pattern.format(**locals())


if __name__ == "__main__":
    import willow

    with open("handovers.txt", 'w') as f:
        for line in holidaynights(willow.holidaymap):
            f.write(line + "\n")

    cal = writeical(willow.holidaymap)
    cal_content = cal.to_ical()
    with open("handovers.ics", 'wb') as f:
        f.write(cal_content)

