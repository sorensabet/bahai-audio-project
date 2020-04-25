# -*- coding: utf-8 -*-
"""
Created on Sat Feb 22 19:13:34 2020

@author: Darth
"""
import numpy as np
import re
import os
import string
import urllib
import shutil 
import pandas as pd
from urllib import request
from urllib.request import urlretrieve
from bs4 import BeautifulSoup as bs

import io



# Step 1. Get html from webpage                                                 (DONE)
# Step 2. Get relevant table                                                    (DONE)
# Step 3. Parse for relevant data and put into pandas                           (DONE)
# Step 4. Generate PDF links based on website structure                         (DONE)
# Step 5. Make a folder for each message with the correct naming convention     (DONE)
# Step 5a)  Download the PDF with correct naming                                (DONE)
# Step 5b)  Make a text file with the description for YouTube videos 
# Step 5c)  Write text file to new folder 
# Step 6) Record all messages 

url = 'https://www.bahai.org/library/authoritative-texts/the-universal-house-of-justice/messages/#20191201_001'
pdf_url = 'https://www.bahai.org/library/authoritative-texts/the-universal-house-of-justice/messages/'
uhj_recordings_folder = r'C:\\Users\\Darth\\Desktop\\Writings Recordings\\UHJ\\'
soup = bs(request.urlopen(url).read(), "html.parser")     
table = soup.find(id="letterstable") 
table_rows = list(table.findAll(lambda tag: tag.name=='tr'))

df = pd.DataFrame(table_rows, columns=['raw_text'])
df['raw_text'] = df['raw_text'].astype(str)
df['id'] = df['raw_text'].str.extract(r'id="(.*?)(?=">)')
df = df.loc[~df['id'].isnull()]
df['date'] = pd.to_datetime(df['id'].str.split('_').str[0])
date = df['id'].str
df['date_str'] = df['date'].dt.strftime('%Y-%m-%d')
#df['date_str'] = date[:4] + '-' + date[4:6] + '-' + date[6:8]

temp = df['raw_text'].str.extractall(r'<a href=.+?>(.*?)<\/a>').reset_index()

to_df = temp.loc[temp['match'] == 0]
to_df.index = to_df['level_0']
to_df.drop(columns={'match', 'level_0'}, inplace=True)

rec_df = temp.loc[temp['match'] == 1]
rec_df.index = rec_df['level_0']
rec_df.drop(columns={'match', 'level_0'}, inplace=True)

sub_df = temp.loc[temp['match'] == 2]
sub_df.index = sub_df['level_0']
sub_df.drop(columns={'match', 'level_0'}, inplace=True)

df['stated_date'] = to_df[0]
df['recipient'] = rec_df[0]
df['subject'] = sub_df[0]
df['pdf'] = pdf_url + df['id'] + '/' + df['id'] + '.pdf'
df.drop(columns={'raw_text', 'id', 'date'}, inplace=True)


df['cum_count'] = df.groupby('date_str').cumcount() + 1
df['date_str'] = np.where(df['cum_count'] > 1, df['date_str'] + '_' + df['cum_count'].astype(str), df['date_str'])

# Okay. I now hav all the information that I need. 
# Next step: 
# Iteratively make a folder for each row, download the pdf to that folder, and make a text file with the explanation for youtube. 

path = r'C:\Users\Darth\Desktop\Writings Recordings\UHJ\0 - AUTO_GENERATE_FOLDERS\unused_folders'

if (os.path.exists(path)):
    shutil.rmtree(path)
os.mkdir(path)

# Okay. Now, I need to check for the ones that have already been completed so it doesn't generate them again. 
subfolders = pd.DataFrame([ f.path for f in os.scandir(uhj_recordings_folder) if f.is_dir() ])
subfolders[0] = subfolders[0].str.extract(r'(\d{0,4}-\d{0,2}-\d{0,2})')

df = df.loc[~df['date_str'].isin(subfolders[0])]

rcount = 0
for row in df.iterrows():
    
    print('Now on: ' + str(row[0]))
    
    folder_name = (row[1]['date_str'] + ' - ' + row[1]['subject'][0:min(100,len(row[1]['subject']))]).strip()
    
    os.mkdir(path + '\\' + folder_name)
    
    pdf_path = path + '\\' + folder_name
    
    urlretrieve(row[1]['pdf'],  pdf_path + '\\' + row[1]['date_str']  + '.pdf')

    line1 = 'This is a reading of the ' + str(row[1]['stated_date']) + ' message from the Universal House of Justice ' + row[1]['recipient'] + ' ' + row[1]['subject'] + '.\n\n'
    line2 = 'The full text of the letter is available online at: ' + row[1]['pdf'] + '\n\n'
    line3 = 'Read by Soren Sabet Sarvestany'
    line4 = 'Universal House of Justice,Audiobook,UHJ messages,Bahai,Audio reading,Bahai Audio Project,English Audio Reading,' + row[1]['date_str'] + ',' + row[1]['subject']
    
    
    print(line1)
#    print(line2)
#    print(line3)
#    print(line4)
        
    with io.open(pdf_path + '\\' + 'text_file.txt', "w", encoding="utf-8") as f:
        f.write(line1)
        f.write('')
        f.write(line2)
        f.write('')
        f.write(line3)
        f.write('')
        f.write('')
        f.write('Tags: ')
        f.write(line4)
    
    
    
#    if (rcount > 5):
#        break

    
#    
#This is a reading of the 27 December 2005 message from the Universal House of Justice to the Conference of the Continental Boards of Counsellors. 
#
#The full text of the letter is available online at: https://www.bahai.org/library/authori...
#
#Read by Soren Sabet Sarvestany
