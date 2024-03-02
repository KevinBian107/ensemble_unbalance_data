import pandas as pd
import numpy as np
from pathlib import Path
import plotly.express as px
pd.options.plotting.backend = 'plotly'



'''Functions for transformation and data cleaning'''

def initial(df):
    '''Initial claeaning and megrging of two df, add average ratings'''

    df['rating'] = df['rating'].fillna(0)
    # not unique recipe_id, unique user_id
    avg = df.groupby('recipe_id')[['rating']].mean().rename(columns={'rating':'avg_rating'})
    df = df.merge(avg, how='left', left_on='recipe_id',right_index=True)
    return df

def transform_df(df):
    '''Transforming nutrition to each of its own catagory,
    tags, steps, ingredients to list,
    submission date to timestamp object,
    and convert types'''
    
    # Convert nutrition to its own caatgory
    data = df['nutrition'].str.strip('[]').str.split(',').to_list()
    name = {0:'calories',1:'total_fat',2:'sugar',3:'sodium',4:'protein',5:'sat_fat',6:'carbs'}
    #zipped = data.apply(lambda x: list(zip(name, x)))
    new = pd.DataFrame(data).rename(columns=name)

    df = df.merge(new,how='inner',right_index=True, left_index=True)
    df = df.drop(columns=['nutrition'])

    # Convert to list
    def convert_to_list(text):
        return text.strip('[]').replace("'",'').split(', ')
    
    df['tags'] = df['tags'].apply(lambda x: convert_to_list(x))
    df['ingredients'] = df['ingredients'].apply(lambda x: convert_to_list(x))

    # it's correct, just some are long sentences, doesn't see "'", notice spelling
    df['steps'] = df['steps'].apply(lambda x: convert_to_list(x)) #some white space need to be handled

    # submission date to time stamp object
    format ='%Y-%m-%d'
    df['submitted'] = pd.to_datetime(df['submitted'],format=format)
    df['date'] = pd.to_datetime(df['date'],format=format)

    # drop not needed & rename
    df = df.drop(columns=['id']).rename(columns={'submitted':'recipe_date','date':'review_date'})


    # Convert data type
    df[['calories','total_fat','sugar','sodium','protein','sat_fat','carbs']] = df[['calories','total_fat','sugar','sodium','protein','sat_fat','carbs']].astype(float)
    #df['user_id'] = df['user_id'].astype(int)
    #df['recipe_id'] = df['recipe_id'].astype(int)

    return df

def outlier(df):
    '''take care of outliers in the data frame'''
    for col in df.select_dtypes(include='number'):
        #print(col)
        q_low = df[col].quantile(0.2)
        q_hi  = df[col].quantile(0.8)
        df_filtered = df[(df[col]<q_hi) & (df[col]>q_low)]

    return df_filtered


def norm(df):
    '''for standarlization of the numerical values in thed ata frame'''
    for col in df.select_dtypes(include='number').columns: 
        df[col] = df[col]/df[col].abs().max()
    return df