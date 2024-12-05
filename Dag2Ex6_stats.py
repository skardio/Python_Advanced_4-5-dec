# This function calculates and returns the mean, median and mode of a list of numbers.
def central_measures(numbers):
    # The mean is calculated.
    mean = sum(numbers)/len(numbers)

    # The median is calculated.
    median = 0.0
    lstSortedNumbers = sorted(numbers)
    if len(lstSortedNumbers) % 2 == 1:
        indexMiddle = int(len(lstSortedNumbers) / 2)
        median =  lstSortedNumbers[indexMiddle]
    else:
        indexMiddle1 = int((len(lstSortedNumbers) / 2) - 1)
        indexMiddle2 = int(len(lstSortedNumbers) / 2)
        median = (lstSortedNumbers[indexMiddle1] + lstSortedNumbers[indexMiddle2]) / 2

    # The mode is calculated.
    mode = 0.0
    uniqueNumbers = list(set(lstSortedNumbers))
    dctNumberCount = {}
    for uniqueNumber in uniqueNumbers:
        dctNumberCount[uniqueNumber] = lstSortedNumbers.count(uniqueNumber)

    modes = []
    highestCount = -1
    for uniqueNumber in dctNumberCount.keys():
        if highestCount < dctNumberCount[uniqueNumber]:
            highestCount = dctNumberCount[uniqueNumber]
            modes.clear()
            modes.append(uniqueNumber)
        elif highestCount == dctNumberCount[uniqueNumber]:
            modes.append(uniqueNumber)

    return mean, median, modes

lstCentralMeasures1 = central_measures([2,3,5,4,6,3,5,34,6,4,4])
lstCentralMeasures2 = central_measures([1,2,3,4,5])
lstCentralMeasures3 = central_measures([1,2,3,4,5,5])

print(lstCentralMeasures1)
print(lstCentralMeasures2)
print(lstCentralMeasures3)