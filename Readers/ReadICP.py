from CustomErrors import *

class ReadICP:
    def __init__(self, filePath):
        self.filePath = filePath
        cleanPath = self.filePath.replace("\\", "/")
        cleanPath = cleanPath.replace("//", "/")
        pathList = cleanPath.split("/")
        self.fileName = pathList[-1]

        self.aluminumIndex = None
        self.arsenicIndex = None
        self.boronIndex = None
        self.bariumIndex = None
        self.calciumIndex = None
        self.cadmiumIndex = None
        self.cobaltIndex = None
        self.chromiumIndex = None
        self.copperIndex = None
        self.ironIndex = None
        self.potassiumIndex = None
        self.magnesiumIndex = None
        self.manganeseIndex = None
        self.molybdenumIndex = None
        self.sodiumIndex = None
        self.nickelIndex = None
        self.phosphorusIndex = None
        self.leadIndex = None
        self.sulfurIndex = None
        self.seleniumIndex = None
        self.siliconIndex = None
        self.strontiumIndex = None
        self.titaniumIndex = None
        self.vanadiumIndex = None
        self.zincIndex = None

        self.aluminum = None
        self.arsenic = None
        self.boron = None
        self.barium = None
        self.calcium = None
        self.cadmium = None
        self.cobalt = None
        self.chromium = None
        self.copper = None
        self.iron = None
        self.potassium = None
        self.magnesium = None
        self.manganese = None
        self.molybdenum = None
        self.sodium = None
        self.nickel = None
        self.phosphorus = None
        self.lead = None
        self.sulfur = None
        self.selenium = None
        self.silicon = None
        self.strontium = None
        self.titanium = None
        self.vanadium = None
        self.zinc = None




    def getFileName(self):
        return self.fileName

    def getFilePath(self):
        return self.filePath

    def readBatch(self, columns):
        # get the filename
        nameList = self.fileName.split(".")
        try:
            self.runDate = nameList[0]
            self.projectId = nameList[1]
            self.operator = nameList[2]
        except:
            raise ICPFileNotNamedCorrectly(self.fileName)

        self.projectId = self.projectId.replace(" ","")


        # fix the date
        year = self.runDate[0:2]
        month = self.runDate[2:4]
        day = self.runDate[4:6]
        year = "20" + year
        self.runDate = year + "-" + month + "-" + day

        # get the column indices of the columns we want to parse
        # fullReport = False
        # dilutionIncluded = False
        # startIndex = 0
        # stopIndex = len(columns)

        # i = 0
        # for column in columns:
        #     column = column.lower()
        #     if "total dissolved solids" in column:
        #         fullReport = True
        #         startIndex = i + 1
        #     if "dilution" in column:
        #         stopIndex = i
        #         dilutionIncluded = True
        #     i = i + 1
        # if fullReport:
        #     columnsToSearch = range(startIndex,stopIndex)
        # else:
        #     if dilutionIncluded:
        #         columnsToSearch = range(1,stopIndex)
        #     else:
        #         raise ICPMustHaveDilutionColumn(self.fileName)

        for index in range(len(columns)):
            column = columns[index].lower()

            if ("sort" in column and "chem" in column) or ("lab" in column and "#" in column) or ("sample" in column and "id" in column):
                self.sortChemIndex = index
            # elif ("al" in column) and (not "ppm" in column) and (index > 0):
            elif column == "al":
                self.aluminumIndex = index
            # elif ("as" in column) and (not "ppm" in column) and (index > 0):
            elif column == "as":
                self.arsenicIndex = index
            # elif ("b" in column) and (not "ppm" in column) and (index > 0) and ("ba" not in column) and ("pb" not in column):
            elif column == "b":
                self.boronIndex = index
            # elif ("ba" in column) and (not "ppm" in column) and (index > 0):
            elif column == "ba":
                self.bariumIndex = index
            # elif ("ca" in column) and (not "ppm" in column) and (index > 0):
            elif column == "ca":
                self.calciumIndex = index
            # elif ("cd" in column) and (not "ppm" in column) and (index > 0):
            elif column == "cd":
                self.cadmiumIndex = index
            # elif ("co" in column) and (not "ppm" in column) and (index > 0):
            elif column == "co":
                self.cobaltIndex = index
            # elif ("cr" in column) and (not "ppm" in column) and (index > 0):
            elif column == "cr":
                self.chromiumIndex = index
            # elif ("cu" in column) and (not "ppm" in column) and (index > 0):
            elif column == "cu":
                self.copperIndex = index
            # elif ("fe" in column) and (not "ppm" in column) and (index > 0):
            elif column == "fe":
                self.ironIndex = index
            # elif ("k" in column) and (not "ppm" in column) and (index > 0):
            elif column == "k":
                self.potassiumIndex = index
            # elif ("mg" in column) and (not "ppm" in column) and (index > 0):
            elif column == "mg":
                self.magnesiumIndex = index
            # elif ("mn" in column) and (not "ppm" in column) and (index > 0):
            elif column == "mn":
                self.manganeseIndex = index
            # elif ("mo" in column) and (not "ppm" in column) and (index > 0):
            elif column == "mo":
                self.molybdenumIndex = index
            # elif ("na" in column) and (not "ppm" in column) and (index > 0):
            elif column == "na":
                self.sodiumIndex = index
            # elif ("ni" in column) and (not "ppm" in column) and (index > 0):
            elif column == "ni":
                self.nickelIndex = index
            # elif ("p" in column) and (not "ppm" in column) and (index > 0) and ("pb" not in column):
            elif column == "p":
                self.phosphorusIndex = index
            # elif ("pb" in column) and (not "ppm" in column) and (index > 0):
            elif column == "pb":
                self.leadIndex = index
            # elif ("s" in column) and (not "ppm" in column) and (index > 0) and ("se" not in column) and ("si" not in column) and ("sr" not in column):
            elif column == "s":
                self.sulfurIndex = index
            # elif ("se" in column) and (not "ppm" in column) and (index > 0):
            elif column == "se":
                self.seleniumIndex = index
            # elif ("si" in column) and (not "ppm" in column) and (index > 0):
            elif column == "si":
                self.siliconIndex = index
            # elif ("sr" in column) and (not "ppm" in column) and (index > 0):
            elif column == "sr":
                self.strontiumIndex = index
            # elif ("ti" in column) and (not "ppm" in column) and (index > 0):
            elif column == "ti":
                self.titaniumIndex = index
            # elif ("v" in column) and (not "ppm" in column) and (index > 0):
            elif column == "v":
                self.vanadiumIndex = index
            # elif ("zn" in column) and (not "ppm" in column) and (index > 0):
            elif column == "zn":
                self.zincIndex = index
            else:
                print("skipped this column")
                print(column)


    def clearValues(self):
        self.sortChem = None
        self.aluminum = None
        self.arsenic = None
        self.boron = None
        self.barium = None
        self.calcium = None
        self.cadmium = None
        self.cobalt = None
        self.chromium = None
        self.copper = None
        self.iron = None
        self.potassium = None
        self.magnesium = None
        self.manganese = None
        self.molybdenum = None
        self.sodium = None
        self.nickel = None
        self.phosphorus = None
        self.lead = None
        self.sulfur = None
        self.selenium = None
        self.silicon = None
        self.strontium = None
        self.titanium = None
        self.vanadium = None
        self.zinc = None


    def readRow(self, row):
        self.clearValues()

        if self.sortChemIndex != None:
            self.sortChem = row[self.sortChemIndex]
        if self.aluminumIndex != None:
            self.aluminum = row[self.aluminumIndex]
        if self.arsenicIndex != None:
            self.arsenic = row[self.arsenicIndex]
        if self.boronIndex != None:
            self.boron = row[self.boronIndex]
        if self.bariumIndex != None:
            self.barium = row[self.bariumIndex]
        if self.calciumIndex != None:
            self.calcium= row[self.calciumIndex]
        if self.cadmiumIndex != None:
            self.cadmium = row[self.cadmiumIndex]
        if self.cobaltIndex != None:
            self.cobalt = row[self.cobaltIndex]
        if self.chromiumIndex != None:
            self.chromium = row[self.chromiumIndex]
        if self.copperIndex != None:
            self.copper = row[self.copperIndex]
        if self.ironIndex != None:
            self.iron = row[self.ironIndex]
        if self.potassiumIndex != None:
            self.potassium = row[self.potassiumIndex]
        if self.magnesiumIndex != None:
            self.magnesium = row[self.magnesiumIndex]
        if self.manganeseIndex != None:
            self.manganese = row[self.manganeseIndex]
        if self.molybdenumIndex != None:
            self.molybdenum = row[self.molybdenumIndex]
        if self.sodiumIndex != None:
            self.sodium = row[self.sodiumIndex]
        if self.nickelIndex != None:
            self.nickel = row[self.nickelIndex]
        if self.phosphorusIndex != None:
            self.phosphorus = row[self.phosphorusIndex]
        if self.leadIndex != None:
            self.lead = row[self.leadIndex]
        if self.sulfurIndex != None:
            self.sulfur = row[self.sulfurIndex]
        if self.seleniumIndex != None:
            self.selenium = row[self.seleniumIndex]
        if self.siliconIndex != None:
            self.silicon = row[self.siliconIndex]
        if self.strontiumIndex != None:
            self.strontium = row[self.strontiumIndex]
        if self.titaniumIndex != None:
            self.titanium = row[self.titaniumIndex]
        if self.vanadiumIndex != None:
            self.vanadium = row[self.vanadiumIndex]
        if self.zincIndex != None:
            self.zinc = row[self.zincIndex]

