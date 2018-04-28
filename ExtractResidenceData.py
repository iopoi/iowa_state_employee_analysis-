import csv
import sys

# Read data from mulitple residence data files
# Write combined file that keys on (area, year) with column for each attribute from each source file
# Missing years are filled in for each attr using most recent entry

if __name__ == "__main__":
    fileNames = [
        "../ODN_RWJF_Health_Behaviors.csv",
        "../ODN_Geographic_Area.csv",
        "../ODN_Education.csv",
        "../ODN_Population.csv"
    ]

    fileAttrs = [
        ["adult_obesity_value", "children_in_poverty_value", "income_inequality_value", "median_household_income_value", "some_college_value", "unemployment_value", "violent_crime_value", "uninsured_value"],
        ["density"],
        ["percent_graduate_or_professional_degree", "percent_some_college", "percent_less_than_9th_grade", "percent_associates_degree", "percent_bachelors_degree_or_higher", "percent_high_school_graduate"],
        ["count"]
    ]

    # Will map area to attribute to year to value
    initDict = dict()

    # Process each data file
    for fi, f in enumerate(fileNames):
        # Read all rows in csv format
        with open(f) as dataFile:
            reader = csv.DictReader(dataFile)
            for row in reader:
                # Get the associated variable for this row, and decide if we want to keep it
                var = row["variable"]
                if var in fileAttrs[fi]:

                    # Get the name of the area
                    area = row["name"].upper().split(",")[0]
                    if area != "HANCOCK COUNTY" and area != "JACKSON COUNTY":
                        area = area.replace(" COUNTY", "")

                    # Create entry for this area and variable
                    if area not in initDict:
                        initDict[area] = dict()
                    if var not in initDict[area]:
                        initDict[area][var] = dict()

                    # Get the year
                    year = int(row["year"])

                    # Record entry
                    initDict[area][var][year] = row["value"]

    # Make sure there is data for every year, and invert the dictionaries
    finalDict = dict()
    for area in initDict.keys():
        finalDict[area] = dict()
        attrs = initDict[area]
        for attr in attrs.keys():
            years = attrs[attr]

            # Get earliest data that exists
            firstYear = min(years.keys())
            curVal = years[firstYear]

            # For each year in desired range, fill in missing years with most recently updated data
            for y in range(2007, 2018):
                if y not in years:
                    years[y] = curVal
                else:
                    curVal = years[y]

                # Final dict has order (area, year, attr) rather than (area, attr, year)
                if y not in finalDict[area]:
                    finalDict[area][y] = dict()
                finalDict[area][y][attr] = years[y]

    # Convert combined data to csv format
    with open("residenceData.csv", "w") as finalFile:
        columns = ["Place of Residence", "Fiscal Year"] + [a for fAttr in fileAttrs for a in fAttr]
        writer = csv.DictWriter(finalFile, fieldnames=columns)
        writer.writeheader()
        for area, years in finalDict.items():
            for year, attrs in years.items():
                attrs["Place of Residence"] = area
                attrs["Fiscal Year"] = year
                writer.writerow(attrs)
