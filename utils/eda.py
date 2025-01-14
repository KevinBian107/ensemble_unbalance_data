import pandas as pd
from itertools import chain
import numpy as np
from pathlib import Path
import plotly.express as px
pd.options.plotting.backend = 'plotly'

'''Functions for transformation and data cleaning'''

def initial(df):
    '''Initial claeaning and megrging of two df, add average ratings'''

    # fill 0 with np.NaN
    df['rating'] = df['rating'].apply(lambda x: np.NaN if x==0 else x)

    # not unique recipe_id
    avg = df.groupby('recipe_id')[['rating']].mean().rename(columns={'rating':'avg_rating'})
    df = df.merge(avg, how='left', left_on='recipe_id',right_index=True)
    return df


def transform_df(df):
    '''Transforming nutrition to each of its own catagory,
    tags, steps, ingredients to list,
    submission date to timestamp object,
    convert types,
    and remove 'nan' to np.NaN'''

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
    df[['calories','total_fat','sugar',
        'sodium','protein','sat_fat','carbs']] = df[['calories','total_fat','sugar',
                                                     'sodium','protein','sat_fat','carbs']].astype(float)
    
    df[['user_id','recipe_id','contributor_id']] = df[['user_id','recipe_id','contributor_id']].astype(str)

    # there are 'nan' values, remove that
    for col in df.select_dtypes(include='object'):
        df[col] = df[col].apply(lambda x: np.NaN if x=='nan' else x)

    return df


def outlier(df):
    '''take care of outliers in the data frame'''
    # Remove outlier in graph dierctly

    check = ['minutes', 'n_steps', 'n_ingredients', 'calories', 'total_fat', 'sugar', 'sodium', 'protein', 'sat_fat', 'carbs']
    for col in check:#df.select_dtypes(include='number'):
        q_low = df[col].quantile(0.01)
        #print(q_low)
        q_hi  = df[col].quantile(0.99)
        #print(q_hi)
        df = df[(df[col]<q_hi) & (df[col]>q_low)]

    return df #same name so update df


def norm(df):
    '''for standarlization of the numerical values in thed ata frame'''
    for col in df.select_dtypes(include='number').columns: 
        df[col] = df[col]/df[col].abs().max()
    return df


def group_recipe(df):
    func = lambda x: list(x)
    check_dict = {'minutes':'mean', 'n_steps':'mean', 'n_ingredients':'mean',
                'avg_rating':'mean', 'rating':'mean', 'calories':'mean',
                'total_fat':'mean', 'sugar':'mean', 'sodium':'mean',
                'protein':'mean', 'sat_fat':'mean', 'carbs':'mean',
                'steps':'first', 'name':'first', 'description':'first',
                'ingredients':func, 'user_id':func, 'contributor_id':func,
                'review_date':func, 'review':func,  'recipe_date':func,
                'tags':lambda x: list(chain.from_iterable(x))}

    grouped = df.groupby('recipe_id').agg(check_dict)
    #grouped['rating'] = grouped['rating'].astype(int)

    return grouped


def group_user(df):
    '''function for grouping by unique user_id and concating all steps/names/tags of recipe and averaging rating give'''
    
    return (df #[df['rating']==5]
            .groupby('user_id')['steps','rating','name','tags','minutes','calories','description','n_ingredients','ingredients','contributor_id','review']
            .agg({'steps':lambda x: list(chain.from_iterable(x)),
                  'name':lambda x: list(x),
                  'tags':lambda x: list(chain.from_iterable(x)),
                  'rating':'mean',
                  'minutes':'mean',
                  'calories':'mean',
                  'description':lambda x: list(x),
                  'n_ingredients':'mean',
                  'ingredients':lambda x: list(chain.from_iterable(x)),
                  'contributor_id':lambda x: list(x),
                  'review':lambda x: list(x),
                  })
    )