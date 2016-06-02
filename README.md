# SPDDataClean
Scripts to cleanup Seattle Police Department (SPD) 911 response data, as exported from here:
https://data.seattle.gov/Public-Safety/NGLNeighborhood_85_90_Aurora_Wallingford/pjbc-999y

That link is a filtered view, but the script should work(-ish) for any data exported from that SPD
dataset. Additional cleanup is usually required--sometimes just hopping into excel and looking for
outliers is the easiest thing to do--but hopefully it can be fully automated at some point.

What does this script do?
- Homogenize block string representation, so "Foo St / Bar Ave" and "Bar Ave / Foo St" become the same, 
  whichever we see first "wins" and all will be rewritten so that they match.  This lets them all get thrown
  into the same LOD bin in Tableau etc. if you put that field in play
- All records with same block string representation will get overwritten with same lat/lon (first seen "wins" for all)
- applies special rewrite rules (currently coded in applySpecialRewriteRules function below), for known badly-formatted
  block names.  They can also be discarded via this function.  You will want to add your own rewrite rules here to
  replace what is there now.
- when I have time to do the work, it will warn about block names that appear to be non-compliant

Example of how I use the cleaned up data:
https://public.tableau.com/profile/dave.smith5366#!/vizhome/NorthGreenlakeCrimeJan2009-Oct2015/Dashboard1

TO RUN:

1. You need to install python (version 3.x may be required, I didn't actually test it with 2) from [here](https://www.python.org/).
2. Run the script with "python clean_spd_data.py /path/to/my_spd_data.csv"
3. It will write out a file my_spd_data_cleaned.csv
