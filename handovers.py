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


def holidaynights(holidaymap):
    for holidayName, start, end in holidaybounds(holidaymap):
        start = parser.parse(start)
        end = parser.parse(end)
        totalNights = countnights(start, end)
        startString = prettify(start)
        endString = prettify(end)
        mumFirst = (
            ("Autumn" in holidayName and "Holiday" in holidayName and start.year % 2 != 0) or 
            ("Summer" in holidayName and "Holiday" in holidayName)
        )
        firstParent = "Mum" if mumFirst else "Dad"
        secondParent = "Dad" if mumFirst else "Mum"
        pattern = "{holidayName}: ({totalNights} nights) {firstParent} has first period starting {startString} "
        if "Summer" in holidayName and "Holiday" in holidayName:
            nextnoon = noon(start)
            sequenceDates = []
#            for offset in (14,14,7,7):
            for offset in (7,7,14,14):
                nextnoon += datetime.timedelta(offset)
                sequenceDates.append(nextnoon.date())
            sequenceSummary = ", ".join([prettify(date) for date in sequenceDates])
            surplusNights = countnights(nextnoon, end)
            finalHandover = formatcandidates(generatecandidates(nextnoon, end))
            pattern += "with handovers {sequenceSummary} then half of remaining {surplusNights} nights with {secondParent} until handover {finalHandover}. "
        else:
            sequenceSummary = formatcandidates(generatecandidates(start, end))
            pattern += "with handover {sequenceSummary}. "        
        pattern += "Holiday ends {endString}"
        yield pattern.format(**locals())


if __name__ == "__main__":
    import willow
    for item in holidaynights(willow.holidaymap):
        print(item)
