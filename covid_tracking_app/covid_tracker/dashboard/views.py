from django.shortcuts import render
import pandas as pd 


# Create your views here.
def dashboard(request):
    """ Main dashboard. The landing page. """

    # get data on global confirmed cases
    lastUpdateDate, totalInfectionCases, country, infections, maxVal = getGlobalData()
    map_data = getMapData(country, infections)

    # determine wether or not to show world map
    showMap = "True"

    # display data
    context = {'totalInfectionCases': totalInfectionCases,
               'lastUpdateDate': lastUpdateDate,
               'infections': infections,
               'country': country,
               'mapData': map_data,
               'showMap': showMap,
               'xdata':[],
               'data1':[],
               'data2':[],
               'maxVal':maxVal}

    return render(request, 'index.html', context)

def getGlobalData():
    """ Get global data and extract data 
    
        The data is located on the COVID-19 Data Repository by the Center for Systems Science and Engineering (CSSE) at Johns Hopkins University's github page.

        ** Time series summary (csse_covid_19_time_series)
        This folder contains daily time series summary tables, including confirmed, deaths and recovered. All data is read in from the daily case report. The time series tables are subject to be updated if inaccuracies are identified in our historical data. The daily reports will not be adjusted in these instances to maintain a record of raw data.
        Two time series tables are for the US confirmed cases and deaths, reported at the county level. They are named time_series_covid19_confirmed_US.csv, time_series_covid19_deaths_US.csv, respectively.
        Three time series tables are for the global confirmed cases, recovered cases and deaths. Australia, Canada and China are reported at the province/state level. Dependencies of the Netherlands, the UK, France and Denmark are listed under the province/state level. The US and other countries are at the country level. The tables are renamed time_series_covid19_confirmed_global.csv and time_series_covid19_deaths_global.csv, and time_series_covid19_recovered_global.csv, respectively.
       
        **Update frequency
        Once a day around 23:59 (UTC).
    """

    # read in data
    confirmedGlobalCases = pd.read_csv(
        'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv', encoding='utf-8', na_values=None)

    # 1. Get - Date data was last updated
    lastUpdateDate = confirmedGlobalCases.columns[-1]

    # 2. Get - Total number of infections reported
    # i.e. sum all values in latest update column
    totalInfectionCases = confirmedGlobalCases[confirmedGlobalCases.columns[-1]].sum()

    # 3. Get - Total infections per country
    infectionCountsPerCountry = confirmedGlobalCases[[
        'Country/Region', confirmedGlobalCases.columns[-1]]]
    infectionCountsPerCountry.columns = ["country", "infections"] # rename columns
    countries = infectionCountsPerCountry.groupby(
        'country').sum()  # group similar named countries
    countries = countries.sort_values(
        by="infections", ascending=False)  # sort by largets number of infections
    country = countries.index.tolist()
    infections = countries.infections.values.tolist()

    df2 = confirmedGlobalCases[list(
        confirmedGlobalCases.columns[1:2])+list([confirmedGlobalCases.columns[-2]])]
    df2.columns = ['Country/Region', 'values']
    countsVal = list(df2['values'].values)
    maxVal = max(countsVal)
    return lastUpdateDate, totalInfectionCases, country, infections, maxVal

def getMapData(country, infections):
    """ Get data to populate on the world map. """

    # read in data
    # map country names from highcharts
    map_data = pd.read_json(
        'https://cdn.jsdelivr.net/gh/highcharts/highcharts@v7.0.0/samples/data/world-population-density.json')

    # search our data
    new_map = []

    # make lists from dataframe columns
    map_countries = list(map_data.name)
    map_code = list(map_data.code)
    map_code3 = list(map_data.code3)
    map_value = list(map_data.value)

    cnt = 0  # counter variable

    for i in map_countries:

        if i in country:
            # get country index
            country_index = country.index(i)

            map_dict = {}

            
            map_dict["code3"] = map_code3[cnt]
            map_dict["name"]  = map_countries[cnt]
            map_dict["value"] = int(infections[country_index])
            map_dict["code"]  = map_code[cnt]
            new_map.append(map_dict)

        else:
            # can't match country, rename value as undefined
            map_dict = {}
            map_dict["code3"] = map_code3[cnt]
            map_dict["name"]  = map_countries[cnt]
            map_dict["value"] = 0
            map_dict["code"]  = map_code[cnt]
            new_map.append(map_dict)
            
            pass

        cnt = cnt+1

    return new_map

def selectCountry(request):
    """ Select country and display statistics. """
  
    # read in data
    confirmedGlobalCases = pd.read_csv(
        'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv', encoding='utf-8', na_values=None)

    # Date data was last updated
    lastUpdateDate = confirmedGlobalCases.columns[-1]

    # Total number of infections reported
    # sum all values in latest update column
    totalInfectionCases = confirmedGlobalCases[confirmedGlobalCases.columns[-1]].sum()

    # 2. Get total infections per country
    infectionCountsPerCountry = confirmedGlobalCases[[
        'Country/Region', confirmedGlobalCases.columns[-1]]]
    infectionCountsPerCountry.columns = ["country", "infections"]
    countries = infectionCountsPerCountry.groupby(
        'country').sum()  # group similar named countries
    countries = countries.sort_values(
        by="infections", ascending=False)# sort by largets number of infections
    country = countries.index.tolist()
    infections = countries.infections.values.tolist()

    # get country selected from page button
    #print(request.POST.dict())
    selectedCountry = request.POST.get("countryName")
    print("Chose: ", selectedCountry)

    # 3. Get all country data and sum it
    countryDataSummed = pd.DataFrame(confirmedGlobalCases[confirmedGlobalCases['Country/Region'] == selectedCountry][confirmedGlobalCases.columns[4:-1]].sum()).reset_index()

    countryDataSummed.columns = ["country","infections"] # rename columns
    countryDataSummed['lagValue'] = countryDataSummed['infections'].shift(1).fillna(0)
    countryDataSummed['incrementalValue'] = countryDataSummed['infections'] - \
        countryDataSummed['lagValue']
    countryDataSummed['rollingMean'] = countryDataSummed['incrementalValue'].rolling(window=7).mean()
    countryDataSummed = countryDataSummed.fillna(0)
    #data = [{'label1': 'Daily Cumulated Data', 'data1':countryDataSummed['infections'].values.tolist()},
    #        {'label2': '7 Day Rolling Mean', 'data2': countryDataSummed['rollingMean'].values.tolist()}]
    data1 = countryDataSummed['infections'].values.tolist()
    label1 = 'Daily Cumulated Infections'
    data2 = countryDataSummed['rollingMean'].values.tolist()
    label2 = '7 Day Rolling Mean'
    xdata = countryDataSummed.index.tolist()

    # determine wether or not to show world map
    showMap="False"

    context = {'totalInfectionCases': totalInfectionCases,
               'lastUpdateDate': lastUpdateDate,
               'infections': infections,
               'country': country,
               #'mapData': map_data,
               'showMap': showMap,
               'data1': data1,
               'label1': label1,
               'data2': data2,
               'label2':label2,
               'xdata':xdata,
               'selectedCountry': selectedCountry}

    return render(request, 'index.html', context)
