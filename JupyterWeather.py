#!/usr/bin/env python
# coding: utf-8

# In[48]:


import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import re
import datetime
from os import path
import subprocess
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


# In[49]:


import pandas as pd
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

file_name = 'torontoWeather.{}.html'

month_dict = {
    'january': 1,
    'february': 2,
    'march': 3,
    'april': 4,
    'may': 5,
    'june': 6,
    'july': 7,
    'august': 8,
    'september': 9,
    'october': 10,
    'november': 11,
    'december': 12
}

def createAllCsvFiles(startYear, endYear):
    weatherDataFrame = pd.DataFrame(columns=['City', 'dayOfYear', 'month', 'dayOfMonth', 'Year', 'highTemp', 'lowTemp', 'precipitation'])
    
    for year in range(startYear, endYear + 1):  
        filename = file_name.format(year)
        
        if not path.exists(filename):
            print(f"File {filename} does not exist. Skipping.")
            continue
        
        html_df = pd.read_html(filename)
        html_df.pop(0) 
        html_df.pop()
        year_df = pd.concat(html_df, ignore_index=True)

        year_df['High (°C)'] = pd.to_numeric(year_df['High (°C)'], errors='coerce').fillna(0)
        year_df['Low (°C)'] = pd.to_numeric(year_df['Low (°C)'], errors='coerce').fillna(0)
        year_df['Precip. (cm)'] = pd.to_numeric(year_df['Precip. (cm)'], errors='coerce').fillna(0)

        new_year_df = pd.DataFrame(columns=['City', 'dayOfYear', 'month', 'dayOfMonth', 'Year', 'highTemp', 'lowTemp', 'precipitation'])
        new_year_df['month'] = year_df['Day'].str.split().str[0].str.lower().map(month_dict).astype(int)
        new_year_df['dayOfMonth'] = year_df['Day'].str.split().str[1].astype(int)
        new_year_df['highTemp'] = year_df['High (°C)']
        new_year_df['lowTemp'] = year_df['Low (°C)']
        new_year_df['precipitation'] = year_df['Precip. (cm)']
        new_year_df['dayOfYear'] = new_year_df.index + 1
        new_year_df['City'] = 'Toronto'
        new_year_df['Year'] = year

        year_csv_name = file_name.format(year) + '.csv'
        new_year_df.to_csv(year_csv_name, index=False)
        weatherDataFrame = pd.concat([weatherDataFrame, new_year_df], ignore_index=True)


  
    weatherDataFrame[['dayOfYear', 'month', 'dayOfMonth', 'Year']] = weatherDataFrame[['dayOfYear', 'month', 'dayOfMonth', 'Year']].astype(int)
    
    return weatherDataFrame.sort_values(by=['Year', 'month', 'dayOfMonth'], ascending=True)

pdFrame = createAllCsvFiles(1900,2023)
print(pdFrame)


# In[57]:


def showWeatherByDayMonthYear(pdFrame, day, month, year):
    
    months = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']


    filtered_df = pdFrame[(pdFrame['dayOfMonth'] == day) &
                          (pdFrame['month'] == month) &
                          (pdFrame['Year'] == year)]
    if len(filtered_df)>0:

        result = 'Year : {} , Month : {}, Day : {}, High Temperature: {}°C, Low Temperature: {}°C, Total Precipitation: {} cm'.format(
            filtered_df['Year'].values[0], months[int(filtered_df['month'].values[0])], filtered_df['dayOfMonth'].values[0], filtered_df['highTemp'].values[0], filtered_df['lowTemp'].values[0], filtered_df['precipitation'].values[0]
        )
    else:
        result = 'No Data Found'
        
    print(result)

print("1. Displaying Weather by Month and Year")
showWeatherByDayMonthYear(pdFrame, 15, 10, 2002)


# In[51]:


def showWeatherByDayForAllYears(pdFrame, dayNum):

    filtered_df = pdFrame[pdFrame['dayOfYear'] == dayNum]
    

    mean_high_temp = round(filtered_df['highTemp'].mean(), 2)
    mean_low_temp = round(filtered_df['lowTemp'].mean(), 2)
    mean_precipitation = round(filtered_df['precipitation'].mean(), 2)

    
    result = "Mean High Temperature: {:.1f}°C\nMean Low Temperature: {:.1f}°C\nMean Total Precipitation: {:.1f} cm".format(mean_high_temp, mean_low_temp, mean_precipitation)
    
    print(result)
print("2. Displaying Weather by All Year (1900-2023)")
showWeatherByDayForAllYears(pdFrame, 36)


# In[52]:


def showWeatherByMonthAndYear(pdFrame, year, month):

    filtered_df = pdFrame[(pdFrame['Year'] == year) & (pdFrame['month'] == month)]

    high_temp = filtered_df['highTemp'].max()
    low_temp = filtered_df['lowTemp'].min()
    total_precipitation = filtered_df['precipitation'].sum()
    mean_temp = filtered_df[['highTemp', 'lowTemp']].mean().mean()

    result = f"Highest Temperature: {round(high_temp, 2)}\nLowest Temperature: {round(low_temp, 2)}\nTotal Precipitation: {round(total_precipitation, 2)}\nMean Temperature: {round(mean_temp, 2)}"
    print(result)

print("3. Displaying Weather by Specfic year and month")
showWeatherByMonthAndYear(pdFrame, 2002, 9)



# In[61]:


def showWeatherByMonthForAllYears(pdFrame, month):
    
    filtered_df = pdFrame[pdFrame['month'] == month]
    

    mean_high_temp = filtered_df['highTemp'].mean()
    mean_low_temp = filtered_df['lowTemp'].mean()
    mean_precipitation = filtered_df['precipitation'].mean()
    
    result = f"Mean High Temperature: {round(mean_high_temp, 2)}\nMean Low Temperature: {round(mean_low_temp, 2)}\nMean Precipitation: {round(mean_precipitation, 2)}"
    print(result)
    
print("4. Displaying Weather by All years and specific month")
showWeatherByMonthForAllYears(pdFrame , 12)


# In[70]:


def graphWeatherByMonthForEachYear(pdFrame, month):
    filtered_df = pdFrame[pdFrame['month'] == month]
    
    grouped_df = filtered_df.groupby('Year')
    
    fig, bargraph = plt.subplots()
    
    mean_high_temps = []
    mean_low_temps = []
    years = []
    bar_width = 0.35
    
    for year, group in grouped_df:
        years.append(int(year))
        mean_high_temps.append(group['highTemp'].mean())
        mean_low_temps.append(group['lowTemp'].mean())

    index = np.arange(len(years))
    rects1 = bargraph.bar(index, mean_high_temps, bar_width, label='Mean High', color='red')
    rects2 = bargraph.bar(index + bar_width, mean_low_temps, bar_width, label='Mean Low', color='blue')

    bargraph.set_title(f"Mean High and Low Temperatures for Month {int(month)}")
    bargraph.set_xlabel("Year")
    bargraph.set_ylabel("Temperature (Celsius)")
    bargraph.legend()
    
    bargraph.set_xticks(index + bar_width / 2)
    bargraph.set_xticklabels(years, rotation=45)

    for rect1, rect2 in zip(rects1, rects2):
        height1 = rect1.get_height()
        height2 = rect2.get_height()
        bargraph.annotate(f'{height1:.1f}',
                          xy=(rect1.get_x() + rect1.get_width() / 2, height1),
                          xytext=(0, 5),  
                          textcoords="offset points",
                          ha='center',
                          va='bottom',
                          fontsize=8, 
                          bbox=dict(boxstyle="round,pad=0.3", edgecolor="none", facecolor="white", alpha=0.5))
        bargraph.annotate(f'{height2:.1f}',
                          xy=(rect2.get_x() + rect2.get_width() / 2, height2),
                          xytext=(0, 5),
                          textcoords="offset points",
                          ha='center',
                          va='bottom',
                          fontsize=8, 
                          bbox=dict(boxstyle="round,pad=0.3", edgecolor="none", facecolor="white", alpha=0.5))



        
    plt.tight_layout()
    plt.show()
print("5. Displaying Weather by All years and specific month")
graphWeatherByMonthForEachYear(pdFrame, 10)


# In[63]:


def graphWeatherByDayForEachYear(pdFrame, dayNum):
    
    filtered_df = pdFrame[pdFrame['dayOfYear'] == dayNum]
    grouped_df = filtered_df.groupby('Year')

    years = []
    high_temps = []
    low_temps = []
    precipitation = []


    for year, group in grouped_df:
        years.append(year)
        high_temps.append(group['highTemp'].mean())
        low_temps.append(group['lowTemp'].mean())
        precipitation.append(group['precipitation'].mean())

    x = range(len(years))
    width = 0.25

    fig, ax1 = plt.subplots()

   
    ax1.bar(x, high_temps, width, label='Mean High Temp', color='red')
    ax1.bar([i + width for i in x], low_temps, width, label='Mean Low Temp', color='blue')
    ax1.set_xlabel("Year")
    ax1.set_ylabel("Temperature (Celsius)")
    ax1.set_xticks([i + width for i in x])
    ax1.set_xticklabels(years)
    ax1.legend(loc="upper left")


    ax2 = ax1.twinx()
    ax2.bar([i + 2*width for i in x], precipitation, width, label='Mean Precipitation', color='green')
    ax2.set_ylabel("Precipitation (mm)")
    ax2.legend(loc="upper right")

    ax1.set_title(f"Mean High, Low Temperatures and Precipitation for Day {dayNum}")

    plt.show()

print("6. Displaying Weather by All years and specific Day")
graphWeatherByDayForEachYear(pdFrame, 128)


# In[ ]:




