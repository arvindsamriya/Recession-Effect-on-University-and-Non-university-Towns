
# coding: utf-8

# ---
# 
# _You are currently looking at **version 1.1** of this notebook. To download notebooks and datafiles, as well as get help on Jupyter notebooks in the Coursera platform, visit the [Jupyter Notebook FAQ](https://www.coursera.org/learn/python-data-analysis/resources/0dhYG) course resource._
# 
# ---

# In[9]:


import pandas as pd
import numpy as np
from scipy.stats import ttest_ind


# # Assignment 4 - Hypothesis Testing
# This assignment requires more individual learning than previous assignments - you are encouraged to check out the [pandas documentation](http://pandas.pydata.org/pandas-docs/stable/) to find functions or methods you might not have used yet, or ask questions on [Stack Overflow](http://stackoverflow.com/) and tag them as pandas and python related. And of course, the discussion forums are open for interaction with your peers and the course staff.
# 
# Definitions:
# * A _quarter_ is a specific three month period, Q1 is January through March, Q2 is April through June, Q3 is July through September, Q4 is October through December.
# * A _recession_ is defined as starting with two consecutive quarters of GDP decline, and ending with two consecutive quarters of GDP growth.
# * A _recession bottom_ is the quarter within a recession which had the lowest GDP.
# * A _university town_ is a city which has a high percentage of university students compared to the total population of the city.
# 
# **Hypothesis**: University towns have their mean housing prices less effected by recessions. Run a t-test to compare the ratio of the mean price of houses in university towns the quarter before the recession starts compared to the recession bottom. (`price_ratio=quarter_before_recession/recession_bottom`)
# 
# The following data files are available for this assignment:
# * From the [Zillow research data site](http://www.zillow.com/research/data/) there is housing data for the United States. In particular the datafile for [all homes at a city level](http://files.zillowstatic.com/research/public/City/City_Zhvi_AllHomes.csv), ```City_Zhvi_AllHomes.csv```, has median home sale prices at a fine grained level.
# * From the Wikipedia page on college towns is a list of [university towns in the United States](https://en.wikipedia.org/wiki/List_of_college_towns#College_towns_in_the_United_States) which has been copy and pasted into the file ```university_towns.txt```.
# * From Bureau of Economic Analysis, US Department of Commerce, the [GDP over time](http://www.bea.gov/national/index.htm#gdp) of the United States in current dollars (use the chained value in 2009 dollars), in quarterly intervals, in the file ```gdplev.xls```. For this assignment, only look at GDP data from the first quarter of 2000 onward.
# 
# Each function in this assignment below is worth 10%, with the exception of ```run_ttest()```, which is worth 50%.

# In[72]:


# Use this dictionary to map state names to two letter acronyms
states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 'NA': 'National', 'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana', 'IL': 'Illinois', 'TN': 'Tennessee', 'DC': 'District of Columbia', 'VT': 'Vermont', 'ID': 'Idaho', 'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan', 'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 'GU': 'Guam', 'MS': 'Mississippi', 'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas', 'SD': 'South Dakota', 'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 'MO': 'Missouri', 'CT': 'Connecticut', 'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana', 'KS': 'Kansas', 'NY': 'New York', 'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 'CA': 'California', 'CO': 'Colorado', 'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island', 'MN': 'Minnesota', 'VI': 'Virgin Islands', 'NH': 'New Hampshire', 'MA': 'Massachusetts', 'GA': 'Georgia', 'ND': 'North Dakota', 'VA': 'Virginia'}


# In[3]:


def get_list_of_university_towns():
    '''Returns a DataFrame of towns and the states they are in from the 
    university_towns.txt list. The format of the DataFrame should be:
    DataFrame( [ ["Michigan", "Ann Arbor"], ["Michigan", "Yipsilanti"] ], 
    columns=["State", "RegionName"]  )
    
    The following cleaning needs to be done:

    1. For "State", removing characters from "[" to the end.
    2. For "RegionName", when applicable, removing every character from " (" to the end.
    3. Depending on how you read the data, you may need to remove newline character '\n'. '''
    import pandas as pd
    dfp=pd.read_csv('university_towns.txt',sep=('\n'),header=None)
    state=''
    dfp2=pd.DataFrame()
    for i in dfp.index:
        if 'edit' in str(dfp.loc[i]):
            state=(dfp.loc[i]).values[0]
        else:
            dic={'State':state, 'RegionName':(dfp.loc[i]).values[0]}
            dfp2=dfp2.append(dic,ignore_index=True)
    dfp2['State']=dfp2['State'].str.replace("\[.*","")
    dfp2['RegionName']=dfp2['RegionName'].str.replace(r" \(.*","")
    dfp2=dfp2.set_index('State').reset_index()
    return dfp2


# In[4]:


def get_recession_start():
    '''Returns the year and quarter of the recession start time as a 
    string value in a format such as 2005q3'''
    import pandas as pd
    df2=pd.read_excel('gdplev.xls',skiprows=5)
    df2=df2[df2.iloc[:,4]>='2000q1'].iloc[:,[4,6]]
    df2.columns=['quat','GDP']
    df2=df2.set_index('quat').reset_index()
    i=0
    result=''
    while(i<(len(df2)-1)):
        if(((df2.loc[i,'GDP'])>(df2.loc[i+1,'GDP']))and((df2.loc[i+1,'GDP'])>(df2.loc[i+2,'GDP']))):
            result=df2.loc[i+1,'quat']
            break
        else:
            i=i+1    
    return result


# In[5]:


def get_recession_end():
    '''Returns the year and quarter of the recession end time as a 
    string value in a format such as 2005q3'''
    result=get_recession_start()
    import pandas as pd
    df3=pd.read_excel('gdplev.xls',skiprows=5)
    df3=df3[df3.iloc[:,4]>=result].iloc[:,[4,6]]
    df3.columns=['quat','GDP']
    df3=df3.set_index('quat').reset_index()
    i=0
    res=''
    while(i<(len(df3)-1)):
        if(((df3.loc[i,'GDP'])<(df3.loc[i+1,'GDP']))and((df3.loc[i+1,'GDP'])<(df3.loc[i+2,'GDP']))):
            res=df3.loc[i+2,'quat']
            break
        else:
            i=i+1  
    return res


# In[6]:


def get_recession_bottom():
    '''Returns the year and quarter of the recession bottom time as a 
    string value in a format such as 2005q3'''
    start=get_recession_start()
    end=get_recession_end()
    import pandas as pd
    df4=pd.read_excel('gdplev.xls',skiprows=5)
    df4=df4[(df4.iloc[:,4]>=start )&(df4.iloc[:,4]<=end )].iloc[:,[4,6]]
    df4.columns=['quat','GDP']
    df4=df4.set_index('quat').reset_index()
    i=0
    res=''
    while(i<(len(df4)-1)):
        if((df4.loc[i,'GDP'])<(df4.loc[i+1,'GDP'])):
            res=df4.loc[i,'quat']
            break
        else:
            i=i+1  
    return res


# In[67]:


def convert_housing_data_to_quarters():
    '''Converts the housing data to quarters and returns it as mean 
    values in a dataframe. This dataframe should be a dataframe with
    columns for 2000q1 through 2016q3, and should have a multi-index
    in the shape of ["State","RegionName"].
    
    Note: Quarters are defined in the assignment description, they are
    not arbitrary three month periods.
    
    The resulting dataframe should have 67 columns, and 10,730 rows.
    '''
    df4=pd.read_csv('City_Zhvi_AllHomes.csv')
    df5=df4.iloc[:,-200::]
    #df5=df5.fillna(0)
    df5=df5[df5.columns].rename(columns=pd.to_datetime)
    df5=df5.resample('q',axis=1).mean().rename(columns=lambda x: '{:}q{:}'.format(x.year, int(x.month/4)+1))
    df5['State']=df4['State']
    df5['RegionName']=df4['RegionName']
    df5['State']=df5['State'].replace({'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 'NA': 'National', 'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana', 'IL': 'Illinois', 'TN': 'Tennessee', 'DC': 'District of Columbia', 'VT': 'Vermont', 'ID': 'Idaho', 'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan', 'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 'GU': 'Guam', 'MS': 'Mississippi', 'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas', 'SD': 'South Dakota', 'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 'MO': 'Missouri', 'CT': 'Connecticut', 'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana', 'KS': 'Kansas', 'NY': 'New York', 'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 'CA': 'California', 'CO': 'Colorado', 'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island', 'MN': 'Minnesota', 'VI': 'Virgin Islands', 'NH': 'New Hampshire', 'MA': 'Massachusetts', 'GA': 'Georgia', 'ND': 'North Dakota', 'VA': 'Virginia'})
    df5.set_index(['State','RegionName'],inplace=True)
    return df5


# In[71]:


def run_ttest():
    '''First creates new data showing the decline or growth of housing prices
    between the recession start and the recession bottom. Then runs a ttest
    comparing the university town values to the non-university towns values, 
    return whether the alternative hypothesis (that the two groups are the same)
    is true or not as well as the p-value of the confidence. 
    
    Return the tuple (different, p, better) where different=True if the t-test is
    True at a p<0.01 (we reject the null hypothesis), or different=False if 
    otherwise (we cannot reject the null hypothesis). The variable p should
    be equal to the exact p value returned from scipy.stats.ttest_ind(). The
    value for better should be either "university town" or "non-university town"
    depending on which has a lower mean price ratio (which is equivilent to a
    reduced market loss).'''
    from scipy.stats import ttest_ind
    start=get_recession_start()
    bot=get_recession_bottom()
    df6=convert_housing_data_to_quarters()
    ind=df6.columns.get_loc(start)
    before_start=df6.columns[ind-1]
    df6['price_ratio']=df6[before_start].div(df6[bot])
    df6_u= get_list_of_university_towns().set_index(['State','RegionName'])
    f=df6.index.isin(df6_u.index)
    uni=df6.loc[f==True].dropna()
    non_uni=df6.loc[f==False].dropna()
    test=ttest_ind(uni['price_ratio'],non_uni['price_ratio'])
    different=test.pvalue<0.01
    p=test.pvalue
    dictt={non_uni['price_ratio'].mean():'non-university town',uni['price_ratio'].mean():'university town'}
    better=dictt[min(dictt.keys())]
    return (different,p,better)


# In[ ]:




