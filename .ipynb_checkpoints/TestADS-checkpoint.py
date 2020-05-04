{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 5,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Python imports and dependencies\n",
    "import json\n",
    "import pandas as pd\n",
    "import numpy as np\n",
    "import re\n",
    "import sqlalchemy\n",
    "from sqlalchemy import create_engine\n",
    "import sys\n",
    "import time\n",
    "import psycopg2"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 171,
   "metadata": {},
   "outputs": [],
   "source": [
    "from config import db_password"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 7,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Define file directory info \n",
    "file_dir = 'C:/Users/dcohen/Documents/UCBE/Movies-ETL/'"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 10,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Open file\n",
    "with open(f'{file_dir}/wikipedia.movies.json', mode='r') as file:\n",
    "    wiki_movies_raw = json.load(file)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 30,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Read file again, update file name\n",
    "kaggle_metadata = pd.read_csv(f'{file_dir}movies_metadata.csv', low_memory=False)\n",
    "ratings = pd.read_csv(f'{file_dir}ratings.csv')\n",
    "# View DataFrame\n",
    "wiki_movies_df = pd.DataFrame(wiki_movies_raw)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 42,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Clean table to movies with director info\n",
    "wiki_movies = [movie for movie in wiki_movies_raw\n",
    "               if ('Director' in movie or 'Directed by' in movie)\n",
    "                   and 'imdb_link' in movie\n",
    "                   and 'No. of episodes' not in movie]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 43,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Create new data frame\n",
    "wiki_movies_df = pd.DataFrame(wiki_movies)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 62,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Consolidated columns\n",
    "\n",
    "def clean_movie(movie):\n",
    "    movie = dict(movie) #create a non-destructive copy\n",
    "    alt_titles = {}\n",
    "    # combine alternate titles into one list\n",
    "    for key in ['Also known as','Arabic','Cantonese','Chinese','French',\n",
    "                'Hangul','Hebrew','Hepburn','Japanese','Literally',\n",
    "                'Mandarin','McCune-Reischauer','Original title','Polish',\n",
    "                'Revised Romanization','Romanized','Russian',\n",
    "                'Simplified','Traditional','Yiddish']:\n",
    "        if key in movie:\n",
    "            alt_titles[key] = movie[key]\n",
    "            movie.pop(key)\n",
    "    if len(alt_titles) > 0:\n",
    "        movie['alt_titles'] = alt_titles\n",
    "\n",
    "    # merge column names\n",
    "    def change_column_name(old_name, new_name):\n",
    "        if old_name in movie:\n",
    "            movie[new_name] = movie.pop(old_name)\n",
    "    change_column_name('Adaptation by', 'Writer(s)')\n",
    "    change_column_name('Country of origin', 'Country')\n",
    "    change_column_name('Directed by', 'Director')\n",
    "    change_column_name('Distributed by', 'Distributor')\n",
    "    change_column_name('Edited by', 'Editor(s)')\n",
    "    change_column_name('Length', 'Running time')\n",
    "    change_column_name('Original release', 'Release date')\n",
    "    change_column_name('Music by', 'Composer(s)')\n",
    "    change_column_name('Produced by', 'Producer(s)')\n",
    "    change_column_name('Producer', 'Producer(s)')\n",
    "    change_column_name('Productioncompanies ', 'Production company(s)')\n",
    "    change_column_name('Productioncompany ', 'Production company(s)')\n",
    "    change_column_name('Released', 'Release Date')\n",
    "    change_column_name('Release Date', 'Release date')\n",
    "    change_column_name('Screen story by', 'Writer(s)')\n",
    "    change_column_name('Screenplay by', 'Writer(s)')\n",
    "    change_column_name('Story by', 'Writer(s)')\n",
    "    change_column_name('Theme music composer', 'Composer(s)')\n",
    "    change_column_name('Written by', 'Writer(s)')\n",
    "\n",
    "    return movie"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 64,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Create updated data frame with merged titles and columns\n",
    "\n",
    "clean_movies = [clean_movie(movie) for movie in wiki_movies]\n",
    "wiki_movies_df = pd.DataFrame(clean_movies)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 66,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "7076\n",
      "7033\n"
     ]
    },
    {
     "data": {
      "text/html": [
       "<div>\n",
       "<style scoped>\n",
       "    .dataframe tbody tr th:only-of-type {\n",
       "        vertical-align: middle;\n",
       "    }\n",
       "\n",
       "    .dataframe tbody tr th {\n",
       "        vertical-align: top;\n",
       "    }\n",
       "\n",
       "    .dataframe thead th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr style=\"text-align: right;\">\n",
       "      <th></th>\n",
       "      <th>url</th>\n",
       "      <th>year</th>\n",
       "      <th>imdb_link</th>\n",
       "      <th>title</th>\n",
       "      <th>Based on</th>\n",
       "      <th>Starring</th>\n",
       "      <th>Narrated by</th>\n",
       "      <th>Cinematography</th>\n",
       "      <th>Release date</th>\n",
       "      <th>Running time</th>\n",
       "      <th>...</th>\n",
       "      <th>Preceded by</th>\n",
       "      <th>Suggested by</th>\n",
       "      <th>alt_titles</th>\n",
       "      <th>Recorded</th>\n",
       "      <th>Venue</th>\n",
       "      <th>Label</th>\n",
       "      <th>Animation by</th>\n",
       "      <th>Color process</th>\n",
       "      <th>McCune–Reischauer</th>\n",
       "      <th>imdb_id</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>0</th>\n",
       "      <td>https://en.wikipedia.org/wiki/The_Adventures_o...</td>\n",
       "      <td>1990</td>\n",
       "      <td>https://www.imdb.com/title/tt0098987/</td>\n",
       "      <td>The Adventures of Ford Fairlane</td>\n",
       "      <td>[Characters, by Rex Weiner]</td>\n",
       "      <td>[Andrew Dice Clay, Wayne Newton, Priscilla Pre...</td>\n",
       "      <td>Andrew \"Dice\" Clay</td>\n",
       "      <td>Oliver Wood</td>\n",
       "      <td>[July 11, 1990, (, 1990-07-11, )]</td>\n",
       "      <td>102 minutes</td>\n",
       "      <td>...</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>tt0098987</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>1</th>\n",
       "      <td>https://en.wikipedia.org/wiki/After_Dark,_My_S...</td>\n",
       "      <td>1990</td>\n",
       "      <td>https://www.imdb.com/title/tt0098994/</td>\n",
       "      <td>After Dark, My Sweet</td>\n",
       "      <td>[the novel, After Dark, My Sweet, by, Jim Thom...</td>\n",
       "      <td>[Jason Patric, Rachel Ward, Bruce Dern, George...</td>\n",
       "      <td>NaN</td>\n",
       "      <td>Mark Plummer</td>\n",
       "      <td>[May 17, 1990, (, 1990-05-17, ), (Cannes Film ...</td>\n",
       "      <td>114 minutes</td>\n",
       "      <td>...</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>tt0098994</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2</th>\n",
       "      <td>https://en.wikipedia.org/wiki/Air_America_(film)</td>\n",
       "      <td>1990</td>\n",
       "      <td>https://www.imdb.com/title/tt0099005/</td>\n",
       "      <td>Air America</td>\n",
       "      <td>[Air America, by, Christopher Robbins]</td>\n",
       "      <td>[Mel Gibson, Robert Downey Jr., Nancy Travis, ...</td>\n",
       "      <td>NaN</td>\n",
       "      <td>Roger Deakins</td>\n",
       "      <td>[August 10, 1990, (, 1990-08-10, )]</td>\n",
       "      <td>113 minutes</td>\n",
       "      <td>...</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>tt0099005</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>3</th>\n",
       "      <td>https://en.wikipedia.org/wiki/Alice_(1990_film)</td>\n",
       "      <td>1990</td>\n",
       "      <td>https://www.imdb.com/title/tt0099012/</td>\n",
       "      <td>Alice</td>\n",
       "      <td>NaN</td>\n",
       "      <td>[Alec Baldwin, Blythe Danner, Judy Davis, Mia ...</td>\n",
       "      <td>NaN</td>\n",
       "      <td>Carlo Di Palma</td>\n",
       "      <td>[December 25, 1990, (, 1990-12-25, )]</td>\n",
       "      <td>106 minutes</td>\n",
       "      <td>...</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>tt0099012</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>4</th>\n",
       "      <td>https://en.wikipedia.org/wiki/Almost_an_Angel</td>\n",
       "      <td>1990</td>\n",
       "      <td>https://www.imdb.com/title/tt0099018/</td>\n",
       "      <td>Almost an Angel</td>\n",
       "      <td>NaN</td>\n",
       "      <td>[Paul Hogan, Elias Koteas, Linda Kozlowski]</td>\n",
       "      <td>NaN</td>\n",
       "      <td>Russell Boyd</td>\n",
       "      <td>December 19, 1990</td>\n",
       "      <td>95 minutes</td>\n",
       "      <td>...</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>tt0099018</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "<p>5 rows × 41 columns</p>\n",
       "</div>"
      ],
      "text/plain": [
       "                                                 url  year  \\\n",
       "0  https://en.wikipedia.org/wiki/The_Adventures_o...  1990   \n",
       "1  https://en.wikipedia.org/wiki/After_Dark,_My_S...  1990   \n",
       "2   https://en.wikipedia.org/wiki/Air_America_(film)  1990   \n",
       "3    https://en.wikipedia.org/wiki/Alice_(1990_film)  1990   \n",
       "4      https://en.wikipedia.org/wiki/Almost_an_Angel  1990   \n",
       "\n",
       "                               imdb_link                            title  \\\n",
       "0  https://www.imdb.com/title/tt0098987/  The Adventures of Ford Fairlane   \n",
       "1  https://www.imdb.com/title/tt0098994/             After Dark, My Sweet   \n",
       "2  https://www.imdb.com/title/tt0099005/                      Air America   \n",
       "3  https://www.imdb.com/title/tt0099012/                            Alice   \n",
       "4  https://www.imdb.com/title/tt0099018/                  Almost an Angel   \n",
       "\n",
       "                                            Based on  \\\n",
       "0                        [Characters, by Rex Weiner]   \n",
       "1  [the novel, After Dark, My Sweet, by, Jim Thom...   \n",
       "2             [Air America, by, Christopher Robbins]   \n",
       "3                                                NaN   \n",
       "4                                                NaN   \n",
       "\n",
       "                                            Starring         Narrated by  \\\n",
       "0  [Andrew Dice Clay, Wayne Newton, Priscilla Pre...  Andrew \"Dice\" Clay   \n",
       "1  [Jason Patric, Rachel Ward, Bruce Dern, George...                 NaN   \n",
       "2  [Mel Gibson, Robert Downey Jr., Nancy Travis, ...                 NaN   \n",
       "3  [Alec Baldwin, Blythe Danner, Judy Davis, Mia ...                 NaN   \n",
       "4        [Paul Hogan, Elias Koteas, Linda Kozlowski]                 NaN   \n",
       "\n",
       "   Cinematography                                       Release date  \\\n",
       "0     Oliver Wood                  [July 11, 1990, (, 1990-07-11, )]   \n",
       "1    Mark Plummer  [May 17, 1990, (, 1990-05-17, ), (Cannes Film ...   \n",
       "2   Roger Deakins                [August 10, 1990, (, 1990-08-10, )]   \n",
       "3  Carlo Di Palma              [December 25, 1990, (, 1990-12-25, )]   \n",
       "4    Russell Boyd                                  December 19, 1990   \n",
       "\n",
       "  Running time  ... Preceded by Suggested by alt_titles Recorded Venue Label  \\\n",
       "0  102 minutes  ...         NaN          NaN        NaN      NaN   NaN   NaN   \n",
       "1  114 minutes  ...         NaN          NaN        NaN      NaN   NaN   NaN   \n",
       "2  113 minutes  ...         NaN          NaN        NaN      NaN   NaN   NaN   \n",
       "3  106 minutes  ...         NaN          NaN        NaN      NaN   NaN   NaN   \n",
       "4   95 minutes  ...         NaN          NaN        NaN      NaN   NaN   NaN   \n",
       "\n",
       "  Animation by Color process McCune–Reischauer    imdb_id  \n",
       "0          NaN           NaN               NaN  tt0098987  \n",
       "1          NaN           NaN               NaN  tt0098994  \n",
       "2          NaN           NaN               NaN  tt0099005  \n",
       "3          NaN           NaN               NaN  tt0099012  \n",
       "4          NaN           NaN               NaN  tt0099018  \n",
       "\n",
       "[5 rows x 41 columns]"
      ]
     },
     "execution_count": 66,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "# Using regex to remove duplicate row based on IMDB ID\n",
    "\n",
    "wiki_movies_df['imdb_id'] = wiki_movies_df['imdb_link'].str.extract(r'(tt\\d{7})')\n",
    "print(len(wiki_movies_df))\n",
    "wiki_movies_df.drop_duplicates(subset='imdb_id', inplace=True)\n",
    "print(len(wiki_movies_df))\n",
    "wiki_movies_df.head()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 68,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "['url',\n",
       " 'year',\n",
       " 'imdb_link',\n",
       " 'title',\n",
       " 'Based on',\n",
       " 'Starring',\n",
       " 'Cinematography',\n",
       " 'Release date',\n",
       " 'Running time',\n",
       " 'Country',\n",
       " 'Language',\n",
       " 'Budget',\n",
       " 'Box office',\n",
       " 'Director',\n",
       " 'Distributor',\n",
       " 'Editor(s)',\n",
       " 'Composer(s)',\n",
       " 'Producer(s)',\n",
       " 'Production company(s)',\n",
       " 'Writer(s)',\n",
       " 'imdb_id']"
      ]
     },
     "execution_count": 68,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "# Remove columns that are more than 90% null \n",
    "[column for column in wiki_movies_df.columns if wiki_movies_df[column].isnull().sum() < len(wiki_movies_df) * 0.9]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 69,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Columns we want to keep\n",
    "\n",
    "wiki_columns_to_keep = [column for column in wiki_movies_df.columns if wiki_movies_df[column].isnull().sum() < len(wiki_movies_df) * 0.9]\n",
    "wiki_movies_df = wiki_movies_df[wiki_columns_to_keep]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 72,
   "metadata": {},
   "outputs": [],
   "source": [
    "#Remove anything without \"Box office\" info\n",
    "box_office = wiki_movies_df['Box office'].dropna() "
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 73,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "34                           [US$, 4,212,828]\n",
       "54      [$6,698,361 (, United States, ), [2]]\n",
       "74                    [$6,488,144, (US), [1]]\n",
       "126                [US$1,531,489, (domestic)]\n",
       "130                          [US$, 4,803,039]\n",
       "                        ...                  \n",
       "6980               [$99.6, million, [4], [5]]\n",
       "6994                   [$365.6, million, [1]]\n",
       "6995                         [$53.8, million]\n",
       "7015                     [$435, million, [7]]\n",
       "7048                   [$529.3, million, [4]]\n",
       "Name: Box office, Length: 135, dtype: object"
      ]
     },
     "execution_count": 73,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "# Convert to strings use map and/or lambda functions\n",
    "\n",
    "def is_not_a_string(x):\n",
    "    return type(x) != str\n",
    "#box_office[box_office.map(is_not_a_string)]\n",
    "box_office[box_office.map(lambda x: type(x) != str)]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 74,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Join character info on strings\n",
    "box_office = box_office.apply(lambda x: ' '.join(x) if type(x) == list else x)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 75,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Regex for getting $ figures Form 1\n",
    "form_one = r'\\$\\d+\\.?\\d*\\s*[mb]illion'"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 79,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Next code to count the box office values Form 2\n",
    "form_two = r'\\$\\d{1,3}(?:,\\d{3})+'\n",
    "#box_office.str.contains(form_two, flags=re.IGNORECASE).sum()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 80,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Match box office info\n",
    "matches_form_one = box_office.str.contains(form_one, flags=re.IGNORECASE)\n",
    "matches_form_two = box_office.str.contains(form_two, flags=re.IGNORECASE)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 81,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "34                         US$ 4,212,828\n",
       "79                              $335.000\n",
       "110                   $4.35-4.37 million\n",
       "130                        US$ 4,803,039\n",
       "600                           $5000 (US)\n",
       "731                         $ 11,146,270\n",
       "957                             $ 50,004\n",
       "1070                          35,254,617\n",
       "1147    $ 407,618 (U.S.) (sub-total) [1]\n",
       "1446                        $ 11,829,959\n",
       "1480                          £3 million\n",
       "1611                            $520.000\n",
       "1865                        ¥1.1 billion\n",
       "2032                                 N/A\n",
       "2091                                $309\n",
       "2130               US$ 171.8 million [9]\n",
       "2257                   US$ 3,395,581 [1]\n",
       "2263            $ 1,223,034 ( domestic )\n",
       "2347                            $282.175\n",
       "2638            $ 104,883 (US sub-total)\n",
       "2665         926,423 admissions (France)\n",
       "2697      $ 1.7 million (US) (sub-total)\n",
       "2823                            $414.000\n",
       "2924                            $621.000\n",
       "3088           $32 [2] –33.1 million [1]\n",
       "3631                                 TBA\n",
       "3859                  $38.9–40.3 million\n",
       "3879            CN¥3.650 million (China)\n",
       "4116                          £7,385,434\n",
       "4123                            $161.000\n",
       "4261                  $20.7–23.9 million\n",
       "4306                              $20-30\n",
       "4492                        $47.7 millon\n",
       "4561             $45.2k (only in Turkey)\n",
       "4662                USD$ 8.2 million [2]\n",
       "5362                   $ 142 million [3]\n",
       "5447                               £2.56\n",
       "5784                            413 733$\n",
       "6013                             Unknown\n",
       "6145                  $17.5–18.4 million\n",
       "6234                  $41.8–41.9 million\n",
       "6369                               $111k\n",
       "6370                                $588\n",
       "6593                      less than $372\n",
       "6829                    $ 41 million [3]\n",
       "6843                             8 crore\n",
       "6904                         $6.9 millon\n",
       "Name: Box office, dtype: object"
      ]
     },
     "execution_count": 81,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "# List of matched based on form info\n",
    "#this will throw an error!\n",
    "#box_office[(not matches_form_one) and (not matches_form_two)]\n",
    "box_office[~matches_form_one & ~matches_form_two]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 82,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Redux forms to capture new info\n",
    "form_one = r'\\$\\s*\\d+\\.?\\d*\\s*[mb]illion'\n",
    "               #form_two = r'\\$\\s*\\d{1,3}(?:,\\d{3})+'\n",
    "               #form_two = r'\\$\\s*\\d{1,3}(?:[,\\.]\\d{3})+'\n",
    "form_two = r'\\$\\s*\\d{1,3}(?:[,\\.]\\d{3})+(?!\\s[mb]illion)'"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 83,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Fix range issues with numbers\n",
    "box_office = box_office.str.replace(r'\\$.*[-—–](?![a-z])', '$', regex=True)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 90,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Section 8.3.10 code\n",
    "def parse_dollars(s):\n",
    "    # if s is not a string, return NaN\n",
    "    if type(s) != str:\n",
    "        return np.nan\n",
    "\n",
    "    # if input is of the form $###.# million\n",
    "    if re.match(r'\\$\\s*\\d+\\.?\\d*\\s*milli?on', s, flags=re.IGNORECASE):\n",
    "\n",
    "        # remove dollar sign and \" million\"\n",
    "        s = re.sub('\\$|\\s|[a-zA-Z]','', s)\n",
    "\n",
    "        # convert to float and multiply by a million\n",
    "        value = float(s) * 10**6\n",
    "\n",
    "        # return value\n",
    "        return value\n",
    "\n",
    "    # if input is of the form $###.# billion\n",
    "    elif re.match(r'\\$\\s*\\d+\\.?\\d*\\s*billi?on', s, flags=re.IGNORECASE):\n",
    "\n",
    "        # remove dollar sign and \" billion\"\n",
    "        s = re.sub('\\$|\\s|[a-zA-Z]','', s)\n",
    "\n",
    "        # convert to float and multiply by a billion\n",
    "        value = float(s) * 10**9\n",
    "\n",
    "        # return value\n",
    "        return value\n",
    "\n",
    "    # if input is of the form $###,###,###\n",
    "    elif re.match(r'\\$\\s*\\d{1,3}(?:[,\\.]\\d{3})+(?!\\s[mb]illion)', s, flags=re.IGNORECASE):\n",
    "\n",
    "        # remove dollar sign and commas\n",
    "        s = re.sub('\\$|,','', s)\n",
    "\n",
    "        # convert to float\n",
    "        value = float(s)\n",
    "\n",
    "        # return value\n",
    "        return value\n",
    "\n",
    "    # otherwise, return NaN\n",
    "    else:\n",
    "        return np.nan"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 91,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Update to data frame (getting a warning message)\n",
    "wiki_movies_df['box_office'] = box_office.str.extract(f'({form_one}|{form_two})', flags=re.IGNORECASE)[0].apply(parse_dollars)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 92,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Drop box office info but the data frame is returning a warning message\n",
    "wiki_movies_df.drop('Box office', axis=1, inplace=True)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 94,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Budget info with dropped null values\n",
    "budget = wiki_movies_df['Budget'].dropna()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 95,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Lambda function to drop nulls\n",
    "budget = budget.map(lambda x: ' '.join(x) if type(x) == list else x)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 96,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Regex function to drop nulls\n",
    "budget = budget.str.replace(r'\\$.*[-—–](?![a-z])', '$', regex=True)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 97,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "136                         Unknown\n",
       "204     60 million Norwegian Kroner\n",
       "478                         Unknown\n",
       "973             $34 [3] [4] million\n",
       "1126               $120 [4] million\n",
       "1226                        Unknown\n",
       "1278                            HBO\n",
       "1374                     £6,000,000\n",
       "1397                     13 million\n",
       "1480                   £2.8 million\n",
       "1734                   CAD2,000,000\n",
       "1913     PHP 85 million (estimated)\n",
       "1948                    102,888,900\n",
       "1953                   3,500,000 DM\n",
       "1973                     ₤2,300,874\n",
       "2281                     $14 milion\n",
       "2451                     ₤6,350,000\n",
       "3144                   € 40 million\n",
       "3360               $150 [6] million\n",
       "3418                        $218.32\n",
       "3802                   £4.2 million\n",
       "3906                            N/A\n",
       "3959                    760,000 USD\n",
       "4470                       19 crore\n",
       "4641                    £17 million\n",
       "5034              $$200 [4] million\n",
       "5055           $155 [2] [3] million\n",
       "5419                $40 [4] million\n",
       "5424                            N/A\n",
       "5447                     £4 million\n",
       "5671                    €14 million\n",
       "5687                   $ dead link]\n",
       "6385               £ 12 million [3]\n",
       "6593                     £3 million\n",
       "6821                  £12.9 million\n",
       "6843                      3.5 crore\n",
       "6895                        919,000\n",
       "7070                   €4.3 million\n",
       "Name: Budget, dtype: object"
      ]
     },
     "execution_count": 97,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "# View budget info\n",
    "matches_form_one = budget.str.contains(form_one, flags=re.IGNORECASE)\n",
    "matches_form_two = budget.str.contains(form_two, flags=re.IGNORECASE)\n",
    "budget[~matches_form_one & ~matches_form_two]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 98,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "136                         Unknown\n",
       "204     60 million Norwegian Kroner\n",
       "478                         Unknown\n",
       "973                     $34 million\n",
       "1126                   $120 million\n",
       "1226                        Unknown\n",
       "1278                            HBO\n",
       "1374                     £6,000,000\n",
       "1397                     13 million\n",
       "1480                   £2.8 million\n",
       "1734                   CAD2,000,000\n",
       "1913     PHP 85 million (estimated)\n",
       "1948                    102,888,900\n",
       "1953                   3,500,000 DM\n",
       "1973                     ₤2,300,874\n",
       "2281                     $14 milion\n",
       "2451                     ₤6,350,000\n",
       "3144                   € 40 million\n",
       "3360                   $150 million\n",
       "3418                        $218.32\n",
       "3802                   £4.2 million\n",
       "3906                            N/A\n",
       "3959                    760,000 USD\n",
       "4470                       19 crore\n",
       "4641                    £17 million\n",
       "5034                  $$200 million\n",
       "5055                   $155 million\n",
       "5419                    $40 million\n",
       "5424                            N/A\n",
       "5447                     £4 million\n",
       "5671                    €14 million\n",
       "5687                   $ dead link]\n",
       "6385                  £ 12 million \n",
       "6593                     £3 million\n",
       "6821                  £12.9 million\n",
       "6843                      3.5 crore\n",
       "6895                        919,000\n",
       "7070                   €4.3 million\n",
       "Name: Budget, dtype: object"
      ]
     },
     "execution_count": 98,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "# Match budget info to 8.3.11\n",
    "budget = budget.str.replace(r'\\[\\d+\\]\\s*', '')\n",
    "budget[~matches_form_one & ~matches_form_two]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 99,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Run datafram to view updated info. Still getting warning meesage. Switched from Python3 to PythonData but same message. May need to create a new data frame or make a copy.\n",
    "wiki_movies_df['budget'] = budget.str.extract(f'({form_one}|{form_two})', flags=re.IGNORECASE)[0].apply(parse_dollars)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 100,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Show budget info\n",
    "wiki_movies_df.drop('Budget', axis=1, inplace=True)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 101,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Review release date info\n",
    "release_date = wiki_movies_df['Release date'].dropna().apply(lambda x: ' '.join(x) if type(x) == list else x)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 102,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Create new date variables\n",
    "date_form_one = r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\\s[123]\\d,\\s\\d{4}'\n",
    "date_form_two = r'\\d{4}.[01]\\d.[123]\\d'\n",
    "date_form_three = r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\\s\\d{4}'\n",
    "date_form_four = r'\\d{4}'"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 103,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Review movies based on release date info\n",
    "#release_date.str.extract(f'({date_form_one}|{date_form_two}|{date_form_three}|{date_form_four})', flags=re.IGNORECASE)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 104,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Rerun dataframe\n",
    "wiki_movies_df['release_date'] = pd.to_datetime(release_date.str.extract(f'({date_form_one}|{date_form_two}|{date_form_three}|{date_form_four})')[0], infer_datetime_format=True)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 105,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Review running time variables\n",
    "running_time = wiki_movies_df['Running time'].dropna().apply(lambda x: ' '.join(x) if type(x) == list else x)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 108,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "9                                                 102 min\n",
       "26                                                 93 min\n",
       "28                                                32 min.\n",
       "34                                                101 min\n",
       "35                                                 97 min\n",
       "                              ...                        \n",
       "6500       114 minutes [1] 120 minutes (extended edition)\n",
       "6643                                             104 mins\n",
       "6709    90 minutes (theatrical) [1] 91 minutes (unrate...\n",
       "7057    108 minutes (Original cut) 98 minutes (UK cut)...\n",
       "7075                Variable; 90 minutes for default path\n",
       "Name: Running time, Length: 366, dtype: object"
      ]
     },
     "execution_count": 108,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "# Look at running time string\n",
    "running_time[running_time.str.contains(r'^\\d*\\s*minutes$', flags=re.IGNORECASE) != True]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 113,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Create new variable to extract the info\n",
    "running_time_extract = running_time.str.extract(r'(\\d+)\\s*ho?u?r?s?\\s*(\\d*)|(\\d+)\\s*m')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 114,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Convert strings to numeric values\n",
    "running_time_extract = running_time_extract.apply(lambda col: pd.to_numeric(col, errors='coerce')).fillna(0)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 115,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Look at time in minutes\n",
    "wiki_movies_df['running_time'] = running_time_extract.apply(lambda row: row[0]*60 + row[1] if row[2] == 0 else row[2], axis=1)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 116,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Remove time info from movies\n",
    "wiki_movies_df.drop('Running time', axis=1, inplace=True)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 120,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<div>\n",
       "<style scoped>\n",
       "    .dataframe tbody tr th:only-of-type {\n",
       "        vertical-align: middle;\n",
       "    }\n",
       "\n",
       "    .dataframe tbody tr th {\n",
       "        vertical-align: top;\n",
       "    }\n",
       "\n",
       "    .dataframe thead th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr style=\"text-align: right;\">\n",
       "      <th></th>\n",
       "      <th>adult</th>\n",
       "      <th>belongs_to_collection</th>\n",
       "      <th>budget</th>\n",
       "      <th>genres</th>\n",
       "      <th>homepage</th>\n",
       "      <th>id</th>\n",
       "      <th>imdb_id</th>\n",
       "      <th>original_language</th>\n",
       "      <th>original_title</th>\n",
       "      <th>overview</th>\n",
       "      <th>...</th>\n",
       "      <th>release_date</th>\n",
       "      <th>revenue</th>\n",
       "      <th>runtime</th>\n",
       "      <th>spoken_languages</th>\n",
       "      <th>status</th>\n",
       "      <th>tagline</th>\n",
       "      <th>title</th>\n",
       "      <th>video</th>\n",
       "      <th>vote_average</th>\n",
       "      <th>vote_count</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>19730</th>\n",
       "      <td>- Written by Ørnås</td>\n",
       "      <td>0.065736</td>\n",
       "      <td>/ff9qCepilowshEtG2GYWwzt2bs4.jpg</td>\n",
       "      <td>[{'name': 'Carousel Productions', 'id': 11176}...</td>\n",
       "      <td>[{'iso_3166_1': 'CA', 'name': 'Canada'}, {'iso...</td>\n",
       "      <td>1997-08-20</td>\n",
       "      <td>0</td>\n",
       "      <td>104.0</td>\n",
       "      <td>[{'iso_639_1': 'en', 'name': 'English'}]</td>\n",
       "      <td>Released</td>\n",
       "      <td>...</td>\n",
       "      <td>1</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>29503</th>\n",
       "      <td>Rune Balot goes to a casino connected to the ...</td>\n",
       "      <td>1.931659</td>\n",
       "      <td>/zV8bHuSL6WXoD6FWogP9j4x80bL.jpg</td>\n",
       "      <td>[{'name': 'Aniplex', 'id': 2883}, {'name': 'Go...</td>\n",
       "      <td>[{'iso_3166_1': 'US', 'name': 'United States o...</td>\n",
       "      <td>2012-09-29</td>\n",
       "      <td>0</td>\n",
       "      <td>68.0</td>\n",
       "      <td>[{'iso_639_1': 'ja', 'name': '日本語'}]</td>\n",
       "      <td>Released</td>\n",
       "      <td>...</td>\n",
       "      <td>12</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>35587</th>\n",
       "      <td>Avalanche Sharks tells the story of a bikini ...</td>\n",
       "      <td>2.185485</td>\n",
       "      <td>/zaSf5OG7V8X8gqFvly88zDdRm46.jpg</td>\n",
       "      <td>[{'name': 'Odyssey Media', 'id': 17161}, {'nam...</td>\n",
       "      <td>[{'iso_3166_1': 'CA', 'name': 'Canada'}]</td>\n",
       "      <td>2014-01-01</td>\n",
       "      <td>0</td>\n",
       "      <td>82.0</td>\n",
       "      <td>[{'iso_639_1': 'en', 'name': 'English'}]</td>\n",
       "      <td>Released</td>\n",
       "      <td>...</td>\n",
       "      <td>22</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "      <td>NaN</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "<p>3 rows × 24 columns</p>\n",
       "</div>"
      ],
      "text/plain": [
       "                                                   adult  \\\n",
       "19730                                 - Written by Ørnås   \n",
       "29503   Rune Balot goes to a casino connected to the ...   \n",
       "35587   Avalanche Sharks tells the story of a bikini ...   \n",
       "\n",
       "      belongs_to_collection                            budget  \\\n",
       "19730              0.065736  /ff9qCepilowshEtG2GYWwzt2bs4.jpg   \n",
       "29503              1.931659  /zV8bHuSL6WXoD6FWogP9j4x80bL.jpg   \n",
       "35587              2.185485  /zaSf5OG7V8X8gqFvly88zDdRm46.jpg   \n",
       "\n",
       "                                                  genres  \\\n",
       "19730  [{'name': 'Carousel Productions', 'id': 11176}...   \n",
       "29503  [{'name': 'Aniplex', 'id': 2883}, {'name': 'Go...   \n",
       "35587  [{'name': 'Odyssey Media', 'id': 17161}, {'nam...   \n",
       "\n",
       "                                                homepage          id imdb_id  \\\n",
       "19730  [{'iso_3166_1': 'CA', 'name': 'Canada'}, {'iso...  1997-08-20       0   \n",
       "29503  [{'iso_3166_1': 'US', 'name': 'United States o...  2012-09-29       0   \n",
       "35587           [{'iso_3166_1': 'CA', 'name': 'Canada'}]  2014-01-01       0   \n",
       "\n",
       "      original_language                            original_title  overview  \\\n",
       "19730             104.0  [{'iso_639_1': 'en', 'name': 'English'}]  Released   \n",
       "29503              68.0      [{'iso_639_1': 'ja', 'name': '日本語'}]  Released   \n",
       "35587              82.0  [{'iso_639_1': 'en', 'name': 'English'}]  Released   \n",
       "\n",
       "       ... release_date revenue runtime spoken_languages status  tagline  \\\n",
       "19730  ...            1     NaN     NaN              NaN    NaN      NaN   \n",
       "29503  ...           12     NaN     NaN              NaN    NaN      NaN   \n",
       "35587  ...           22     NaN     NaN              NaN    NaN      NaN   \n",
       "\n",
       "       title video vote_average vote_count  \n",
       "19730    NaN   NaN          NaN        NaN  \n",
       "29503    NaN   NaN          NaN        NaN  \n",
       "35587    NaN   NaN          NaN        NaN  \n",
       "\n",
       "[3 rows x 24 columns]"
      ]
     },
     "execution_count": 120,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "# Remove bad data in adult types\n",
    "kaggle_metadata[~kaggle_metadata['adult'].isin(['True','False'])]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 121,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Here's the fix, drop them\n",
    "kaggle_metadata = kaggle_metadata[kaggle_metadata['adult'] == 'False'].drop('adult',axis='columns')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 122,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "False    45358\n",
       "True        93\n",
       "Name: video, dtype: int64"
      ]
     },
     "execution_count": 122,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "# Now we'll look at the video column\n",
    "kaggle_metadata['video'].value_counts()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 123,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "0        False\n",
       "1        False\n",
       "2        False\n",
       "3        False\n",
       "4        False\n",
       "         ...  \n",
       "45461    False\n",
       "45462    False\n",
       "45463    False\n",
       "45464    False\n",
       "45465    False\n",
       "Name: video, Length: 45454, dtype: bool"
      ]
     },
     "execution_count": 123,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "# Converting the code for the video column\n",
    "kaggle_metadata['video'] == 'True'"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 124,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Boolean column has been created\n",
    "kaggle_metadata['video'] = kaggle_metadata['video'] == 'True'"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 125,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Code for converting the budget, id and popularity columns\n",
    "kaggle_metadata['budget'] = kaggle_metadata['budget'].astype(int)\n",
    "kaggle_metadata['id'] = pd.to_numeric(kaggle_metadata['id'], errors='raise')\n",
    "kaggle_metadata['popularity'] = pd.to_numeric(kaggle_metadata['popularity'], errors='raise')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 126,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Release date is the final\n",
    "kaggle_metadata['release_date'] = pd.to_datetime(kaggle_metadata['release_date'])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 129,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Now that the formatting is correct, it can be assigned to the timestamp column\n",
    "ratings['timestamp'] = pd.to_datetime(ratings['timestamp'], unit='s')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 130,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "count    2.602429e+07\n",
       "mean     3.528090e+00\n",
       "std      1.065443e+00\n",
       "min      5.000000e-01\n",
       "25%      3.000000e+00\n",
       "50%      3.500000e+00\n",
       "75%      4.000000e+00\n",
       "max      5.000000e+00\n",
       "Name: rating, dtype: float64"
      ]
     },
     "execution_count": 130,
     "metadata": {},
     "output_type": "execute_result"
    },
    {
     "data": {
      "image/png": "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\n",
      "text/plain": [
       "<Figure size 432x288 with 1 Axes>"
      ]
     },
     "metadata": {
      "needs_background": "light"
     },
     "output_type": "display_data"
    }
   ],
   "source": [
    "# Create a histogram\n",
    "ratings['rating'].plot(kind='hist')\n",
    "ratings['rating'].describe()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 132,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Lesson 8.4.1, merge Kaggle and Wikipedia data\n",
    "movies_df = pd.merge(wiki_movies_df, kaggle_metadata, on='imdb_id', suffixes=['_wiki','_kaggle'])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 133,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Competing data:\n",
    "# Wiki                     Movielens                Resolution\n",
    "#--------------------------------------------------------------------------\n",
    "# title_wiki               title_kaggle\n",
    "# running_time             runtime\n",
    "# budget_wiki              budget_kaggle\n",
    "# box_office               revenue\n",
    "# release_date_wiki        release_date_kaggle\n",
    "# Language                 original_language\n",
    "# Production company(s)    production_companies "
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 141,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "<matplotlib.axes._subplots.AxesSubplot at 0x1b810d33e08>"
      ]
     },
     "execution_count": 141,
     "metadata": {},
     "output_type": "execute_result"
    },
    {
     "data": {
      "image/png": "iVBORw0KGgoAAAANSUhEUgAAAX0AAAD9CAYAAABQvqc9AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAALEgAACxIB0t1+/AAAADh0RVh0U29mdHdhcmUAbWF0cGxvdGxpYiB2ZXJzaW9uMy4xLjMsIGh0dHA6Ly9tYXRwbG90bGliLm9yZy+AADFEAAAgAElEQVR4nO3deXyU1dn/8c83CyKLgIAbAQJVqSxRIGCsVqEVwVoVat2gLg8qrcujtq4/61at/VFrrUstFgWXlkL9ua9V7IPyqMSSoCKKCyJoCspiXNgKIdfvj/skDnGSTCbLTDLX+/Wa19xz7mWumUyuOXPuc58jM8M551xmyEp1AM4551qOJ33nnMsgnvSdcy6DeNJ3zrkM4knfOecyiCd955zLIDn1bSCpN3A/sAdQCUw3s1sl7Qr8HcgHVgAnmFm5pEnAZWH3DcDZZvZGONY44FYgG7jbzKbW9/w9evSw/Pz8Br4s55zLXKWlpevMrGe8daqvn76kPYE9zWyRpM5AKTAeOB34zMymSroc6GZml0n6DrA0fAEcCVxrZgdKygbeA8YAZcBC4GQze7uu5y8sLLSSkpIGvWDnnMtkkkrNrDDeunqbd8xstZktCstfAUuBXsCxwH1hs/uIvggws1fMrDyUFwN5YXkksMzMlpvZVmBOOIZzzrkW0qA2fUn5wFDgVWB3M1sN0RcDsFucXc4AngnLvYCPY9aVhTLnnHMtpN42/SqSOgEPARea2ZeS6tt+NFHSP6SqKM5mcduWJE0BpgD06dMn0RCdc87VI6GkLymXKOHPMrOHQ/GnkvY0s9Wh3X9NzPYFwN3AkWa2PhSXAb1jDpsHrIr3fGY2HZgOUZt+zfXbtm2jrKyMLVu2JBK+y0Dt27cnLy+P3NzcVIfiXFpJpPeOgBlEJ2dvjln1OHAaMDXcPxa27wM8DJxiZu/FbL8Q2EdSP+DfwEnAxGSCLisro3PnzuTn51PfLw6XecyM9evXU1ZWRr9+/VIdjnNpJZGa/sHAKcCbkl4PZVcQJfsHJJ0BfAQcH9ZdDXQH/hQScoWZFZpZhaTzgGeJumzONLO3kgl6y5YtnvBdrSTRvXt31q5dm+pQnEtI6cpyipevp1uHdixZ9QUvv7+O9Rv/w+H77c4tJw1t0ueqN+mb2UvEb48H+H6c7c8EzqzlWE8DTzckwNp4wnd18c+HS2enzniV4uXr2avrzhzQuyuPvh63pbu6vCkTf8Incp1zziWnqiZf1L871z/xFq+XfQHAivWbWLF+U537Pr/00yaNxYdhaEajRo0iXS4sSySWW265hU2b6v4A1iY/P59169YltW8iVqxYweDBg5vt+M41l9KV5Uy6u5jfP/cuJ09fUJ3wE9W7W4cmjSdjkn7pynLumLeM0pXl9W/cAGZGZWVlkx4zVRqT9J1z8RUvX8+WbZVUGmzd3vCZCn89YUiTxpMRST/2m3bS3cWNTvwrVqxgv/3245xzzmHYsGH85S9/4aCDDmLYsGEcf/zxbNiw4Rv7PPfcc3G3ue666xgxYgSDBw9mypQpVA2LcdtttzFw4EAKCgo46aSTANi4cSOTJ09mxIgRDB06lMcee6zWGDdv3sxJJ51EQUEBJ554Ips3b65ed/bZZ1NYWMigQYO45pprqp9v1apVjB49mtGjR9cZc102b97MuHHjuOuuuwAYP348w4cPZ9CgQUyfPr16uxkzZrDvvvsyatQozjrrLM477zwAPvjgA4qKihgxYgRXX301nTp1+sZzbN++nUsuuYQRI0ZQUFDAn//853rjci5Vvtq8Lan9unfM5aGzv8Pwvt2aNJ6MSPrFy9eztSL6pt1WUUnx8vX171SPd999l1NPPZW5c+cyY8YMnn/+eRYtWkRhYSE333zzDtuuW7eOX//613G3Oe+881i4cCFLlixh8+bNPPnkkwBMnTqV1157jcWLF3PnnXcCcMMNN/C9732PhQsXMm/ePC655BI2btwYN75p06bRoUMHFi9ezC9/+UtKS0ur191www2UlJSwePFiXnzxRRYvXsz555/PXnvtxbx585g3b16dMddmw4YNHH300UycOJGzzjoLgJkzZ1JaWkpJSQm33XYb69evZ9WqVVx//fUUFxczd+5c3nnnnepjXHDBBVxwwQUsXLiQvfbaK+7zzJgxgy5durBw4UIWLlzIXXfdxYcfflhnbM61lL+9+hGnzHiVC+e8xrF/fIk75y9v8DFWTD2K0quOaPKEDxlyIreof3fa5WSxraKS3Jwsivp3b/Qx+/btS1FREU8++SRvv/02Bx98MABbt27loIMO2mHb4uLiWreZN28eN954I5s2beKzzz5j0KBBHH300RQUFDBp0iTGjx/P+PHjgajm/fjjj3PT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\n",
      "text/plain": [
       "<Figure size 432x288 with 1 Axes>"
      ]
     },
     "metadata": {
      "needs_background": "light"
     },
     "output_type": "display_data"
    }
   ],
   "source": [
    "# Release date scatter plot\n",
    "movies_df[['release_date_wiki','release_date_kaggle']].plot(x='release_date_wiki', y='release_date_kaggle', style='.')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 142,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<div>\n",
       "<style scoped>\n",
       "    .dataframe tbody tr th:only-of-type {\n",
       "        vertical-align: middle;\n",
       "    }\n",
       "\n",
       "    .dataframe tbody tr th {\n",
       "        vertical-align: top;\n",
       "    }\n",
       "\n",
       "    .dataframe thead th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr style=\"text-align: right;\">\n",
       "      <th></th>\n",
       "      <th>url</th>\n",
       "      <th>year</th>\n",
       "      <th>imdb_link</th>\n",
       "      <th>title_wiki</th>\n",
       "      <th>Based on</th>\n",
       "      <th>Starring</th>\n",
       "      <th>Cinematography</th>\n",
       "      <th>Release date</th>\n",
       "      <th>Country</th>\n",
       "      <th>Language</th>\n",
       "      <th>...</th>\n",
       "      <th>release_date_kaggle</th>\n",
       "      <th>revenue</th>\n",
       "      <th>runtime</th>\n",
       "      <th>spoken_languages</th>\n",
       "      <th>status</th>\n",
       "      <th>tagline</th>\n",
       "      <th>title_kaggle</th>\n",
       "      <th>video</th>\n",
       "      <th>vote_average</th>\n",
       "      <th>vote_count</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>3607</th>\n",
       "      <td>https://en.wikipedia.org/wiki/The_Holiday</td>\n",
       "      <td>2006</td>\n",
       "      <td>https://www.imdb.com/title/tt00457939/</td>\n",
       "      <td>The Holiday</td>\n",
       "      <td>NaN</td>\n",
       "      <td>[Kate Winslet, Cameron Diaz, Jude Law, Jack Bl...</td>\n",
       "      <td>Dean Cundey</td>\n",
       "      <td>[December 8, 2006, (, 2006-12-08, )]</td>\n",
       "      <td>United States</td>\n",
       "      <td>English</td>\n",
       "      <td>...</td>\n",
       "      <td>1953-08-28</td>\n",
       "      <td>30500000.0</td>\n",
       "      <td>118.0</td>\n",
       "      <td>[{'iso_639_1': 'en', 'name': 'English'}]</td>\n",
       "      <td>Released</td>\n",
       "      <td>Pouring out of impassioned pages...brawling th...</td>\n",
       "      <td>From Here to Eternity</td>\n",
       "      <td>False</td>\n",
       "      <td>7.2</td>\n",
       "      <td>137.0</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "<p>1 rows × 44 columns</p>\n",
       "</div>"
      ],
      "text/plain": [
       "                                            url  year  \\\n",
       "3607  https://en.wikipedia.org/wiki/The_Holiday  2006   \n",
       "\n",
       "                                   imdb_link   title_wiki Based on  \\\n",
       "3607  https://www.imdb.com/title/tt00457939/  The Holiday      NaN   \n",
       "\n",
       "                                               Starring Cinematography  \\\n",
       "3607  [Kate Winslet, Cameron Diaz, Jude Law, Jack Bl...    Dean Cundey   \n",
       "\n",
       "                              Release date        Country Language  ...  \\\n",
       "3607  [December 8, 2006, (, 2006-12-08, )]  United States  English  ...   \n",
       "\n",
       "     release_date_kaggle     revenue runtime  \\\n",
       "3607          1953-08-28  30500000.0   118.0   \n",
       "\n",
       "                              spoken_languages    status  \\\n",
       "3607  [{'iso_639_1': 'en', 'name': 'English'}]  Released   \n",
       "\n",
       "                                                tagline  \\\n",
       "3607  Pouring out of impassioned pages...brawling th...   \n",
       "\n",
       "               title_kaggle  video  vote_average  vote_count  \n",
       "3607  From Here to Eternity  False           7.2       137.0  \n",
       "\n",
       "[1 rows x 44 columns]"
      ]
     },
     "execution_count": 142,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "# Modify date range\n",
    "movies_df[(movies_df['release_date_wiki'] > '1996-01-01') & (movies_df['release_date_kaggle'] < '1965-01-01')]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 143,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "Int64Index([3607], dtype='int64')"
      ]
     },
     "execution_count": 143,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "# Fix dropped info\n",
    "movies_df[(movies_df['release_date_wiki'] > '1996-01-01') & (movies_df['release_date_kaggle'] < '1965-01-01')].index"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 144,
   "metadata": {},
   "outputs": [],
   "source": [
    "# New code to drop duplicate info\n",
    "movies_df = movies_df.drop(movies_df[(movies_df['release_date_wiki'] > '1996-01-01') & (movies_df['release_date_kaggle'] < '1965-01-01')].index)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 149,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Remove column names we do no need\n",
    "movies_df.drop(columns=['title_wiki','release_date_wiki','Language','Production company(s)'], inplace=True)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 150,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Fill in data for missing pairs\n",
    "def fill_missing_kaggle_data(df, kaggle_column, wiki_column):\n",
    "    df[kaggle_column] = df.apply(\n",
    "        lambda row: row[wiki_column] if row[kaggle_column] == 0 else row[kaggle_column]\n",
    "        , axis=1)\n",
    "    df.drop(columns=wiki_column, inplace=True)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 151,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<div>\n",
       "<style scoped>\n",
       "    .dataframe tbody tr th:only-of-type {\n",
       "        vertical-align: middle;\n",
       "    }\n",
       "\n",
       "    .dataframe tbody tr th {\n",
       "        vertical-align: top;\n",
       "    }\n",
       "\n",
       "    .dataframe thead th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr style=\"text-align: right;\">\n",
       "      <th></th>\n",
       "      <th>url</th>\n",
       "      <th>year</th>\n",
       "      <th>imdb_link</th>\n",
       "      <th>Based on</th>\n",
       "      <th>Starring</th>\n",
       "      <th>Cinematography</th>\n",
       "      <th>Release date</th>\n",
       "      <th>Country</th>\n",
       "      <th>Director</th>\n",
       "      <th>Distributor</th>\n",
       "      <th>...</th>\n",
       "      <th>release_date_kaggle</th>\n",
       "      <th>revenue</th>\n",
       "      <th>runtime</th>\n",
       "      <th>spoken_languages</th>\n",
       "      <th>status</th>\n",
       "      <th>tagline</th>\n",
       "      <th>title_kaggle</th>\n",
       "      <th>video</th>\n",
       "      <th>vote_average</th>\n",
       "      <th>vote_count</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>0</th>\n",
       "      <td>https://en.wikipedia.org/wiki/The_Adventures_o...</td>\n",
       "      <td>1990</td>\n",
       "      <td>https://www.imdb.com/title/tt0098987/</td>\n",
       "      <td>[Characters, by Rex Weiner]</td>\n",
       "      <td>[Andrew Dice Clay, Wayne Newton, Priscilla Pre...</td>\n",
       "      <td>Oliver Wood</td>\n",
       "      <td>[July 11, 1990, (, 1990-07-11, )]</td>\n",
       "      <td>United States</td>\n",
       "      <td>Renny Harlin</td>\n",
       "      <td>20th Century Fox</td>\n",
       "      <td>...</td>\n",
       "      <td>1990-07-11</td>\n",
       "      <td>20423389.0</td>\n",
       "      <td>104.0</td>\n",
       "      <td>[{'iso_639_1': 'en', 'name': 'English'}]</td>\n",
       "      <td>Released</td>\n",
       "      <td>Kojak. Columbo. Dirty Harry. Wimps.</td>\n",
       "      <td>The Adventures of Ford Fairlane</td>\n",
       "      <td>False</td>\n",
       "      <td>6.2</td>\n",
       "      <td>72.0</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>1</th>\n",
       "      <td>https://en.wikipedia.org/wiki/After_Dark,_My_S...</td>\n",
       "      <td>1990</td>\n",
       "      <td>https://www.imdb.com/title/tt0098994/</td>\n",
       "      <td>[the novel, After Dark, My Sweet, by, Jim Thom...</td>\n",
       "      <td>[Jason Patric, Rachel Ward, Bruce Dern, George...</td>\n",
       "      <td>Mark Plummer</td>\n",
       "      <td>[May 17, 1990, (, 1990-05-17, ), (Cannes Film ...</td>\n",
       "      <td>United States</td>\n",
       "      <td>James Foley</td>\n",
       "      <td>Avenue Pictures</td>\n",
       "      <td>...</td>\n",
       "      <td>1990-08-24</td>\n",
       "      <td>2700000.0</td>\n",
       "      <td>114.0</td>\n",
       "      <td>[{'iso_639_1': 'en', 'name': 'English'}]</td>\n",
       "      <td>Released</td>\n",
       "      <td>All they risked was everything.</td>\n",
       "      <td>After Dark, My Sweet</td>\n",
       "      <td>False</td>\n",
       "      <td>6.5</td>\n",
       "      <td>17.0</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2</th>\n",
       "      <td>https://en.wikipedia.org/wiki/Air_America_(film)</td>\n",
       "      <td>1990</td>\n",
       "      <td>https://www.imdb.com/title/tt0099005/</td>\n",
       "      <td>[Air America, by, Christopher Robbins]</td>\n",
       "      <td>[Mel Gibson, Robert Downey Jr., Nancy Travis, ...</td>\n",
       "      <td>Roger Deakins</td>\n",
       "      <td>[August 10, 1990, (, 1990-08-10, )]</td>\n",
       "      <td>United States</td>\n",
       "      <td>Roger Spottiswoode</td>\n",
       "      <td>TriStar Pictures</td>\n",
       "      <td>...</td>\n",
       "      <td>1990-08-10</td>\n",
       "      <td>33461269.0</td>\n",
       "      <td>112.0</td>\n",
       "      <td>[{'iso_639_1': 'en', 'name': 'English'}, {'iso...</td>\n",
       "      <td>Released</td>\n",
       "      <td>The few. The proud. The totally insane.</td>\n",
       "      <td>Air America</td>\n",
       "      <td>False</td>\n",
       "      <td>5.3</td>\n",
       "      <td>146.0</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>3</th>\n",
       "      <td>https://en.wikipedia.org/wiki/Alice_(1990_film)</td>\n",
       "      <td>1990</td>\n",
       "      <td>https://www.imdb.com/title/tt0099012/</td>\n",
       "      <td>NaN</td>\n",
       "      <td>[Alec Baldwin, Blythe Danner, Judy Davis, Mia ...</td>\n",
       "      <td>Carlo Di Palma</td>\n",
       "      <td>[December 25, 1990, (, 1990-12-25, )]</td>\n",
       "      <td>United States</td>\n",
       "      <td>Woody Allen</td>\n",
       "      <td>Orion Pictures</td>\n",
       "      <td>...</td>\n",
       "      <td>1990-12-25</td>\n",
       "      <td>7331647.0</td>\n",
       "      <td>102.0</td>\n",
       "      <td>[{'iso_639_1': 'en', 'name': 'English'}]</td>\n",
       "      <td>Released</td>\n",
       "      <td>NaN</td>\n",
       "      <td>Alice</td>\n",
       "      <td>False</td>\n",
       "      <td>6.3</td>\n",
       "      <td>57.0</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>4</th>\n",
       "      <td>https://en.wikipedia.org/wiki/Almost_an_Angel</td>\n",
       "      <td>1990</td>\n",
       "      <td>https://www.imdb.com/title/tt0099018/</td>\n",
       "      <td>NaN</td>\n",
       "      <td>[Paul Hogan, Elias Koteas, Linda Kozlowski]</td>\n",
       "      <td>Russell Boyd</td>\n",
       "      <td>December 19, 1990</td>\n",
       "      <td>US</td>\n",
       "      <td>John Cornell</td>\n",
       "      <td>Paramount Pictures</td>\n",
       "      <td>...</td>\n",
       "      <td>1990-12-21</td>\n",
       "      <td>6939946.0</td>\n",
       "      <td>95.0</td>\n",
       "      <td>[{'iso_639_1': 'en', 'name': 'English'}]</td>\n",
       "      <td>Released</td>\n",
       "      <td>Who does he think he is?</td>\n",
       "      <td>Almost an Angel</td>\n",
       "      <td>False</td>\n",
       "      <td>5.6</td>\n",
       "      <td>23.0</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>...</th>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>6047</th>\n",
       "      <td>https://en.wikipedia.org/wiki/A_Fantastic_Woman</td>\n",
       "      <td>2018</td>\n",
       "      <td>https://www.imdb.com/title/tt5639354/</td>\n",
       "      <td>NaN</td>\n",
       "      <td>[Daniela Vega, Francisco Reyes]</td>\n",
       "      <td>Benjamín Echazarreta</td>\n",
       "      <td>[12 February 2017, (, 2017-02-12, ), (, Berlin...</td>\n",
       "      <td>[Chile, Germany, Spain, United States, [2]]</td>\n",
       "      <td>Sebastián Lelio</td>\n",
       "      <td>[Participant Media (Chile), Piffl Medien (Germ...</td>\n",
       "      <td>...</td>\n",
       "      <td>2017-04-06</td>\n",
       "      <td>3700000.0</td>\n",
       "      <td>104.0</td>\n",
       "      <td>[{'iso_639_1': 'es', 'name': 'Español'}]</td>\n",
       "      <td>Released</td>\n",
       "      <td>NaN</td>\n",
       "      <td>A Fantastic Woman</td>\n",
       "      <td>False</td>\n",
       "      <td>7.2</td>\n",
       "      <td>13.0</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>6048</th>\n",
       "      <td>https://en.wikipedia.org/wiki/Permission_(film)</td>\n",
       "      <td>2018</td>\n",
       "      <td>https://www.imdb.com/title/tt5390066/</td>\n",
       "      <td>NaN</td>\n",
       "      <td>[Rebecca Hall, Dan Stevens, Morgan Spector, Fr...</td>\n",
       "      <td>Adam Bricker</td>\n",
       "      <td>[April 22, 2017, (, 2017-04-22, ), (, Tribeca ...</td>\n",
       "      <td>United States</td>\n",
       "      <td>Brian Crano</td>\n",
       "      <td>Good Deed Entertainment</td>\n",
       "      <td>...</td>\n",
       "      <td>2017-04-22</td>\n",
       "      <td>NaN</td>\n",
       "      <td>96.0</td>\n",
       "      <td>[{'iso_639_1': 'en', 'name': 'English'}]</td>\n",
       "      <td>Released</td>\n",
       "      <td>NaN</td>\n",
       "      <td>Permission</td>\n",
       "      <td>False</td>\n",
       "      <td>0.0</td>\n",
       "      <td>1.0</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>6049</th>\n",
       "      <td>https://en.wikipedia.org/wiki/Loveless_(film)</td>\n",
       "      <td>2018</td>\n",
       "      <td>https://www.imdb.com/title/tt6304162/</td>\n",
       "      <td>NaN</td>\n",
       "      <td>[Maryana Spivak, Aleksey Rozin, Matvey Novikov...</td>\n",
       "      <td>Mikhail Krichman</td>\n",
       "      <td>[18 May 2017, (, 2017-05-18, ), (, Cannes, ), ...</td>\n",
       "      <td>[Russia, France, Belgium, Germany, [3]]</td>\n",
       "      <td>Andrey Zvyagintsev</td>\n",
       "      <td>[Sony Pictures Releasing, (Russia), [1]]</td>\n",
       "      <td>...</td>\n",
       "      <td>2017-06-01</td>\n",
       "      <td>4800000.0</td>\n",
       "      <td>128.0</td>\n",
       "      <td>[{'iso_639_1': 'ru', 'name': 'Pусский'}]</td>\n",
       "      <td>Released</td>\n",
       "      <td>NaN</td>\n",
       "      <td>Loveless</td>\n",
       "      <td>False</td>\n",
       "      <td>7.8</td>\n",
       "      <td>26.0</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>6050</th>\n",
       "      <td>https://en.wikipedia.org/wiki/Gemini_(2017_film)</td>\n",
       "      <td>2018</td>\n",
       "      <td>https://www.imdb.com/title/tt5795086/</td>\n",
       "      <td>NaN</td>\n",
       "      <td>[Lola Kirke, Zoë Kravitz, Greta Lee, Michelle ...</td>\n",
       "      <td>Andrew Reed</td>\n",
       "      <td>[March 12, 2017, (, 2017-03-12, ), (, SXSW, ),...</td>\n",
       "      <td>United States</td>\n",
       "      <td>Aaron Katz</td>\n",
       "      <td>Neon</td>\n",
       "      <td>...</td>\n",
       "      <td>2017-03-12</td>\n",
       "      <td>200340.0</td>\n",
       "      <td>92.0</td>\n",
       "      <td>[{'iso_639_1': 'en', 'name': 'English'}]</td>\n",
       "      <td>Post Production</td>\n",
       "      <td>NaN</td>\n",
       "      <td>Gemini</td>\n",
       "      <td>False</td>\n",
       "      <td>0.0</td>\n",
       "      <td>0.0</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>6051</th>\n",
       "      <td>https://en.wikipedia.org/wiki/How_to_Talk_to_G...</td>\n",
       "      <td>2018</td>\n",
       "      <td>https://www.imdb.com/title/tt3859310/</td>\n",
       "      <td>[\", How to Talk to Girls at Parties, \", by, Ne...</td>\n",
       "      <td>[Elle Fanning, Alex Sharp, Nicole Kidman, Ruth...</td>\n",
       "      <td>Frank G. DeMarco</td>\n",
       "      <td>[May 21, 2017, (, 2017-05-21, ), (, Cannes, ),...</td>\n",
       "      <td>[United Kingdom, United States]</td>\n",
       "      <td>John Cameron Mitchell</td>\n",
       "      <td>[A24, StudioCanal UK]</td>\n",
       "      <td>...</td>\n",
       "      <td>2017-12-27</td>\n",
       "      <td>382053.0</td>\n",
       "      <td>102.0</td>\n",
       "      <td>[{'iso_639_1': 'en', 'name': 'English'}]</td>\n",
       "      <td>Released</td>\n",
       "      <td>Some girls are out of this world.</td>\n",
       "      <td>How to Talk to Girls at Parties</td>\n",
       "      <td>False</td>\n",
       "      <td>0.0</td>\n",
       "      <td>10.0</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "<p>6051 rows × 37 columns</p>\n",
       "</div>"
      ],
      "text/plain": [
       "                                                    url  year  \\\n",
       "0     https://en.wikipedia.org/wiki/The_Adventures_o...  1990   \n",
       "1     https://en.wikipedia.org/wiki/After_Dark,_My_S...  1990   \n",
       "2      https://en.wikipedia.org/wiki/Air_America_(film)  1990   \n",
       "3       https://en.wikipedia.org/wiki/Alice_(1990_film)  1990   \n",
       "4         https://en.wikipedia.org/wiki/Almost_an_Angel  1990   \n",
       "...                                                 ...   ...   \n",
       "6047    https://en.wikipedia.org/wiki/A_Fantastic_Woman  2018   \n",
       "6048    https://en.wikipedia.org/wiki/Permission_(film)  2018   \n",
       "6049      https://en.wikipedia.org/wiki/Loveless_(film)  2018   \n",
       "6050   https://en.wikipedia.org/wiki/Gemini_(2017_film)  2018   \n",
       "6051  https://en.wikipedia.org/wiki/How_to_Talk_to_G...  2018   \n",
       "\n",
       "                                  imdb_link  \\\n",
       "0     https://www.imdb.com/title/tt0098987/   \n",
       "1     https://www.imdb.com/title/tt0098994/   \n",
       "2     https://www.imdb.com/title/tt0099005/   \n",
       "3     https://www.imdb.com/title/tt0099012/   \n",
       "4     https://www.imdb.com/title/tt0099018/   \n",
       "...                                     ...   \n",
       "6047  https://www.imdb.com/title/tt5639354/   \n",
       "6048  https://www.imdb.com/title/tt5390066/   \n",
       "6049  https://www.imdb.com/title/tt6304162/   \n",
       "6050  https://www.imdb.com/title/tt5795086/   \n",
       "6051  https://www.imdb.com/title/tt3859310/   \n",
       "\n",
       "                                               Based on  \\\n",
       "0                           [Characters, by Rex Weiner]   \n",
       "1     [the novel, After Dark, My Sweet, by, Jim Thom...   \n",
       "2                [Air America, by, Christopher Robbins]   \n",
       "3                                                   NaN   \n",
       "4                                                   NaN   \n",
       "...                                                 ...   \n",
       "6047                                                NaN   \n",
       "6048                                                NaN   \n",
       "6049                                                NaN   \n",
       "6050                                                NaN   \n",
       "6051  [\", How to Talk to Girls at Parties, \", by, Ne...   \n",
       "\n",
       "                                               Starring        Cinematography  \\\n",
       "0     [Andrew Dice Clay, Wayne Newton, Priscilla Pre...           Oliver Wood   \n",
       "1     [Jason Patric, Rachel Ward, Bruce Dern, George...          Mark Plummer   \n",
       "2     [Mel Gibson, Robert Downey Jr., Nancy Travis, ...         Roger Deakins   \n",
       "3     [Alec Baldwin, Blythe Danner, Judy Davis, Mia ...        Carlo Di Palma   \n",
       "4           [Paul Hogan, Elias Koteas, Linda Kozlowski]          Russell Boyd   \n",
       "...                                                 ...                   ...   \n",
       "6047                    [Daniela Vega, Francisco Reyes]  Benjamín Echazarreta   \n",
       "6048  [Rebecca Hall, Dan Stevens, Morgan Spector, Fr...          Adam Bricker   \n",
       "6049  [Maryana Spivak, Aleksey Rozin, Matvey Novikov...      Mikhail Krichman   \n",
       "6050  [Lola Kirke, Zoë Kravitz, Greta Lee, Michelle ...           Andrew Reed   \n",
       "6051  [Elle Fanning, Alex Sharp, Nicole Kidman, Ruth...      Frank G. DeMarco   \n",
       "\n",
       "                                           Release date  \\\n",
       "0                     [July 11, 1990, (, 1990-07-11, )]   \n",
       "1     [May 17, 1990, (, 1990-05-17, ), (Cannes Film ...   \n",
       "2                   [August 10, 1990, (, 1990-08-10, )]   \n",
       "3                 [December 25, 1990, (, 1990-12-25, )]   \n",
       "4                                     December 19, 1990   \n",
       "...                                                 ...   \n",
       "6047  [12 February 2017, (, 2017-02-12, ), (, Berlin...   \n",
       "6048  [April 22, 2017, (, 2017-04-22, ), (, Tribeca ...   \n",
       "6049  [18 May 2017, (, 2017-05-18, ), (, Cannes, ), ...   \n",
       "6050  [March 12, 2017, (, 2017-03-12, ), (, SXSW, ),...   \n",
       "6051  [May 21, 2017, (, 2017-05-21, ), (, Cannes, ),...   \n",
       "\n",
       "                                          Country               Director  \\\n",
       "0                                   United States           Renny Harlin   \n",
       "1                                   United States            James Foley   \n",
       "2                                   United States     Roger Spottiswoode   \n",
       "3                                   United States            Woody Allen   \n",
       "4                                              US           John Cornell   \n",
       "...                                           ...                    ...   \n",
       "6047  [Chile, Germany, Spain, United States, [2]]        Sebastián Lelio   \n",
       "6048                                United States            Brian Crano   \n",
       "6049      [Russia, France, Belgium, Germany, [3]]     Andrey Zvyagintsev   \n",
       "6050                                United States             Aaron Katz   \n",
       "6051              [United Kingdom, United States]  John Cameron Mitchell   \n",
       "\n",
       "                                            Distributor  ...  \\\n",
       "0                                      20th Century Fox  ...   \n",
       "1                                       Avenue Pictures  ...   \n",
       "2                                      TriStar Pictures  ...   \n",
       "3                                        Orion Pictures  ...   \n",
       "4                                    Paramount Pictures  ...   \n",
       "...                                                 ...  ...   \n",
       "6047  [Participant Media (Chile), Piffl Medien (Germ...  ...   \n",
       "6048                            Good Deed Entertainment  ...   \n",
       "6049           [Sony Pictures Releasing, (Russia), [1]]  ...   \n",
       "6050                                               Neon  ...   \n",
       "6051                              [A24, StudioCanal UK]  ...   \n",
       "\n",
       "     release_date_kaggle     revenue runtime  \\\n",
       "0             1990-07-11  20423389.0   104.0   \n",
       "1             1990-08-24   2700000.0   114.0   \n",
       "2             1990-08-10  33461269.0   112.0   \n",
       "3             1990-12-25   7331647.0   102.0   \n",
       "4             1990-12-21   6939946.0    95.0   \n",
       "...                  ...         ...     ...   \n",
       "6047          2017-04-06   3700000.0   104.0   \n",
       "6048          2017-04-22         NaN    96.0   \n",
       "6049          2017-06-01   4800000.0   128.0   \n",
       "6050          2017-03-12    200340.0    92.0   \n",
       "6051          2017-12-27    382053.0   102.0   \n",
       "\n",
       "                                       spoken_languages           status  \\\n",
       "0              [{'iso_639_1': 'en', 'name': 'English'}]         Released   \n",
       "1              [{'iso_639_1': 'en', 'name': 'English'}]         Released   \n",
       "2     [{'iso_639_1': 'en', 'name': 'English'}, {'iso...         Released   \n",
       "3              [{'iso_639_1': 'en', 'name': 'English'}]         Released   \n",
       "4              [{'iso_639_1': 'en', 'name': 'English'}]         Released   \n",
       "...                                                 ...              ...   \n",
       "6047           [{'iso_639_1': 'es', 'name': 'Español'}]         Released   \n",
       "6048           [{'iso_639_1': 'en', 'name': 'English'}]         Released   \n",
       "6049           [{'iso_639_1': 'ru', 'name': 'Pусский'}]         Released   \n",
       "6050           [{'iso_639_1': 'en', 'name': 'English'}]  Post Production   \n",
       "6051           [{'iso_639_1': 'en', 'name': 'English'}]         Released   \n",
       "\n",
       "                                      tagline  \\\n",
       "0         Kojak. Columbo. Dirty Harry. Wimps.   \n",
       "1             All they risked was everything.   \n",
       "2     The few. The proud. The totally insane.   \n",
       "3                                         NaN   \n",
       "4                    Who does he think he is?   \n",
       "...                                       ...   \n",
       "6047                                      NaN   \n",
       "6048                                      NaN   \n",
       "6049                                      NaN   \n",
       "6050                                      NaN   \n",
       "6051        Some girls are out of this world.   \n",
       "\n",
       "                         title_kaggle  video vote_average  vote_count  \n",
       "0     The Adventures of Ford Fairlane  False          6.2        72.0  \n",
       "1                After Dark, My Sweet  False          6.5        17.0  \n",
       "2                         Air America  False          5.3       146.0  \n",
       "3                               Alice  False          6.3        57.0  \n",
       "4                     Almost an Angel  False          5.6        23.0  \n",
       "...                               ...    ...          ...         ...  \n",
       "6047                A Fantastic Woman  False          7.2        13.0  \n",
       "6048                       Permission  False          0.0         1.0  \n",
       "6049                         Loveless  False          7.8        26.0  \n",
       "6050                           Gemini  False          0.0         0.0  \n",
       "6051  How to Talk to Girls at Parties  False          0.0        10.0  \n",
       "\n",
       "[6051 rows x 37 columns]"
      ]
     },
     "execution_count": 151,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "# Fill in the zeros\n",
    "fill_missing_kaggle_data(movies_df, 'runtime', 'running_time')\n",
    "fill_missing_kaggle_data(movies_df, 'budget_kaggle', 'budget_wiki')\n",
    "fill_missing_kaggle_data(movies_df, 'revenue', 'box_office')\n",
    "movies_df"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 152,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "video\n"
     ]
    }
   ],
   "source": [
    "# Convert lists and value count info\n",
    "\n",
    "for col in movies_df.columns:\n",
    "    lists_to_tuples = lambda x: tuple(x) if type(x) == list else x\n",
    "    value_counts = movies_df[col].apply(lists_to_tuples).value_counts(dropna=False)\n",
    "    num_values = len(value_counts)\n",
    "    if num_values == 1:\n",
    "        print(col)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 154,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Reorder columns\n",
    "movies_df = movies_df.loc[:, ['imdb_id','id','title_kaggle','original_title','tagline','belongs_to_collection','url','imdb_link',\n",
    "                       'runtime','budget_kaggle','revenue','release_date_kaggle','popularity','vote_average','vote_count',\n",
    "                       'genres','original_language','overview','spoken_languages','Country',\n",
    "                       'production_companies','production_countries','Distributor',\n",
    "                       'Producer(s)','Director','Starring','Cinematography','Editor(s)','Writer(s)','Composer(s)','Based on'\n",
    "                      ]]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 155,
   "metadata": {},
   "outputs": [],
   "source": [
    "# More consistency\n",
    "movies_df.rename({'id':'kaggle_id',\n",
    "                  'title_kaggle':'title',\n",
    "                  'url':'wikipedia_url',\n",
    "                  'budget_kaggle':'budget',\n",
    "                  'release_date_kaggle':'release_date',\n",
    "                  'Country':'country',\n",
    "                  'Distributor':'distributor',\n",
    "                  'Producer(s)':'producers',\n",
    "                  'Director':'director',\n",
    "                  'Starring':'starring',\n",
    "                  'Cinematography':'cinematography',\n",
    "                  'Editor(s)':'editors',\n",
    "                  'Writer(s)':'writers',\n",
    "                  'Composer(s)':'composers',\n",
    "                  'Based on':'based_on'\n",
    "                 }, axis='columns', inplace=True)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 160,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Pivot the data to add movieid\n",
    "\n",
    "rating_counts = ratings.groupby(['movieId','rating'], as_index=False).count() \\\n",
    "                .rename({'userId':'count'}, axis=1) \\\n",
    "                .pivot(index='movieId',columns='rating', values='count')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 161,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Rename other columns\n",
    "rating_counts.columns = ['rating_' + str(col) for col in rating_counts.columns]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 162,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Left join to merge info\n",
    "movies_with_ratings_df = pd.merge(movies_df, rating_counts, left_on='kaggle_id', right_index=True, how='left')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 163,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Fill missing values \n",
    "movies_with_ratings_df[rating_counts.columns] = movies_with_ratings_df[rating_counts.columns].fillna(0)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 172,
   "metadata": {},
   "outputs": [],
   "source": [
    "#from config import db_password\n",
    "db_password = 'Your Password'"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 166,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Create a variable for the link\n",
    "db_string = f\"postgres://postgres:{db_password}@127.0.0.1:5432/movie_data\"\n",
    "#db_string = f\"postgresql://username:password@localhost:5432/mydatabase\""
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 167,
   "metadata": {},
   "outputs": [],
   "source": [
    "# String redefined\n",
    "engine = create_engine(db_string)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {},
   "outputs": [],
   "source": [
    "# create a variable for the number of rows imported\n",
    "#rows_imported = 0\n",
    "#start_time = time.time()\n",
    "#for data in pd.read_csv(f'{file_dir}ratings.csv', chunksize=1000000):\n",
    "\n",
    "    # print out the range of rows that are being imported\n",
    " #   print(f'importing rows {rows_imported} to {rows_imported + len(data)}...', end='')\n",
    "\n",
    "#    data.to_sql(name='ratings', con=engine, if_exists='append')\n",
    "\n",
    "    # increment the number of rows imported by the size of 'data'\n",
    " #   rows_imported += len(data)\n",
    "\n",
    "    # print that the rows have finished importing\n",
    "  #  print(f'Done. {time.time() - start_time} total seconds elapsed')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "PythonData",
   "language": "python",
   "name": "pythondata"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.7.6"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}
