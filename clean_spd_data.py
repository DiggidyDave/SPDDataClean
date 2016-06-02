#!/usr/local/bin/python3

'''
Meant to cleanup data sourced from here:
https://data.seattle.gov/Public-Safety/NGLNeighborhood_85_90_Aurora_Wallingford/pjbc-999y

However, should work(-ish) for any data exported from that SPD dataset.  Additional cleanup is always
required, sometimes just hopping into excel and looking for outliers is the easiest thing to do.

What does this script do?
- Homogenize block string representation, so "Foo St / Bar Ave" and "Bar Ave / Foo St" become the same
  whichever we see first "wins" and all will be rewritten
- All records with same block string representation will get overwritten with same lat/lon (first seen "wins" for all)
- applies special rewrite rules (currently coded in applySpecialRewriteRules function below), for known badly-formatted
  block names.  They can also be discarded via this function
- when I have time to do the work, it will warn about block names that appear to be non-compliant
'''

import csv
import re
import sys

def applySpecialRewriteRules(blockName):
    '''
    This function can be used to look for specific strings, patterns, etc and rewrite as needed,
    useful if there are known bad records that require one-off treatment for cleanup
    If this returns None, the record will be discarded
    '''
    result = blockName

    # "AVE" to "AV"
    blockName = re.sub(r' AVE(\b)', r' AV\1', blockName)

    if blockName == '8853 1 / 2 NESBIT AV N':
        result = '88XX BLOCK of NESBIT AV N'
    elif blockName == '90TH AV / AURORA AV N SEATTLE WA':
        result = 'N 90 ST / AURORA AV N'

    # Log changes we made, if any
    if blockName != result:
        print("Rewriting block name from '%s' to '%s'" % (blockName, result))
    return result

def warnOnUnknownPattern(recordBlock):
    blockPattern = '[0-9]{1,}XX BLOCK OF '


def cleanupFile(path):
    # column indices (probably should look these up instead of hard-code)
    blockIdx = 10
    latIdx = 15
    lonIdx = 14
    latLongIdx = 16

    headers = None
    records = None
    with open(path, 'rt', newline='') as f:
        csvr = csv.reader(f)
        records = [l for l in csvr]
        headers = records.pop(0)

    visitedBlocks = {}

    # Go through a de-dup, cleanup, etc.
    # - Homogenize block string representation, so "Foo St / Bar Ave" and "Bar Ave / Foo St" become the same
    #   whichever we see first "wins" and all will be rewritten
    # - All records with same block get overwritten with same lat/lon (first seen "wins" for all)
    for curRecord in records:
        blockLookupKey = None

        curRecordBlockName = curRecord[blockIdx].upper()

        curRecordBlockName = applySpecialRewriteRules(curRecordBlockName)
        if curRecordBlockName == None:
            continue

        warnOnUnknownPattern(curRecordBlockName)

        if curRecordBlockName in visitedBlocks.keys():
            # we've used this exact block string as a key so use it
            blockLookupKey = curRecordBlockName
        elif '/' in curRecordBlockName:
            # if there is a / in our name we may have used its reverse, if so reuse it
            # ex "N 90th St / Aurora Av N" vs "Aurora Av N / N 90th St"
            s = [s.strip() for s in curRecordBlockName.split('/')]
            reversedBlockLookupKey = "%s / %s" % (s[1], s[0])
            if reversedBlockLookupKey in visitedBlocks.keys():
                blockLookupKey = reversedBlockLookupKey

        if blockLookupKey:
            # we have stored block info for this, so just copy prev-used values into current record
            blockInfo = visitedBlocks[blockLookupKey]
            curRecord[blockIdx] = blockInfo[0]
            curRecord[latIdx] = blockInfo[1]
            curRecord[lonIdx] = blockInfo[2]
            curRecord[latLongIdx] = blockInfo[3]
        else:
            # we have NOT seen this block info before, so shove current block info into visited blocks
            visitedBlocks[curRecordBlockName] = [
                curRecordBlockName, curRecord[latIdx], curRecord[lonIdx], curRecord[latLongIdx]
            ]

    fc = path.split('.')
    outfile = "%s_cleaned.%s" % (fc[0], fc[1])
    with open(outfile, 'wt') as f:
        f.write("\t".join(headers) + '\n')
        for curRecord in records:
            f.write("\t".join(curRecord) + '\n')


if __name__ == "__main__":
    cleanupFile(sys.argv[1])
