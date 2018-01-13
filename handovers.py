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

def formatcandidates(candidates, prefix="until"):
    if len(candidates) > 1:
        return prefix + " either " + " or ".join([prettify(candidate.date()) for candidate in candidates])
    else:
        return prefix + " " + prettify(candidates[0].date())
        
def holidaynights(holidaymap):
    for name, start, end in holidaybounds(holidaymap):
        start = parser.parse(start)
        end = parser.parse(end)
        nights = countnights(start, end)
        prefix = name + ": ({} nights) ".format(nights)
        if "Autumn" in name and "Holiday" in name and start.year % 2 != 0:
            prefix += "Mum "
        else:
            prefix += "Dad "
        prefix += "has first period "
        if not("Summer" in name and "Holiday" in name):
            yield prefix + formatcandidates(generatecandidates(start, end))
        else:
            nextnoon = noon(start)
            sequence = []
            for offset in (14,14,7,7):
                nextnoon += datetime.timedelta(offset)
                sequence.append(prettify(nextnoon.date()))
            sequence = ", ".join(sequence)
            yield prefix + "with handovers " + sequence + " then half of remaining {} nights with Dad ".format(countnights(nextnoon, end)) + formatcandidates(generatecandidates(nextnoon, end), prefix="until final handover")


if __name__ == "__main__":
    import willow
    for item in holidaynights(willow.holidaymap):
        print(item)
