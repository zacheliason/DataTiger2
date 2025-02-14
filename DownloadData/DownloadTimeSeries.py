import seaborn as sns  # for sample data
import sqlite3
from scipy.optimize import curve_fit
from scipy import stats
from datetime import datetime
import copy
import random
from statistics import *
import platform
from DownloadData.SQLQueries import *
import pandas as pd
from DownloadData.DateToIndex import *
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import traceback
import math
import os

from USGS_downloaders.scrape_usgs_catchments import *


def getIndexList():
    # go from the start date to now
    now = str(datetime.datetime.now())
    date, time = now.split(" ")
    year, month, day = date.split("-")
    year = year[2:]
    hour, minute, second = time.split(":")
    second = second[:2]

    endIndex = datetimeToIndex(year, month, day, hour, minute, second)
    endIndex = round(endIndex / dayToIndexRatio) * dayToIndexRatio

    diff = endIndex - startIndex
    numIndices = diff / dayToIndexRatio

    indexList = []
    for i in range(0,int(numIndices)):
        newVal = startIndex + (i * (dayToIndexRatio))
        indexList.append(newVal)

    return indexList


def joinDictSite(dict1, fullDict, siteID):
    dataNames = dict1.keys()
    for name in dataNames:
        if name == "index" or name == "datetime":
            pass
        else:

            dataList = dict1[name]
            indices = dict1["index"]

            newData = [None] * len(fullDict["index"])

            for i in range(len(indices)):
                index = indices[i]
                #listIndex = int(index / dayToIndexRatio) - int(startIndex / dayToIndexRatio)
                listIndex = round(index / dayToIndexRatio)

                data = dataList[i]

                newData[listIndex] = data

            newName = siteID + "_" + name
            fullDict[newName] = newData
    return fullDict


def joinDict(dict1, fullDict):
    
    dataNames = dict1.keys()
    for name in dataNames:
        if name == "index" or name == "datetime":
            pass

        elif name == "batch_id" and "batch_id" in fullDict.keys() and len(fullDict["batch_id"]) == len(fullDict["index"]):
            pass
            # dataList = dict1[name]
            # indices = dict1["index"]
            #
            # for i in range(len(indices)):
            #
            #     batch_id = dataList[i]
            #     index = indices[i]
            #     # listIndex = int(index / dayToIndexRatio) - int(startIndex / dayToIndexRatio)
            #     listIndex = round(index * indexToDayRatio)
            #
            #     fullDict["batch_id"][listIndex] = batch_id
        else:
            dataList = dict1[name]
            indices = dict1["index"]
            dtime = dict1["datetime"]

            # if len(indices) > 0:
            #     if max(indices) > 646.6:
            #         for i in range(len(indices)):
            #             if indices[i] > 646.6:
            #                 print("*******************************************************************************")
            #             print(indices[i])
            #             print(dtime[i])

            newData = [None] * len(fullDict["index"])
            # print(fullDict["datetime"][-5:])
            for i in range(len(indices)):
               # print(dtime[i])
               # print(index)
               # print(indexToDayRatio)
               # print((indexToDayRatio * indices[-1]) - (indexToDayRatio * indices[0]))
               # print(index / dayToIndexRatio)
               # print(index * dayToIndexRatio)
                #print(len(newData))

                index = indices[i]
                #listIndex = int(index / dayToIndexRatio) - int(startIndex / dayToIndexRatio)
                listIndex = round(index * indexToDayRatio)

                data = dataList[i]
                dt = dtime[i]
                newData[listIndex] = data

            fullDict[name] = newData
    return fullDict

def getDateList(indexList):
    dateList = []
    for index in indexList:
        year, month, day, hour, minute, second = indexToDatetime(index, startYear)
        datetime = str(year) + "-" + str(month) + "-" + str(day) + " " + str(hour) + ":" + str(minute) + ":" + str(second)
        dateList.append(datetime)
    return dateList

def getWaterYearFromDate(date):
    date, time = date.split(" ")
    year, month, date = date.split("-")
    year = int(year)
    month = int(month)
    if month >= 10:
        year += 1
    return year

def getIndexInWaterYearList(dateList, indexList):
    if len(dateList) > 0:
        indexInWaterYearList = []
        waterYears = []
        previousWaterYear = getWaterYearFromDate(dateList[0])
        subractionValue = 0
        for i in range(len(indexList)):
            date = dateList[i]
            index = indexList[i]
            waterYear = getWaterYearFromDate(date)

            if waterYear != previousWaterYear:
                if previousWaterYear % 4 == 0:
                    numDaysInYear = 366
                else:
                    numDaysInYear = 365
                subractionValue += numDaysInYear

            indexInWaterYearList.append(index - subractionValue)
            waterYears.append(waterYear)

            previousWaterYear = waterYear
    return indexInWaterYearList, waterYears

def makeSiteDF(cursor, siteID, nbsNum, citSciNum, testsDict, optionsDict):
    indexList = getIndexList()
    dateList = getDateList(indexList)
    indexInWaterYear, waterYear = getIndexInWaterYearList(dateList, indexList)

    # print("dates")
    # print(dateList[-50:])
    # print("indices")
    # print(indexList[-50:])
    fullDict = {
        "index": indexList,
        "indexInWaterYear":indexInWaterYear,
        "waterYear":waterYear,
        "datetime": dateList
    }
    # fullDf = pd.DataFrame.from_dict(fullDict)
    # fullDf.to_csv("lookatme.csv")

    if testsDict["fieldSheetInfo"]:
        # try:
            fieldSheetDict = getFieldSheetInfo(cursor, siteID, nbsNum, citSciNum)
            fullDict = joinDict(fieldSheetDict, fullDict)
        # except:
        #     print("ERROR")
    if testsDict["hoboPressure"] or optionsDict["calculateDischarge"]:
        # try:
            pDict = getP(cursor, siteID)
            fullDict = joinDict(pDict, fullDict)
        # except:
        #     print("ERROR")
    if testsDict["hoboLight"]:
        # try:
            lightDict = getLightHobo(cursor, siteID)
            fullDict = joinDict(lightDict, fullDict)
        # except:
        #     print("error")
    if testsDict["hoboConductivity"]:
        # try:
            condDict = getConductivityHobo(cursor, siteID)
            fullDict = joinDict(condDict, fullDict)
        # except:
        #     print("error")
    if testsDict["hoboOxygen"]:
        # try:
            oxygenDict = getOxygenHobo(cursor, siteID)
            fullDict = joinDict(oxygenDict, fullDict)
        # except:
        #     print("error")
    if testsDict["measuredDischarge"]:
        # try:
            qDict = getQ(cursor, siteID)
            fullDict = joinDict(qDict, fullDict)
        # except:
        #     print("error")
    if testsDict["hanna"]:
        try:
            hannaDict = getHanna(cursor, siteID)
            fullDict = joinDict(hannaDict, fullDict)
        except:
            print("error")
    if testsDict["eureka"]:
        # try:
            eurekaDict = getEureka(cursor, siteID)
            fullDict = joinDict(eurekaDict, fullDict)
        # except:
        #     print("error")
    if testsDict["elementar"]:
        # try:
            elementarDict = getElementar(cursor, siteID, nbsNum, citSciNum)
            fullDict = joinDict(elementarDict, fullDict)
        # except:
        #     print("error")
    if testsDict["scanCalculated"]:
        # try:
            scanParDict = getScanPar(cursor, siteID, nbsNum, citSciNum)
            fullDict = joinDict(scanParDict, fullDict)
        # except:
        #     print("error")
    if testsDict["scanRaw"]:
        # try:
            scanFPDict = getScanFp(cursor, siteID, nbsNum, citSciNum)
            fullDict = joinDict(scanFPDict, fullDict)
        # except:
        #     print("error")
    if testsDict["ic"]:
        # try:
            icCationDict = getICCation(cursor, siteID, nbsNum, citSciNum)
            fullDict = joinDict(icCationDict, fullDict)
        # except:
        #     print("error")
    if testsDict["ic"]:
        # try:
            icAnionDict = getICAnion(cursor, siteID, nbsNum, citSciNum)
            fullDict = joinDict(icAnionDict, fullDict)
        # except:
        #     print("error")
    if testsDict["icp"]:
        # try:
            icpDict = getICP(cursor, siteID, nbsNum, citSciNum)
            fullDict = joinDict(icpDict, fullDict)
        # except:
        #     print("error")
        
    df = pd.DataFrame.from_dict(fullDict)
    if optionsDict["include_batch_id"]:
        pass
    elif "batch_id" in df.columns:
        df = df.drop("batch_id", axis=1)
        ###
    return df

def add_directory(outputPath, organizing_directory):
    if not os.path.isdir(os.path.join(outputPath, organizing_directory)):
        os.mkdir(os.path.join(outputPath, organizing_directory))

    outputPath = os.path.join(outputPath, organizing_directory)
    return outputPath

def make_file_path(outputPath, siteID, nbsNum, description=None, ending='.csv'):
    file_name = siteID if siteID != "" else nbsNum
    if description:
        file_name += f"_{description}"
    file_name += ending

    return os.path.join(outputPath, file_name)


def saveDF(df, outputPath, siteId, nbsNum, saveFig=False, corrections_df=None, target_list=None, sensors=None, device=None):
    # Adds appropriate parent organizational directories to respective paths
    timeSeriesReportsPath = add_directory(outputPath, "timeSeriesReports")
    figuresPath = add_directory(outputPath, "timeSeriesFigures")
    correctionFiguresPath = add_directory(outputPath, "correctionFigures")

    # Builds path for individual files
    filePath = make_file_path(timeSeriesReportsPath, siteId, nbsNum)
    figPath = make_file_path(figuresPath, siteId, nbsNum, ending=".png")

    # Formats datetime into date objects
    df = format_df_datetime(df, 'datetime')

    # Saves csv of dataframe
    df.to_csv(filePath, index=False)

    # Output any relavent figures
    if saveFig:
        plot_by_year(df, 'barometricPressure_hanna', figPath, title=siteId)
        if target_list is not None:
            # Saves corrected data, if that's the case
            for target in target_list:
                correctionFigPath = make_file_path(correctionFiguresPath, siteId, nbsNum, description=target, ending=".png")
                saveFigure(corrections_df, correctionFigPath, target, sensors, figTitle=f"{siteId} {target}", device=device)
                plot_by_year(corrections_df, col=f"{target}_{device}", path=correctionFigPath, title=f"{siteId} {target}", YSI=target)


def getAllHannaPressuresDF(cursor):
    indexList = getIndexList()
    dateList = getDateList(indexList)
    indexInWaterYear, waterYear = getIndexInWaterYearList(dateList, indexList)

    fullDict = {
        "index": indexList,
        "indexInWaterYear": indexInWaterYear,
        "waterYear": waterYear,
        "datetime": dateList
    }

    siteListTable = "SELECT * FROM master_site"
    cursor.execute(siteListTable)
    result = cursor.fetchall()
    for line in result:

        siteID = line[3]
        nbsNum = line[2]
        citSciNum = line[4]

        nbsNum = nbsNum.split(".")[1]

        # generate the dataframe
        if siteID != "":
            hannaDict = getHanna(cursor, siteID)
            datetime = hannaDict["datetime"]
            index = hannaDict["index"]
            bp = hannaDict["barometricPressure_hanna"]
            keeperDict = {}
            keeperDict["datetime"] = datetime
            keeperDict["index"] = index
            keeperDict["barometricPressure_hanna"] = bp

            fullDict = joinDictSite(keeperDict, fullDict, siteID)

    fullDF = pd.DataFrame.from_dict(fullDict)
    return fullDF


def getSiteCoordinateDicts(cursor):
    siteListTable = "SELECT * FROM master_site"
    cursor.execute(siteListTable)
    result = cursor.fetchall()

    siteToX = {}
    siteToY = {}
    for line in result:
        siteID = line[3]

        if siteID != "":
            siteToX[siteID] = line[8]
            siteToY[siteID] = line[9]

    return siteToX, siteToY

def getDistance(x1, x2, y1, y2):
    x1 = float(x1)
    x2 = float(x2)
    y1 = float(y1)
    y2 = float(y2)

    dx = x1 - x2
    dy = y1 - y2

    hypsqr = dx**2 + dy**2
    dist = np.sqrt([hypsqr])
    dist = dist[0]
    return dist

def getStationToDistanceDict(xdict, ydict):
    stationToDistances = {}
    for station in xdict.keys():
        x1 = xdict[station]
        y1 = ydict[station]
        distances = []
        for stn in xdict.keys():
            x2 = xdict[stn]
            y2 = ydict[stn]

            distance = getDistance(x1, x2, y1, y2)
            distances.append(distance)
        stationToDistances[station] = distances

    return stationToDistances

def getClosestStationsDict(xdict, ydict):
    stationToClosest = {}
    stationToDistances = getStationToDistanceDict(xdict, ydict)
    stations = list(stationToDistances.keys())
    for station in stations:
        ds = stationToDistances[station]
        sortedDs = copy.copy(ds)
        sortedDs.sort()
        priorityList = []
        for distance in sortedDs:
            for i in range(len(stations)):
                if distance == stationToDistances[station][i]:
                    priorityList.append(stations[i])

        stationToClosest[station] = priorityList

    return stationToClosest

def expandIndex(targetIndex, allIndices):
    newBools = []
    found_newBool = False
    for index in allIndices:
        if abs(index - targetIndex) < 0.1:
            newBools.append(True)
            found_newBool = True
        # if the first statement has been reached and passed, you can break the loop :)
        # elif found_newBool:
        #     break
        else:
            newBools.append(False)
    return newBools

# what is the right way to do this?

# calculate a barometric pressure column that I can subtract from the pressure measurements
# subtract them
# run the standard curve
# calculate discharge
def getBarometricPressureColumnNoCorrections(siteID, pdf, stationToPriority):
    columnPostfix = "_barometricPressure_hanna"
    priorityList = stationToPriority[siteID]

    barometricData = pd.Series([None] * len(pdf[pdf.columns[0]]))
    mask = np.asarray(barometricData.isna())

    for site in priorityList:
        columnName = site + columnPostfix
        siteBarometricData = pdf[columnName]
        siteBarometricData = np.asarray(siteBarometricData)
        barometricData[mask] = siteBarometricData[mask]
        mask = np.asarray(barometricData.isna())

    barometricData = pd.Series(barometricData)
    return barometricData

def getBarometricPressureColumn(siteID, pdf, stationToPriority, output_path, start_date="nan", end_date="nan", save_fig=False):
    columnPostfix = "_barometricPressure_hanna"

    return pdf[f"{siteID}{columnPostfix}"]

    priorityList = stationToPriority[siteID]

    barometricData = pd.Series([None] * len(pdf[pdf.columns[0]]))
    barometricDataSites = pd.Series([None] * len(pdf[pdf.columns[0]]))

    mask = np.asarray(barometricData.isna())

    if save_fig:
        baro_site_means = {}
        hanna_sites = pdf.columns.tolist()[4:]
        for site in hanna_sites:
            baro_site_means[site] = pdf[site].mean()

        variance = pdf[hanna_sites].mean(axis=1)

        plt.figure(figsize=(50, 7))
        plt.style.use('ggplot')
        plt.ylabel("Pressure")
        plt.xlabel("Time")

        plt.plot(variance.index, variance.values, lw=.7, label=f"h(e)")

        for site in hanna_sites:
            plt.axhline(y=baro_site_means[site], linewidth=.3, label=f"{site} average")

        plt.title(f"Corrected Barometric Pressure {start_date} to {end_date}")
        plt.legend()
        plt.clf()
        plt.close()

    for site in priorityList:
        columnName = site + columnPostfix
        siteBarometricData = pdf[columnName]
        siteBarometricData = np.asarray(siteBarometricData)
        barometricData[mask] = siteBarometricData[mask]
        barometricDataSites = barometricDataSites.where(~mask, site)
        mask = np.asarray(barometricData.isna())
    barometricData = pd.Series(barometricData)
    barometricDataSites = barometricDataSites.where(~barometricData.isna(), None)

    bdf = pd.DataFrame({'data': barometricData, 'sites': barometricDataSites})
    bdf["corrections"] = [0] * len(bdf[bdf.columns[0]])
    bdf["corrected_values"] = [None] * len(bdf[bdf.columns[0]])

    # chooses how many steps to look forward/backward in determining average correction to apply
    interval = 2

    values = bdf['sites'].value_counts(dropna=False).keys().tolist()
    counts = bdf['sites'].value_counts(dropna=False).tolist()
    value_dict = dict(zip(values, counts))

    ###
    # finds unique batches and uses them to determine where to apply corrections
    batch_switches = bdf.drop_duplicates(subset='sites', keep='first')
    batch_switch_values = batch_switches.sites.values.tolist()
    bdf["site_changed"] = bdf["sites"].shift(1, fill_value=bdf["sites"].head(1)) != bdf["sites"]
    bdf['site_changed'] = bdf['site_changed'].where(~bdf['data'].isna(), False)
    batch_switches = bdf[bdf['site_changed']].index.tolist()
    # test_dict = dict(zip(batch_switch_values, batch_switches))
    small_break_indices = []

    batch_differences = np.diff(batch_switches)
    if None in batch_differences:
        print("here")

    for i in range(len(batch_differences)):
        if batch_differences[i] < 4:
            small_break_indices.append([copy.copy(batch_switches[i]), copy.copy(batch_switches[i + 1])])
            batch_switches[i] = None
            batch_switches[i + 1] = None

    batch_switches = [x for x in batch_switches if x is not None]

    ### New force continuity
    index_switches = batch_switches

    for small in small_break_indices:
        try:
            mean_prev = mean(bdf["data"][small[0] - interval:small[0]].tolist())
            mean_small = mean(bdf['data'][small[0]:small[1]].tolist())
            diff = mean_prev - mean_small
            mask = (small[0] >= bdf.index) & (bdf.index <= small[1])
            bdf['corrections'] = bdf['corrections'].where(~mask, diff)
            bdf['data'] = bdf['data'] + bdf['corrections']
            bdf["corrections"] = [0] * len(bdf[bdf.columns[0]])
        except:
            print(traceback.format_exc())

    # Looks at previous and next x values of batches, pressure points, and indices
    for i in range(len(index_switches)):
        item = index_switches[i]
        prev_b = bdf["sites"][item - interval:item].tolist()
        next_b = bdf["sites"][item:item + interval].tolist()

        prev = bdf["data"][item - interval:item].tolist()
        next = bdf["data"][item:item + interval].tolist()

        prev_i = bdf[item - interval:item].index.tolist()
        next_i = bdf[item:item + interval].index.tolist()

        # If it's not empty, move forward with comparison
        if not all([pd.isna(elem) for elem in prev_b]) and not all([pd.isna(elem) for elem in next_b]):

            # Removes na values from previous arrays
            new_array = []
            new_indices = []
            for j in range(len(prev)):
                if not pd.isna(prev[j]) and prev[j] != "":
                    new_array.append(float(prev[j]))
                    new_indices.append(float(prev_i[j]))
            prev = new_array
            prev_i = new_indices

            # Removes na values from next arrays
            new_array = []
            new_indices = []
            for j in range(len(next)):
                if not pd.isna(next[j]) and next[j] != "":
                    new_array.append(float(next[j]))
                    new_indices.append(float(next_i[j]))
            next = new_array
            next_i = new_indices

            # Feel free to correct me here but I reasoned that extreme outliers happening at the batch number switch are unlikely to be valid, thus I throw some away here
            outliers, outlier_indices = detect_outlier(prev, prev_i)
            if len(outliers) > 0:
                for x in outlier_indices:
                    bdf.at[x, "pressure_hobo"] = np.nan
            prev_no_outliers = list(set(prev) - set(outliers))
            avg_prev = np.nanmean(prev_no_outliers)

            # Feel free to correct me here but I reasoned that extreme outliers happening at the batch number switch are unlikely to be valid, thus I throw some away here
            outliers, outlier_indices = detect_outlier(next, next_i)
            if len(outliers) > 0:
                for x in outlier_indices:
                    bdf.at[x, "pressure_hobo"] = np.nan
            next_no_outliers = list(set(next) - set(outliers))
            avg_next = np.nanmean(next_no_outliers)

            # Finally, calculate correction value
            correction = avg_next - avg_prev
            if pd.isna(correction):
                print("OH NO :(")
            if abs(correction) > 100:
                print(f'large correction: {correction}')

            # Apply correction value to all previous pressure points thus reached
            mask = (bdf.index < index_switches[i])
            bdf['temp_corrections'] = bdf['corrections'].where(~mask, correction)
            bdf['corrections'] = bdf['corrections'] + bdf['temp_corrections']
            bdf["temp_corrections"] = [0] * len(bdf[bdf.columns[0]])

    bdf['corrections'] = bdf['corrections'].where(~bdf['data'].isna(), None)
    bdf['corrected_values'] = pd.to_numeric(bdf['corrections']) + pd.to_numeric(bdf['data'])

    if save_fig:

        # ############################
        # TEST CONTINUITY BY PLOTTING
        # ############################

        plt.figure(figsize=(50, 7))
        plt.style.use('ggplot')
        plt.ylabel("Pressure")
        plt.xlabel("Time")

        plt.plot(bdf.index, bdf["data"], lw=.3, zorder=2, c='grey', linestyle='dotted', label=f"original data")
        # plt.plot(bdf.index, bdf["corrected_values"], lw=.3, zorder=2, label=f"corrected")

        groups = bdf.groupby('sites')
        for name, group in groups:
            plt.scatter(x=group.index, y=group.corrected_values, s=3, zorder=4, label=f"{name}")

        plt.title(f"Corrected Barometric Pressure {start_date} to {end_date}")
        plt.legend()
        plt.savefig(f"{output_path}/{siteID}/barometric_pressure_corrected_{start_date}_to_{end_date}.png", dpi=300)
        plt.clf()
        plt.close()

        old_output_path = copy.copy(outputPath)
        if not os.path.isdir(os.path.join(outputPath, siteID)):
            os.mkdir(os.path.join(outputPath, siteID))
        outputPath = old_output_path

    # Old force continuity:
    # for i in range(len(index_switches)):
    #     item = index_switches[i]
    #     prev_b = bdf["sites"][item - interval:item].tolist()
    #     next_b = bdf["sites"][item:item + interval].tolist()
    #
    #     prev = bdf["data"][item - interval:item].tolist()
    #     next = bdf["data"][item:item + interval].tolist()
    #
    #     if not all([elem is None for elem in prev_b]) and not all([elem is None for elem in next_b]):
    #         prev = [float(pressure) for pressure in prev if pressure is not None and pressure != ""]
    #         next = [float(pressure) for pressure in next if pressure is not None and pressure != ""]
    #
    #         outliers = detect_outlier(prev)
    #         if len(outliers) > 0:
    #             print(f'help {outliers}')
    #             pass
    #
    #         prev_no_outliers = list(set(prev) - set(outliers))
    #         avg_prev = mean(prev_no_outliers)
    #
    #         outliers = detect_outlier(next)
    #         if len(outliers) > 0:
    #             print(f'help {outliers}')
    #             pass
    #
    #         next_no_outliers = list(set(next) - set(outliers))
    #         avg_next = mean(next_no_outliers)
    #
    #         correction_this_site = avg_prev - avg_next
    #         correction = correction_this_site + cumulative_correction
    #
    #         if abs(correction) > 100:
    #             print(f'large correction: {correction_this_site}')
    #
    #         mask = (bdf.index >= index_switches[i - 1]) & (bdf.index < index_switches[i])
    #         bdf['corrections'] = bdf['corrections'].where(~mask, correction)
    #         cumulative_correction = cumulative_correction + correction_this_site

    # bdf['corrections'] = bdf['corrections'].where(~bdf['data'].isna(), None)
    # bdf['corrected_values'] = pd.to_numeric(bdf['corrections']) + pd.to_numeric(bdf['data'])

    # barometricData = bdf['corrected_values']
    barometricData = bdf['corrected_values']
    return barometricData, bdf

def replaceBlankWithNone(array):
    array = list(array)
    for j in range(len(array)):
        val = array[j]
        val = str(val)
        val.replace(" ","")
        if val == "":
            array[j] = None
    return array

def get_discharge_to_pressure(df, siteID, pdf, cursor, output_path, start_date, end_date):
    try:
        ndf = df.merge(pdf, on='index')
        ndf['corrected'] = ndf['pressure_hobo'] - ndf[f"{siteID}_barometricPressure_hanna"]
    except:
        print(traceback.format_exc())
        print('oaky')

    edf = df.reset_index()

    ndf['corrected'] = (ndf['corrected'] - ndf['corrected'].mean()) / (ndf['corrected'].std())

    edf['corrected_pressure_hobo'] = ndf['corrected']

    return df, ndf

def getDischargeToPressureDF(df, siteID, pdf, cursor, output_path, start_date, end_date):
    # barometricData, bdf = getBarometricPressureColumn(siteID, pdf, stationToPriority, output_path, start_date, end_date, True)
    try:
        barometricData = pdf[f"{siteID}_barometricPressure_hanna"]
    except:
        print(traceback.format_exc())
        print('oaky')

    # step is equal to the difference in index equivalent to 3 hrs (12 indices == 12 15 min intervals == 3 hrs).
    step = 12

    # # drop None values in pressure_hobo
    # indices_no_na = pd.Series(barometricData[~barometricData.isna()].index)
    #
    # # create series of differences between indices so we can later find the jumps where Nones were taken out
    # differences = indices_no_na.diff()
    # # create series of indices of aforementioned differences ^
    # index_df = differences.index
    # # create dict and then df from series
    # d = {'differences': differences, 'index_df': index_df}
    # idf = pd.DataFrame(d)
    #
    # # starts == the beginning index of each individual grouping
    # starts = idf.loc[(idf['differences'] >= step)]['index_df'].values.tolist()
    #
    # if len(starts) > 0:
    #     print("we have a huge err that I don't have the bandwidth to troubleshoot rn sorry :)")
    #     print("basically you have jumps within the barometric pressure data, idk maybe not a huge deal")

    # barometric_pairings = [barometricData.loc[indices_no_na.values.tolist()[0]]['index'], barometricData.loc[indices_no_na.values.tolist()[-1]]['index']]

    # plt.figure(figsize=(50, 7))
    # plt.style.use('ggplot')
    # plt.ylabel("pressure")
    # # plt.xlabel(f"{stationToPriority[siteID]}")
    #
    # # Coloring biz
    # color_labels = bdf['sites'].unique()
    # rgb_values = sns.color_palette("Set2", 8)
    # color_map = dict(zip(color_labels, rgb_values))
    # df = df.reset_index()
    # bdf['colors'] = bdf['sites'].map(color_map)
    #
    # groups = bdf.groupby('sites')
    # for name, group in groups:
    #     plt.scatter(x=group.index, y=group.data, s=3, zorder=4, label=f"{name}")
    #
    # # plt.scatter(x=bdf.index, y=bdf['data'], c=bdf['colors'], lw=.4, label=bdf["sites"])
    # # plt.scatter(x=df.index, y=df["discharge_measured"], c="tomato", s=5)
    #
    # plt.legend()
    # plt.clf()
    # plt.close()

    # columnPostfix = "_barometricPressure_hanna"
    # priorityList = stationToPriority[siteID]

    pdfMask = list(~df["discharge_measured"].isna())
    if len(pdfMask) != len(pdf):
        if len(pdfMask) < len(pdf):
            pdfMask.append(False)
        elif len(pdfMask) > len(pdf):
            pdfMask = pdfMask[:-1]

    try:
        dischargeIndices = pdf[pdfMask]["index"]
        
        # do for barometric pressure

        correctedPressurePoints = df[~df["discharge_measured"].isna()]["corrected_values"]
        correctionPoints = df[~df["discharge_measured"].isna()]["corrections"]
        pressurePoints = df[~df["discharge_measured"].isna()]["pressure_hobo"]
        pressureData = df["pressure_hobo"]
        correctedPressureData = df["corrected_values"]
        dischargePoints = df[~df["discharge_measured"].isna()]["discharge_measured"]
        datePoints = df[~df["discharge_measured"].isna()]["datetime"]

    except:
        print(traceback.format_exc())
        print("tears")

    xs = []
    ys = []
    zs = []
    dates = []

    press = []
    corrected_press = []
    corrections_short = []
    corrections_full = []
    barPress = []
    dis = []
    fullDates = []
    for i in range(len(dischargeIndices)):
        index = list(dischargeIndices)[i]
        pressure = list(pressurePoints)[i]
        discharge = list(dischargePoints)[i]
        date = list(datePoints)[i]
        corrected_pressure = list(correctedPressurePoints)[i]
        correction = list(correctionPoints)[i]

        expandedIndex = expandIndex(index, df["index"])
        expandedIndex = expandedIndex[:len(pdf[pdf.columns[0]])]

        # because "" values can be in there instead of None values
        nearbyBarometricMeasurements = barometricData[expandedIndex]
        nearbyPressureMeasurements = pressureData[:len(barometricData)][expandedIndex]
        nearbyCorrectedPressureMeasurements = correctedPressureData[:len(barometricData)][expandedIndex]

        nearbyBarometricMeasurements = replaceBlankWithNone(nearbyBarometricMeasurements)
        nearbyPressureMeasurements = replaceBlankWithNone(nearbyPressureMeasurements)
        nearbyCorrectedPressureMeasurements = replaceBlankWithNone(nearbyCorrectedPressureMeasurements)

        nearbyBarometricMeasurements = pd.Series(nearbyBarometricMeasurements)
        nearbyPressureMeasurements = pd.Series(nearbyPressureMeasurements)
        nearbyCorrectedPressureMeasurements = pd.Series(nearbyCorrectedPressureMeasurements)

        maskB = np.asarray(~nearbyBarometricMeasurements.isna())
        maskP = np.asarray(~nearbyPressureMeasurements.isna())
        maskC = np.asarray(~nearbyCorrectedPressureMeasurements.isna())

        nearbyBarometricMeasurements = np.asarray(nearbyBarometricMeasurements)
        nearbyPressureMeasurements = np.asarray(nearbyPressureMeasurements)
        nearbyCorrectedPressureMeasurements = np.asarray(nearbyCorrectedPressureMeasurements)

        if np.sum(maskB) > 0:
            meanBarometricPressure = np.mean(nearbyBarometricMeasurements[maskB])
        else:
            meanBarometricPressure = None

        if np.sum(maskP) > 0:
            meanPressure = np.mean(nearbyPressureMeasurements[maskP])
        else:
            meanPressure = None

        if np.sum(maskC) > 0:
            meanCorrectedPressure = np.mean(nearbyCorrectedPressureMeasurements[maskC])
        else:
            meanCorrectedPressure = None

        press.append(meanPressure)
        corrected_press.append(meanCorrectedPressure)
        barPress.append(meanBarometricPressure)
        dis.append(discharge)
        fullDates.append(date)
        corrections_full.append(correction)

        if meanBarometricPressure != None and meanCorrectedPressure != None and discharge != None:
            if not np.isnan(meanBarometricPressure) and not np.isnan(meanPressure) and not np.isnan(discharge):
                discounted_pressure_point = float(meanPressure) - float(meanBarometricPressure)
                if discounted_pressure_point > -15:
                    xs.append(discounted_pressure_point)
                    zs.append(float(meanCorrectedPressure) - float(meanBarometricPressure))
                    ys.append(discharge)
                    dates.append(date)
                    corrections_short.append(correction)
                else:
                    print('err')

    returnDict = {"barometric_discounted_original_pressure": xs, "barometric_discounted_corrected_pressure": zs, "measured_discharge":ys, "datetime":dates, "corrections": corrections_short}
    longDict = {"barometricPressure": barPress, "absolutePressure": press,"discharge": dis, "datetime": fullDates, "correctedPressure": corrected_press, "corrections": corrections_full}
    # FIXME: this isn't quite getting it right!

    returnDF = pd.DataFrame.from_dict(returnDict)
    longDF = pd.DataFrame.from_dict(longDict)

    if len(returnDF.index) == 0 and len(longDF.index) == 0:
        return None, None

    return returnDF, longDF

def interpolate(df):
    print("interpolation not functional yet")
    return df

def detect_outlier(data, indices):
    outliers = []
    outlier_indices = []
    ##### change threshold? Ask Brian
    threshold = 2.5
    mean_1 = np.mean(data)
    std_1 = np.std(data)

    for i in range(len(data)):
        y = data[i]
        index = indices[i]
        z_score = (y - mean_1) / std_1
        if np.abs(z_score) > threshold:
            outliers.append(y)
            outlier_indices.append(index)

    return outliers, outlier_indices

def correct_sensor_gaps(df):
    df["lock_corrections"] = [0] * len(df[df.columns[0]])
    df["corrections"] = [0] * len(df[df.columns[0]])
    df["corrected_values"] = [None] * len(df[df.columns[0]])
    last_index = 0

    # chooses how many steps to look forward/backward in determining average correction to apply
    interval = 12

    # finds unique batches and uses them to determine where to apply corrections
    batch_switches = df.drop_duplicates(subset='batch_id', keep='first')
    index_switches = batch_switches.index.tolist()

    # Looks at previous and next x values of batches, pressure points, and indices
    for i in range(len(index_switches)):
        item = index_switches[i]
        prev_b = df["batch_id"][item - interval:item].tolist()
        next_b = df["batch_id"][item:item + interval].tolist()

        prev = df["pressure_hobo"][item - interval:item].tolist()
        next = df["pressure_hobo"][item:item + interval].tolist()

        prev_i = df[item - interval:item].index.tolist()
        next_i = df[item:item + interval].index.tolist()

        # If it's not empty, move forward with comparison
        if not all([pd.isna(elem) for elem in prev_b]) and not all([pd.isna(elem) for elem in next_b]):

            # Removes na values from previous arrays
            new_array = []
            new_indices = []
            for j in range(len(prev)):
                if not pd.isna(prev[j]) and prev[j] != "":
                    new_array.append(float(prev[j]))
                    new_indices.append(float(prev_i[j]))
            prev = new_array
            prev_i = new_indices

            # Removes na values from next arrays
            new_array = []
            new_indices = []
            for j in range(len(next)):
                if not pd.isna(next[j]) and next[j] != "":
                    new_array.append(float(next[j]))
                    new_indices.append(float(next_i[j]))
            next = new_array
            next_i = new_indices

            # Feel free to correct me here but I reasoned that extreme outliers happening at the batch number switch are unlikely to be valid, thus I throw some away here
            outliers, outlier_indices = detect_outlier(prev, prev_i)
            if len(outliers) > 0:
                for x in outlier_indices:
                    df.at[x, "pressure_hobo"] = np.nan
            prev_no_outliers = list(set(prev) - set(outliers))
            avg_prev = np.nanmean(prev_no_outliers)

            # Feel free to correct me here but I reasoned that extreme outliers happening at the batch number switch are unlikely to be valid, thus I throw some away here
            outliers, outlier_indices = detect_outlier(next, next_i)
            if len(outliers) > 0:
                for x in outlier_indices:
                    df.at[x, "pressure_hobo"] = np.nan
            next_no_outliers = list(set(next) - set(outliers))
            avg_next = np.nanmean(next_no_outliers)

            # Finally, calculate correction value
            correction = avg_next - avg_prev
            if pd.isna(correction):
                print("OH NO :(")
            if abs(correction) > 100:
                print(f'large correction: {correction}')

            # Apply correction value to all previous pressure points thus reached
            mask = (df.index < index_switches[i])
            df['temp_corrections'] = df['corrections'].where(~mask, correction)
            df['corrections'] = df['corrections'] + df['temp_corrections']
            df["temp_corrections"] = [0] * len(df[df.columns[0]])
        else:
            mask = (last_index <= df.index) & (df.index < index_switches[i])
            df['lock_corrections'] = df['lock_corrections'].where(~mask, df['corrections'])
            df["corrections"] = [0] * len(df[df.columns[0]])
            last_index = index_switches[i]

    df['lock_corrections'] = df['lock_corrections'].where(~df['pressure_hobo'].isna(), None)
    df['corrected_values'] = pd.to_numeric(df['lock_corrections']) + pd.to_numeric(df['pressure_hobo'])

    return df

def segment_df_by_continuity(df, pdf):
    # step is equal to the difference in index equivalent to 3 hrs (12 indices == 12 15 min intervals == 3 hrs).
    step = df['index'].diff().mean() * 12

    # drop None values in pressure_hobo
    indices_no_na = df[~df['pressure_hobo'].isna()]['index']
    indices_no_na = indices_no_na.reset_index()
    indices_no_na = indices_no_na['index']

    # create series of differences between indices so we can later find the jumps where Nones were taken out
    differences = indices_no_na.diff()
    # create series of indices of aforementioned differences ^
    index_df = differences.index
    # create dict and then df from series
    d = {'differences': differences, 'index_df': index_df}
    idf = pd.DataFrame(d)
    idf = idf.reset_index()

    # starts == the beginning index of each individual grouping
    starts = idf.loc[(idf['differences'] >= step)]['index_df'].values.tolist()

    # ends == the ending index of each individual grouping
    ends = [i - 1 for i in starts]

    try:
        # add beginning and closing index to starts
        starts.insert(0, indices_no_na.index.tolist()[0])
        starts.append(indices_no_na.index.tolist()[-1])
    except:
        print(traceback.format_exc())
        print(f"length of df: {len(df[~df['pressure_hobo'].isna()]['pressure_hobo'].values.tolist())}")
        return None, None, None


    final = sorted(ends + starts)

    # use indices of indices_no_na to find corresponding target df indices
    final = [indices_no_na.loc[i] for i in final]
    len_final = len(final)
    if len_final % 2 != 0:
        print('it should really be even, mayday!! 😰')

    # pair those indices and you're done :)
    pairings = [[final[i], final[i+1]] for i in range(0, len(final), 2)]

    # This line is obnoxiously obtuse but I don't have the bandwidth to simplify rn. Basically it takes the column ['index'] and uses it to find the actual indices from df
    # But it works!
    list_df = [df[df.loc[df['index'] == pair[0]].index.tolist()[0]:df.loc[df['index'] == pair[1]].index.tolist()[0]] for pair in pairings]
    list_pdf = [pdf[df.loc[df['index'] == pair[0]].index.tolist()[0]:df.loc[df['index'] == pair[1]].index.tolist()[0]] for pair in pairings]
    return list_df, list_pdf, pairings

def format_df_datetime(df, name_of_datetime):
    df[name_of_datetime] = df[name_of_datetime].apply(lambda x: " ".join(
        ["-".join(list(map(lambda y: y.zfill(2), x.split(" ")[0].split("-")))),
         ":".join(list(map(lambda y: y.zfill(2), x.split(" ")[1].split(":"))))]))
    df[name_of_datetime] = pd.to_datetime(df[name_of_datetime], format='%y-%m-%d %H:%M:%S')
    return df

def plot_list_df(df, list_df, outputPath, siteID):
    figures_path = add_directory(outputPath, siteID)
    fig_path = make_file_path(figures_path, siteID, description="segmented", ending=".png")

    plt.figure(figsize=(17, 7))
    plt.style.use('ggplot')
    plt.ylabel("Pressure")
    plt.xlabel("Time")

    z = 0
    for d in list_df:
        z += 1
        plt.plot(d["datetime"], d["pressure_hobo"], lw=.3, zorder=2, label=f"{z}")

    df_filtered_by_discharge = df[~df["discharge_measured"].isna()]
    plt.scatter(df_filtered_by_discharge["datetime"], df_filtered_by_discharge["pressure_hobo"], s=10, c='tomato', zorder=10, label="discharge measurements")

    plt.text(0.95, 0.01, f'{str(len(df_filtered_by_discharge["datetime"].values.tolist()))} discharge measurements at this site.', verticalalignment='bottom', horizontalalignment='right', fontsize=15)

    plt.title(f"{siteID} Segmented by Chunk of Workable Continuous Pressure Data (gaps < 3 hrs)")
    plt.legend()

    plt.savefig(fig_path, dpi=300)
    plt.clf()
    plt.close()

def processDFStandardCurve(cursor, siteID, nbsNum, citSciNum, testsDict, optionsDict, outputPath, calculated_pdf):
# def processDFStandardCurve(cursor, siteID, nbsNum, citSciNum, testsDict, optionsDict, outputPath):

    # NOTE: not all of the catchments have data going up until 2021 (this is corroborated across the usgs website)

    # catchments_df = df of all the catchments
    catchments_df, sites_dict = get_usgs_discharge_sites()

    if optionsDict["calculateStandardCurve"] == True:
        testsDict["hoboPressure"] = True
        testsDict["measuredDischarge"] = True

    ### update testsDict (options?) to grab batch # from database, when batch numbers switch,
    df = makeSiteDF(cursor, siteID, nbsNum, citSciNum, testsDict, optionsDict)

    # Format dates inside df into datetime objects
    df = format_df_datetime(df, 'datetime')

    # -----------------------------------
    # uncomment out for faster testing
    # -----------------------------------
    # df = pd.read_csv("zach_df.csv")
    # df.to_csv("zach_df.csv", index=False)

    # Align leading/lagging ends of each batch
    if optionsDict["include_batch_id"]:
        # NORMALIZE PRESSURE HOBO
        df['pressure_hobo'] = pd.to_numeric(df['pressure_hobo'], errors='coerce')
        # df['pressure_hobo'] = df['pressure_hobo'].replace('', np.nan)
        # df['pressure_hobo'] = (df['pressure_hobo'] - df['pressure_hobo'].mean()) / (df['pressure_hobo'].std())

        # following function will enforce continuity by aligning each of the beginning and lagging ends of each batch in the pressure data
        df = correct_sensor_gaps(df)

    # get nearest usgs site
    usgs_site = sites_dict[siteID]

    # catchments_df[usgs_site] = catchments_df[usgs_site][catchments_df[usgs_site].date > start_datetime]
    normalized_usgs = (catchments_df[usgs_site].flows - catchments_df[usgs_site].flows.mean()) / (catchments_df[usgs_site].flows.std())


    plt.figure(figsize=(50, 7))
    plt.style.use('ggplot')
    plt.ylabel("Pressure")
    plt.xlabel("Time")
    plt.title(f"Full Range of Pressure + Corrected Data at {siteID}")

    groups = df.groupby('batch_id')
    for name, group in groups:
        plt.plot(group['index'], group.corrected_values, lw=.4, zorder=4, )

    plt.plot(catchments_df[usgs_site]['indices'], normalized_usgs, lw=.2, c="tomato", zorder=2, label=f"{usgs_site} discharge")
    # plt.plot(df.datetime, df['pressure_hobo'], lw=.2, c="grey", zorder=2, linestyle='dotted', label=f"original values")
    plt.legend()

    plt.show()
    # plt.savefig(f"{outputPath}/{siteID}/{siteID}_corrected_pressure_data.png", dpi=300)

    # proceed = input('looks good? y/n \n')
    #
    # if proceed == 'y':
    #     print("okay")
    # elif proceed == 'n':
    #     print("not okay")

    plt.clf()
    plt.close()

    df['pressure_hobo'] = df['corrected_values']

    # -------------------------------------
    # Separate DF into continuous segments
    # -------------------------------------

    list_df, list_pdf, pairings = segment_df_by_continuity(df, calculated_pdf)

    if list_df is not None:
        plot_list_df(list_df)

        for i in range(len(list_df)):
            start_date = pd.to_datetime(df.loc[(df["index"] == pairings[i][0])]['datetime'].values.tolist()[0]).strftime("%B %d, %Y")
            end_date = pd.to_datetime(df.loc[(df["index"] == pairings[i][1])]['datetime'].values.tolist()[0]).strftime("%B %d, %Y")

            # df1, df2 = getDischargeToPressureDF(list_df[i], siteID, list_pdf[i], cursor, outputPath, start_date, end_date)
            df1, df2 = get_discharge_to_pressure(list_df[i], siteID, list_pdf[i], cursor, outputPath, start_date, end_date)

            plt.figure(figsize=(50, 7))
            plt.style.use('ggplot')
            plt.ylabel("Pressure")
            plt.xlabel("Time")
            plt.title(f"corrected barometric pressure")

            plt.plot(df1['index'], df2['corrected'], lw=.4, zorder=4, )

            usgs_site = sites_dict[siteID]

            plt.plot(catchments_df[usgs_site]['indices'], normalized_usgs, lw=.2, c="tomato", zorder=2, label=f"{usgs_site} discharge")
            # plt.plot(df.datetime, df['pressure_hobo'], lw=.2, c="grey", zorder=2, linestyle='dotted', label=f"original values")
            plt.legend()
            plt.show()

            plt.figure(figsize=(50, 7))
            plt.style.use('ggplot')
            plt.ylabel("Pressure")
            plt.xlabel("Time")
            plt.title(f"Full Range of Pressure + Corrected Data at {siteID}")

            usgs_site = sites_dict[siteID]

            start_datetime = df2['datetime_x'].iloc[0]
            end_datetime = df2['datetime_x'].iloc[-1]

            catchments_df[usgs_site] = catchments_df[usgs_site][catchments_df[usgs_site].date > start_datetime]
            catchments_df[usgs_site] = catchments_df[usgs_site][catchments_df[usgs_site].date < end_datetime]

            normalized_usgs = (catchments_df[usgs_site].flows - catchments_df[usgs_site].flows.mean()) / (catchments_df[usgs_site].flows.std())

            plt.plot(catchments_df[usgs_site]['date'], normalized_usgs, lw=.2, c="tomato", zorder=2, label=f"{usgs_site} discharge")
            plt.plot(df2['datetime_x'], df2['corrected'], lw=.2, c="grey", zorder=2, linestyle='dotted', label=f"corrected pressure")
            plt.legend()

            plt.show()

            if df1 is not None and df2 is not None and len(df1.index) != 0 and len(df2.index) != 0:
                plotRatingCurve(df1, outputPath, siteID, start_date, end_date)

                df1.to_csv(f"{outputPath}/{siteID}/pressure_to_discharge_no_null_{start_date}_to_{end_date}.csv")
                df2.to_csv(f"{outputPath}/{siteID}/pressure_and_barometric_full_{start_date}_to_{end_date}.csv")
            else:
                print(f"{siteID} empty from {start_date} to {end_date}")

    # download the df
    # download the picture
    # generate the figure
    # download the figure
    # download the csv # date, pressure, discharge,
    # save the slopes onto the database

def plotRatingCurve(df, outputPath, siteID, start_date, end_date):
    plt.figure(figsize=(17, 7))
    plt.style.use('ggplot')

    x = df['measured_discharge'].values.tolist()
    y = df['barometric_discounted_original_pressure'].values.tolist()

    # try:
    #     popt, _ = curve_fit(rating_curve_objective, x, y)
    #     df[f"rating_curve"] = rating_curve_objective(df["barometric_discounted_original_pressure"], *popt)
    #     plt.plot(df["barometric_discounted_original_pressure"], df['rating_curve'], 'r', c='teal', label='fitted line')
    # except:
    try:
        res = stats.linregress(df["barometric_discounted_original_pressure"], df["measured_discharge"])
        plt.plot(df["barometric_discounted_original_pressure"], res.intercept + res.slope * df["barometric_discounted_original_pressure"], 'r', c='teal', label='fitted line')
    except:
        print(traceback.format_exc())

    plt.xlabel("Barometric Discounted Pressure")
    plt.ylabel("Discharge")

    plt.scatter(df["barometric_discounted_original_pressure"], df["measured_discharge"], s=6, c="tomato", zorder=4, label=f"discharge")
    plt.title(f"{siteID} Rating Curve")
    plt.legend()
    plt.savefig(f"{outputPath}/{siteID}/{siteID}_{start_date}_to_{end_date}_rating_curve.png", dpi=300)
    plt.clf()
    plt.close()

def getSlopeIntercept(datetime, siteID, keyDict, siteDict):
    date, time = datetimes.split(" ")
    year, month, day = date.split("/")
    for key in siteDict.keys():
        vec = siteDict[key]
        slope = vec[keyDict["slope"]]
        intercept = vec[keyDict["intercept"]]
        startIndex = vec[keyDict["startIndex"]]
        endIndex = vec[keyDict["endIndex"]]

        # if
        #     return slope, intercept # FIXME not sure wher eintercept is coming from

    print("WARNING getSlopeIntercept not implemented")
    return 1, 1


def addCalculatedDischarge(df, siteID, pdf, stationToPriority, cursor):
    barometricData = getBarometricPressureColumnNoCorrections(siteID, pdf, stationToPriority)
    absoluteData = df["pressure_hobo"]
    dates = df["datetime"]
    print(len(barometricData))
    print(len(absoluteData))

    mask1 = np.asarray(~barometricData.isna())
    mask2 = np.asarray(~absoluteData.isna())
    mask = np.logical_and(mask1, mask2)

    barometricData = np.asarray(barometricData)
    absoluteData = np.asarray(absoluteData)
    pressureData = absoluteData

    pressureData[mask] = float(absoluteData[mask]) - float(barometricData[mask])
    pressureData[~mask] = None
    # print(pressureData)
    # print(pressureData[mask])

    dischargePoints = [None] * len(pressureData)

    keyDict, siteDict = getSlopeInterceptDicts(cursor, siteID)

    for i in range(len(pressureData[mask])):
        date = dates[mask][i]
        slope, intercept = getSlopeIntercept(date, siteID, cursor, keyDict, siteDict)

        pressure = pressureData[mask][i]
        discharge = pressure * slope + intercept
        dischargePoints[mask][i] = discharge

    df["calculated_discharge"] = dischargePoints

    return df

def processDF(cursor, siteID, nbsNum, citSciNum, testsDict, optionsDict, outputPath, pdf, stationToPriority):

    if optionsDict["calculateDischarge"] == True:
        testsDict["hoboPressure"] = True

    df = makeSiteDF(cursor, siteID, nbsNum, citSciNum, testsDict, optionsDict)

    # calculate discharge 
    if optionsDict["calculateDischarge"] == True:
        df = addCalculatedDischarge(df, siteID, pdf, stationToPriority, cursor)

    # interpolate
    if optionsDict["interpolate"] == True:
        df = interpolate(df)

    if optionsDict["correct_values"] == True:
        sensors = ["Hanna", "YSI"]
        target_list = ["electricalConductivity", "pH", "temperature", "orpMV", "dissolvedOxygen_mgL"]
        corrections_df, device = correctValuesCurve(df, sensors, target_list)

        if corrections_df is None:
            if siteID == "":
                print(
                    f"huge error! corrections for NBS{nbsNum} failed because no hobo/eureka/hanna data was found. Possibly it only has scan data?")
            else:
                print(
                    f"Huge error! Corrections for {siteID} failed because no hobo/eureka/hanna data was found. Possibly it only has scan data?")
            saveDF(df, outputPath, siteID, nbsNum)
        else:
            saveDF(df, outputPath, siteID, nbsNum, True, corrections_df, target_list, sensors, device)
    else:
        saveDF(df, outputPath, siteID, nbsNum)
    return df

def objective(x, a, b, c, d, e, f, g, h):
    return (a * x) + (b * x ** 2) + (c * x ** 3) + (d * x ** 4) + (e * x ** 5) + (f * x ** 6) + (g * x ** 7) + h

def rating_curve_objective(x, a, b):
    # return (a * x) + (b * x ** 2) + c
    return (a * x) + b

def correctValuesCurve(df, sensors, target_list):
    df = df.replace("", np.nan, regex=True)
    df = df.fillna(value=np.nan)

    device = senseDeviceType(target_list, df)
    if device is None:
        return None, None

    # correct df names based on device type
    if device == "hobo":
        df = df.rename(columns={"conductivity_hobo": "electricalConductivity_hobo", "dissolvedOxygen_mgl_hobo": "dissolvedOxygen_mgL_hobo"})
        target_list.remove("orpMV")
        target_list.remove("pH")
    elif device == "eureka":
        df = df.rename(columns={"orp_eureka": "orpMV_eureka"})
        target_list.remove("dissolvedOxygen_mgL")
    elif device == "hanna":
        target_list.append("dissolvedOxygenPercent")
    else:
        return None, None

    return df, device # FIXME

    for target in target_list:
        filtered_df = df[~df[f"{target}_fieldsheet"].isna()]
        x = filtered_df["index"].tolist()
        y = filtered_df[f"{target}_fieldsheet"].tolist()
        minind = x[0]
        maxind = x[-1]

        if len(x) < 3:
            continue

        popt, _ = curve_fit(objective, x, y)

        df[f"YSI_curve_{target}"] = objective(df["index"], *popt)

        # cut off errant tails of curve
        df[f"YSI_curve_{target}"] = df[f"YSI_curve_{target}"].where((df["index"] > minind), None)
        df[f"YSI_curve_{target}"] = df[f"YSI_curve_{target}"].where((df["index"] < maxind), None)

        # filter df for creating residuals between ysi curve and data points, find residual points
        filtered_df = df[~df[f"{target}_fieldsheet"].isna()]
        filtered_df = filtered_df[~filtered_df[f"{target}_{device}"].isna()]
        filtered_df = filtered_df[~filtered_df[f"YSI_curve_{target}"].isna()]

        filtered_df[f"residual_curve_{target}"] = [None] * len(filtered_df)
        # fdf["res_curve"] = fdf["YSI_curve"] - fdf["electricalConductivity_eureka"]
        filtered_df[f"residual_curve_{target}"] = filtered_df[f"YSI_curve_{target}"] - filtered_df[f"{target}_{device}"]
        asdf = copy.copy(filtered_df)
        asdf = asdf.rename(columns={f"residual_curve_{target}": f"{target}"})
        asdf = asdf[f"{target}"]
        df = pd.concat([df, asdf], axis=1)

        res = filtered_df[f"residual_curve_{target}"].tolist()
        x = filtered_df["index"].tolist()

        # add residual points to df
        filtered_df = filtered_df[f"residual_curve_{target}"]
        df = pd.concat([df, filtered_df], axis=1)

        # optimize curve for residual points
        popt, _ = curve_fit(objective, x, res)

        filtered_df = df[~df[f"residual_curve_{target}"].isna()]
        x = filtered_df["index"].tolist()
        minind = x[0]
        maxind = x[-1]

        df[f"residual_curve_{target}"] = objective(df["index"], *popt)
        df[f"residual_curve_{target}"] = df[f"residual_curve_{target}"].where((df["index"] > minind), None)
        df[f"residual_curve_{target}"] = df[f"residual_curve_{target}"].where((df["index"] < maxind), None)

        df[f"{target}_{device}_corrected"] = df[f"{target}_{device}"] + df[f"residual_curve_{target}"]

    return df, device

    #
    # cols = []
    #     for point_sensor in resDict.keys():
    #         for target in target_list:
    #             df[f"{point_sensor}_corrected_{target}"] = [None] * len(df[df.columns[0]])
    #             df[f"{point_sensor}_residual_{target}"] = [None] * len(df[df.columns[0]])
    #             cols.extend([f"{point_sensor}_residual_{target}", f"{point_sensor}_corrected_{target}"])
    #             if f"{target}_fieldsheet" not in cols and f"{target}_{device}" not in cols:
    #                 cols.extend([f"{target}_fieldsheet", f"{target}_{device}"])


# def correctValues(df, sensors, target_list):
#     df = df.replace("", np.nan, regex=True)
#     df = df.fillna(value=np.nan)
#
#     resDict, device, df, target_list = loadResidualDict(df, target_list, sensors)
#     if device is None:
#         return None, None
#
#     # specify only important columns for final export
#     cols = []
#     for point_sensor in resDict.keys():
#         for target in target_list:
#             df[f"{point_sensor}_corrected_{target}"] = [None] * len(df[df.columns[0]])
#             df[f"{point_sensor}_residual_{target}"] = [None] * len(df[df.columns[0]])
#             cols.extend([f"{point_sensor}_residual_{target}", f"{point_sensor}_corrected_{target}"])
#             if f"{target}_fieldsheet" not in cols and f"{target}_{device}" not in cols:
#                 cols.extend([f"{target}_fieldsheet", f"{target}_{device}"])
#
#     # for each row in df, point_sensor, and target, calculate necessary values based on preloaded line formula dictionary
#     nan_df = pd.isnull(df)
#     for index, row in df.iterrows():
#         for point_sensor in resDict.keys():
#             for target in resDict[point_sensor].keys():
#                 for k, v in resDict[point_sensor][target].items():
#                     if index < k[0]:
#                         pass
#                     elif k[0] <= index < k[1]:
#                         # calculate corrected position of current index using point-slope formula from piecewise residual function
#                         y = (v["m"] * (index - v["x1"])) + v["y1"]
#                         df.at[index, f"{point_sensor}_residual_{target}"] = y
#                         try:
#                             if not nan_df.at[index, f"{target}_{device}"]:
#                                 df.at[index, f"{point_sensor}_corrected_{target}"] = float(
#                                     df.at[index, f"{target}_{device}"]) + y
#                         except:
#                             print(traceback.format_exc())
#                             print(f"{target}_{device}")
#                         # if current index lies within range, continue to subsequent targets
#                     elif index >= k[1]:
#                         # it'd be nice for performance' sake to not have to cycle through each visited key after it's been passed but I can't think of a quick fix that works at the moment
#                         # following doesn't work
#                         pass
#
#     return df, device

def senseDeviceType(target_list, df):
    parse_df = df[~df[f"{target_list[0]}_fieldsheet"].isna()]
    if not all(parse_df["conductivity_hobo"].isna()):
        device = "hobo"
    elif not all(parse_df["electricalConductivity_eureka"].isna()):
        device = "eureka"
    elif "electricalConductivity_hanna" in parse_df.columns.tolist() and not all(parse_df["electricalConductivity_hanna"].isna()):
        device = "hanna"
    else:
        device = ""
        print("HUGE ERR: no device detected :(")
        print("see whether you can trace the error?")
    return device

# def loadResidualDict(df, target_list, sensors):
#     point_slope_dict = {}
#
#     # sense device type
#     device = senseDeviceType(target_list, df)
#
#     # correct df names based on device type
#     if device == "hobo":
#         df = df.rename(columns={"conductivity_hobo": "electricalConductivity_hobo", "dissolvedOxygen_mgl_hobo": "dissolvedOxygen_mgL_hobo"})
#         target_list.remove("orpMV")
#         target_list.remove("pH")
#     elif device == "eureka":
#         df = df.rename(columns={"orp_eureka": "orpMV_eureka"})
#         target_list.remove("dissolvedOxygen_mgL")
#     elif device == "hanna":
#         target_list.append("dissolvedOxygenPercent")
#     else:
#         return None, None, None, None
#
#     for point_sensor in sensors:
#         point_slope_dict[point_sensor] = {}
#         filtered_df = df[~df[f"{target_list[0]}_fieldsheet"].isna()]
#         filtered_df = filtered_df[filtered_df['device'].str.contains(f"{point_sensor}", na=False)]
#
#         for target in target_list:
#             # further filter df to include only entries with valid readings
#             filter_by_target = filtered_df[~filtered_df[f"{target}_{device}"].isna()]
#             df[f"{point_sensor}_{target}_fieldsheet"] = df[f"{target}_fieldsheet"].mask((~df['device'].str.contains(f"{point_sensor}", na=True)), other=None)
#
#             point_slope_dict[point_sensor][target] = {}
#
#             filter_by_target.loc[:, f"{point_sensor}_{target}_residual_line"] = [None] * len(filter_by_target.index)
#
#             x1, y1, m = None, None, None
#             for index, row in filter_by_target.iterrows():
#                 try:
#                     tf = row[f"{target}_fieldsheet"]
#                     # Error check type etc!
#                     if type(tf) == str:
#                         if ":" in tf:
#                             tf = tf.replace(":", ".")
#                             df.at[index, f"{target}_fieldsheet"] = tf
#                         if tf == "-" or "0($0 !11&8$" in tf or r"435.\x01$0$" in tf:
#                             tf == None
#                         else:
#                             tf = float(tf)
#                     elif type(tf) == int:
#                         tf = float(tf)
#                     elif type(tf) != float:
#                         if tf is None:
#                             tf = np.nan
#                         else:
#                             print(f"ERR: type {type(tf)}")
#                     if not math.isnan(tf):
#                         if type(row[f"{target}_{device}"]) == str:
#                             if row[f"{target}_{device}"] == "":
#                                 print("help!")
#                         filter_by_target.at[index, f"{target}_{device}"] = float(row[f"{target}_{device}"])
#                         # if not first iteration
#                         if x1 is not None:
#                             # calculate slope
#                             m = ((tf - float(row[f"{target}_{device}"]) - y1) / (index - x1))
#                             # from points x1 - x2, slope is m with y1 of y1
#                             point_slope_dict[point_sensor][target][(x1, index)] = {"x1": x1, "y1": y1, "m": m}
#                         y1 = tf - float(row[f"{target}_{device}"])
#                         x1 = index
#                 except:
#                     print(traceback.format_exc())
#                     print("could not convert", row[f"{target}_fieldsheet"], "on target:", target)
#
#     return point_slope_dict, device, df, target_list

def downloadTimeSeries(outputPath, testsDict, optionsDict, cursor):
    print("SYSTEM: ", platform.system())

    if optionsDict["calculateDischarge"] == True:
        pdf = getAllHannaPressuresDF(cursor)
        xdict, ydict = getSiteCoordinateDicts(cursor)
        stationToPriority = getClosestStationsDict(xdict, ydict)
    else:
        pdf = None
        stationToPriority = None
    if not os.path.isdir(outputPath + "/timeSeriesCorrectionFigures"):
        os.makedirs(outputPath + "/timeSeriesCorrectionFigures")
    siteListTable = "SELECT * FROM master_site"
    cursor.execute(siteListTable)
    result = cursor.fetchall()

    progress_length = len(result)
    progress_list = [x[3] for x in result]
    
    for line in result:
        print(f"Now starting {line[3] if line[3] != '' else str(line[2])}")
        print("[" + (("#") * (progress_length - len(progress_list))) + ((" ") * len(progress_list)) + "]")
        print(str(round(((((progress_length - len(progress_list)) / (progress_length)) * 100)), 2)) + "% done" + "\n")

        siteID = line[3]
        nbsNum = line[2]
        citSciNum = line[4]

        nbsNum = nbsNum.split(".")[1]

        # generate the dataframe
        if optionsDict["includeSynoptic"] == True:
            df = processDF(cursor, siteID, nbsNum, citSciNum, testsDict, optionsDict, outputPath, pdf, stationToPriority)
            print('okay')
        else:
            if siteID != "":
                df = processDF(cursor, siteID, nbsNum, citSciNum, testsDict, optionsDict, outputPath, pdf, stationToPriority)
                print('okay')

        progress_list.remove(siteID)
        print(f"{line[3] if line[3] != '' else str(nbsNum)} complete")

    return "successfully downloaded time series report to " + outputPath

def plot_by_year(df, col, path, title, YSI=None, calibration_line=False):
    try:
        plt.style.use('ggplot')

        df[col] = pd.to_numeric(df[col], errors='coerce')
        plt.scatter(df['datetime'], df[col], s=.1)

        # Plots YSI points on timeseries if indicated
        if YSI:
            plt.scatter(df["datetime"], df[f"{YSI}_fieldsheet"], s=4, c="tomato", zorder=4, label=f"{YSI} YSI")

        if calibration_line:
            plt.axvline(x=945, zorder=7, label="Stopped calibrating May 3, 2021")

        plt.title(title)
        plt.legend()
        plt.savefig(path, dpi=300)

        plt.clf()
        plt.close()

    except:
        print(traceback.format_exc())
        print(f"PNG export for {title} failed")


def downloadStandardCurve(outputPath, testsDict, optionsDict, cursor):

    for test in testsDict.keys():
        testsDict[test] = False
    for option in optionsDict.keys():
        optionsDict[option] = False

    # double check that the right things are being requested
    testsDict["pressure_hobo"] = True
    optionsDict["include_batch_id"] = True
    optionsDict["calculateStandardCurve"] = True  # FIXME: figuring out what to do with calculateDischarge

    # START

    pdf = getAllHannaPressuresDF(cursor)
    pdf = format_df_datetime(pdf, 'datetime')
    xdict, ydict = getSiteCoordinateDicts(cursor)
    stationToPriority = getClosestStationsDict(xdict, ydict)

    pdf_sites = pdf.drop(['waterYear', 'index', 'indexInWaterYear', 'datetime'], axis=1)

    # remove values under 100 torr (arbitrarily, happy to change it but I feel relatively safe it wouldn't be below 100)
    for col in pdf_sites:
        pdf_sites[col] = pdf_sites[col].where(pdf_sites[col] > 100, None)

    ## This was for testing where you get unlikely jumps in pressure (ie SFL was going from 600 to then flatlining at 0 for month)
    # differences = pdf_sites['SFL_barometricPressure_hanna'].diff()
    # jumps = abs(differences) > 200
    # where_true = jumps.index[jumps == True].tolist()

    mean_series = pdf_sites.mean(axis=1, skipna=True, numeric_only=True)
    mean_per_site = pdf_sites.mean(axis=0, skipna=True, numeric_only=True)

    overall_mean = mean(mean_series[~mean_series.isna()].values.tolist())
    mean_series = mean_series - overall_mean
    mean_per_site_dict = mean_per_site.to_dict()
    calculated_pdf = {}

    for k,v in mean_per_site_dict.items():
        calculated_pdf[k] = v + mean_series

    calculated_pdf = pd.DataFrame(calculated_pdf)
    calculated_pdf['datetime'] = pdf['datetime']
    calculated_pdf['index'] = pdf['index']
    calculated_pdf['indexInWaterYear'] = pdf['indexInWaterYear']
    calculated_pdf['waterYear'] = pdf['waterYear']

    # END
    # -------------------------------------------------------------------------- #
    # -------------------------------------------------------------------------- #

    siteListTable = "SELECT * FROM master_site"
    cursor.execute(siteListTable)
    result = cursor.fetchall()

    progress_length = len(result)
    progress_list = [x[3] for x in result]


    for line in result:
        print(f"Now starting {line[3] if line[3] != '' else str(line[2])}")
        print("[" + (("#") * (progress_length - len(progress_list))) + ((" ") * len(progress_list)) + "]")
        print(str(round(((((progress_length - len(progress_list)) / (progress_length)) * 100)), 2)) + "% done" + "\n")

        siteID = line[3]
        nbsNum = line[2]
        citSciNum = line[4]

        nbsNum = nbsNum.split(".")[1]

        if siteID != 'BSL':
            continue

        if siteID != "":
            old_output_path = copy.copy(outputPath)
            if not os.path.isdir(os.path.join(outputPath, siteID)):
                os.mkdir(os.path.join(outputPath, siteID))
            outputPath = old_output_path
            processDFStandardCurve(cursor, siteID, nbsNum, citSciNum, testsDict, optionsDict, outputPath, calculated_pdf)
            # processDFStandardCurve(cursor, siteID, nbsNum, citSciNum, testsDict, optionsDict, outputPath)

        progress_list.remove(siteID)
        print(f"{line[3] if line[3] != '' else str(nbsNum)} complete")

    return "successfully downloaded standard curve report to " + outputPath

def downloadLoggerGapsReport(outputPath, cursor, testsDict, optionsDict):
    siteListTable = "SELECT * FROM master_site"
    cursor.execute(siteListTable)
    result = cursor.fetchall()

    for line in result:

        siteID = line[3]
        nbsNum = line[2]
        citSciNum = line[4]

        nbsNum = nbsNum.split(".")[1]

        if siteID != "":
            dataDict = {} 
            
            df = makeSiteDF(cursor, siteID, nbsNum, citSciNum, testsDict, optionsDict)
            for column in df:
                if column != "index" and column != "datetime":
                    dataDict[column] = []
                    
                    startDates = []
                    stopDates = []
                    
                    values = df[column]
                    dates = df["datetime"]
                    indices = df["index"]
                    
                    keeperMask = ~values.isna()
                    
                    values = np.asarray(values)
                    dates = np.asarray(dates)
                    indices = np.asarray(indices)
                    
                    keeperValues = values[keeperMask]
                    keeperDates = dates[keeperMask]
                    keeperIndices = indices[keeperMask]

                    if len(keeperIndices) > 0:
                        firstRecordedDate = keeperDates[0]
                        lastRecordedDate = keeperDates[-1]

                    numPossibleDays = len(keeperIndices) / (4 * 24)
                     
                    for i in range(1, len(keeperIndices)):
                        previous = keeperIndices[i - 1]
                        current = keeperIndices[i]
                         
                        if current - previous > 5: # if we go for ~ more than an hour without data
                            stopDate = keeperDates[i - 1]    
                            startDate = keeperDates[i]
                            
                            stopDates.append(stopDate)
                            startDates.append(startDate)


                    # find the missing values
                    # grab the dates associated with the start and finish
                    # 

                    startToStopDates = dict(zip(startDates, stopDates))

                    if len(keeperIndices) == 0:
                        dataDict[column].append("no data logged")
                    else:
                        dataDict[column].append("first logged date")
                        dataDict[column].append(firstRecordedDate)
                        for key in startToStopDates.keys():
                            dataDict[column].append("start of gap")
                            dataDict[column].append(startToStopDates[key])
                            dataDict[column].append("end of gap")
                            dataDict[column].append(key)
                        dataDict[column].append("last logged date")
                        dataDict[column].append(lastRecordedDate)

        # to csv via a dataframe
        maxLenList = 0
        for key in dataDict.keys():
            if len(dataDict[key]) > maxLenList:
                maxLenList = len(dataDict[key])
        for key in dataDict.keys():
            extra = [None] * (maxLenList - len(dataDict[key]))
            dataDict[key] = dataDict[key] + extra

        missingDf = pd.DataFrame.from_dict(dataDict)
        if platform.system() == "Windows":
            filePath = outputPath + "\\loggerGapsReport_" + siteID + ".csv"
        else:
            filePath = outputPath = "/loggerGapsReport_" + siteID + ".csv"
        missingDf.to_csv(filePath, index=False)

    return "successfully downloaded logger gaps report to " + outputPath


# DEPRECATED
def saveFigure(df, figPath, target, sensors, figTitle, device):
    try:
        # save figure
        plt.figure(figsize=(17, 7))
        plt.style.use('ggplot')
        plt.xlabel("Days since 2018")
        plt.ylabel(target)
        plt.scatter(df["index"], df[f"{target}_{device}"], c="grey", s=.5, zorder=1, label="raw data")

        # for point_sensor in sensors:
        #     if point_sensor == "Hanna":
        #         plt.plot(df["index"], df[f"{point_sensor}_residual_{target}"], lw=1, ls="dotted", c="coral",
        #                  zorder=1, label=f"{point_sensor} residual")
        #         plt.plot(df["index"], df[f"{point_sensor}_corrected_{target}"], lw=.5, c="orange", zorder=1,
        #                  label=f"{point_sensor} corrected values")
        #         plt.scatter(df["index"], df[f"{point_sensor}_{target}_fieldsheet"], s=2, c="orangered", zorder=2,
        #                     label=f"{point_sensor} fieldsheet values")
        #     else:

        plt.scatter(df["index"], df[f"{target}_fieldsheet"], s=6, c="tomato", zorder=4,
                    label=f"{target}_YSI")
        plt.axvline(x=945, c="tomato", zorder=7, label="Stopped calibrating May 3, 2021")
        plt.title(figTitle)
        plt.legend()
        plt.savefig(figPath, dpi=300)
        plt.clf()
        plt.close()
    except:
        print(traceback.format_exc())
        print(f"PNG export for {figTitle} failed at target: {target}")
