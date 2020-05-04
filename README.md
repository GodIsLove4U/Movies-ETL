# Movies-ETL
Module 8 ETL - A hackathon using data from Wikipedia and JSON.

This project required the use of multiple datasets to provide a useful and comprehensive list of movie information. To accomplish this task, three files were provided with the raw data. These files were in the form of JSON and CSV. Information had to be extracted from these files to perform the analysis. The files and description are as follows:
•	wikipedia.movies.json	
JSON file with information on movies dating back to the 1960s. This is a compilation of information from various authors. Over the years a lot of the information was expounded on for some movies and not for others. So, while the content is elaborate, the format is not consistent and changes were made to the structure and format that affect the way the document is display and outlined. 

•	movies_metadata.csv
This is a csv file that was obtained from Kaggle. Kaggle is an open source website that provides datasets and notebooks on various subjects. This data was zipped in a package with the ratings.csv. For the purposes of this analysis, we will now refer to this file as kaggle_metadata.csv.

•	ratings.csv
The ratings file was a part of the Kaggle datasets. It provided copious rows/columns of information of the ratings data for movies. This information will be combined with the two aforementioned files to look at a list of movies and all of the data elements that effectively provide a full description of the movie prior to and following it’s production and onscreen debut. 

Performing this analysis required a combination of processes to include Extracting, Transforming and Loading the data. To do this, Jupyter Notebook was utilized, in concert with local files, GitBash, VSCode, GitHub and Python. The goal is to extract the data so it can be reviewed. Then, review the data, combine the information that is related, remove any ambiguous information, cleanse the data to transform it into something useful for our stakeholder (Britta) who is my colleague at Amazing Prime. In addition, the data is then loaded into a SQL platform for future use and analysis on various topics and subjects. 
There are several assumptions to be made based on the analysis. As I reviewed the data and performed the tasks, I noted the following:
1.	The dataset is massive and has many authors. In addition, it comes from different databases. This data assumes that the authors will continue to use the same types of information to inform and record movie data. If that is true, the columns of data that I’ve include in the final product will be useful. If this is not true, this will no longer become useful to Britta or any other reader. 

2.	The majority of the information is in English. There were a few items that were is 20+ other language. I am assuming that Britta and Amazing Prime want to use this information for our English-speaking consumers. Otherwise, we’ll need to consider building in a tool that will easily, systematically and programmatically read in other languages with proper translation and formatting. 

3.	Without having the ability to review every piece of information, I made some general assumptions about the data that may affect Britta’s ability to gather information in the future. As a follow up exercise, I would spend a little more time discussion the information with Amazing Prime to make sure we are keeping the type of information they want to focus on and not getting rid of anything they want to keep. 


4.	As a follow up to reviewing the information with Britta, I would make sure that I understand what the file is being used for, who the users are and why any significant outliers and/or swings in the data do not have an adverse effect on the goal she is attempting to achieve.

5.	After going thru the columns that I kept, I found that the Kaggle data was a lot more comprehensive than the Wikipedia data. This is understandable, as there are likely a lot more authors on the Wikipedia data. However, there are disadvantages to merging data to including subjective and objective information. Kaggle seemed to have a level of consistency that suggests that the authors have been given the same directives. Whereas Wikipedia data is a lot more unstructured. Due to these factors, I would caution Britta to be mindful of the reliability (or lack thereof) of this data. 

6.	User may not remember to update the file name info so try-except conditions were placed there. This is in the event that there is a typo or the code is run from a different computer without the same files and destinations. 

7.	Due to the fact that many assumptions can be made about the data and the way it is expected to run, I put additional try-except functions around the dropped Box Office info, as well as the SQL data load. Britta and her team should be aware that every time they run the code, they will have to clear the tables in the movie_data file. 

Overall, I’m excited that Amazing Prime afforded me the opportunity to work on this project. While the work was daunting and required a lot of time and effort to put the information into a useful format, I am glad to that I was able to take point on the project and complete it in a timely fashion. This will also allow Britta to meet he timeline and present the information.
