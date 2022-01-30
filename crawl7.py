
import time
import os

import requests
import bs4
from bs4 import BeautifulSoup  
import pandas as pd
import scipy as sc
import numpy as np
import re


df = pd.DataFrame()
column = pd.DataFrame()
url_start = 'https://www.imdb.com'


def load_soup_object(html_file_name):
    r = requests.get(html_file_name)
    c = r.content
    soup = BeautifulSoup(c, 'html.parser')
    soup.prettify()
    return soup


def list_movies(soup):
    
    movie_url_l = list()
    url_end = '?pf_rd_m=A2FGELUUNOQJNL&amp;pf_rd_p=9703a62d-b88a-4e30-ae12-90fcafafa3fc&amp;pf_rd_r=03E5S0DJFP1203AC4186&amp;pf_rd_s=center-1&amp;pf_rd_t=15506&amp;pf_rd_i=top&amp;ref_=chttp_tt_'
    count = 1
    
    for div in soup("div", attrs={"class": "lister-item mode-advanced"}):
        for h in div("h3", attrs={"class": "lister-item-header"}):
            movie_url_l.append(url_start + h.a.get("href"))
            count += 1
    
    return movie_url_l


def build_df(url_list):

    movie_title = list()
    imdb_rating = list()
    number_of_users_rating = list()
    director_name = list()
    director_rated = list()
    star_1_name = list()
    star_1_rated = list()
    star_2_name = list()
    star_2_rated = list()
    star_3_name = list()
    star_3_rated = list()
    genres = list()
    motion_picture_rating = list()
    relese_year = list()
    contry_of_origin = list()
    language = list()
    budget = list()
    gross = list()
    run_time = list()
    color = list()
    sections = list()
    lis = list()

    for url in url_list:
        
        soup = load_soup_object(url)

        soup1 = soup.find("section", attrs=({"class":"ipc-page-section"}))

        if(soup1 == None):
            continue

        relese_year_raw = soup1.find_all("li", attrs=({"class":"ipc-inline-list__item"}))[0].find("span").text
        relese_year.append(relese_year_raw)

        check = soup1.find_all("li", attrs=({"class":"ipc-inline-list__item"}))[1].text
        if(check[1:2] == "h"):
            motion_picture_rating.append("UR")
        else:
            motion_picture_rating_raw = soup1.find_all("li", attrs=({"class":"ipc-inline-list__item"}))[1].find("span").text
            motion_picture_rating.append(motion_picture_rating_raw)

        if(check[1:2] == "h"):
            run_time_raw = soup1.find_all("li", attrs=({"class":"ipc-inline-list__item"}))[1].text
            run_time_raw = run_time_raw.replace("m", "")
            if(len(run_time_raw) > 3):
                run_time_min = int(run_time_raw[:1]) * 60 + int(run_time_raw[3:])
            else:
                run_time_min = int(run_time_raw[:1]) * 60
            run_time.append(run_time_min)
        else:
            run_time_raw = soup1.find_all("li", attrs=({"class":"ipc-inline-list__item"}))[2].text
            run_time_raw = run_time_raw.replace("m", "")
            if(len(run_time_raw) > 3):
                run_time_min = int(run_time_raw[:1]) * 60 + int(run_time_raw[3:])
            else:
                run_time_min = int(run_time_raw[:1]) * 60
            run_time.append(run_time_min)

        is_directors = False

        for li in soup1.find_all("li", attrs=({"class":"ipc-metadata-list__item"})):
            if(li.find("span") == None):
                if(li.find("a").text == "Stars" or li.find("a").text == "Director" or li.find("a").text == "Directors"):
                    if(li.find("a").text == "Directors"):
                        is_directors = True
                    lis.append(li)
                else:
                    li.decompose()
            else:
                if(li.find("a").text == "Stars" or li.find("a").text == "Director" or li.find("a").text == "Directors" or li.find("span").text == "Director" or li.find("span").text == "Directors" or li.find("span").text == "Stars"):
                    if(li.find("a").text == "Directors" or li.find("span").text == "Directors"):
                        is_directors = True
                    lis.append(li)
                else:
                    li.decompose()

        movie_title.append(soup1.find("h1").text)

        imdb_rating.append(soup1.find("span", attrs=({"class":"AggregateRatingButton__RatingScore-sc-1ll29m0-1"})).text)

        number_of_users_rating_raw = soup1.find("div", attrs=({"class":"AggregateRatingButton__TotalRatingAmount-sc-1ll29m0-3"})).text
        zeroes = "000000"
        if(number_of_users_rating_raw.find(".") > -1):
            number_of_users_rating_raw = number_of_users_rating_raw.replace(".", "")
            zeroes = "00000"
        if(number_of_users_rating_raw[-1:] == "M"):
            number_of_users_rating_raw = number_of_users_rating_raw[:-1] + zeroes
        elif(number_of_users_rating_raw[-1:] == "K"):
            number_of_users_rating_raw = number_of_users_rating_raw[:-1] + (zeroes[:3])
        else:
            number_of_users_rating_raw = number_of_users_rating_raw[:-1] + "?"
        number_of_users_rating.append(int(number_of_users_rating_raw))
        
        director_name.append(soup1.find("a", attrs=({"class":"ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link"})).text)
        director_rated_link = soup1.find("a", attrs=({"class":"ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link"})).get('href')
        director_rated_link_soup = load_soup_object(url_start + director_rated_link)
        if(director_rated_link_soup.find("a", attrs=({"id":"meterRank"})).text == "SEE RANK"):
            director_rated.append("Low")
        else:
            director_rated.append(director_rated_link_soup.find("a", attrs=({"id":"meterRank"})).text)

        if(is_directors == True):
            i1,i2,i3 = 2,3,4
        else:
            i1,i2,i3 = 1,2,3

        star_1_name.append(soup1.find_all("a", attrs=({"class":"ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link"}))[i1].text)
        star_1_rated_link = soup1.find_all("a", attrs=({"class":"ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link"}))[i1].get('href')
        star_1_rated_link_soup = load_soup_object(url_start + star_1_rated_link)
        if(star_1_rated_link_soup.find("a", attrs=({"id":"meterRank"})).text == "SEE RANK"):
            star_1_rated.append("Low")
        else:
            star_1_rated.append(star_1_rated_link_soup.find("a", attrs=({"id":"meterRank"})).text)

        star_2_name.append(soup1.find_all("a", attrs=({"class":"ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link"}))[i2].text)
        star_2_rated_link = soup1.find_all("a", attrs=({"class":"ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link"}))[i2].get('href')
        star_2_rated_link_soup = load_soup_object(url_start + star_2_rated_link)
        if(star_2_rated_link_soup.find("a", attrs=({"id":"meterRank"})).text == "SEE RANK"):
            star_2_rated.append("Low")
        else:
            star_2_rated.append(star_2_rated_link_soup.find("a", attrs=({"id":"meterRank"})).text)

        star_3_name.append(soup1.find_all("a", attrs=({"class":"ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link"}))[i3].text)
        star_3_rated_link = soup1.find_all("a", attrs=({"class":"ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link"}))[i3].get('href')
        star_3_rated_link_soup = load_soup_object(url_start + star_3_rated_link)
        if(star_3_rated_link_soup.find("a", attrs=({"id":"meterRank"})).text == "SEE RANK"):
            star_3_rated.append("Low")
        else:
            star_3_rated.append(star_3_rated_link_soup.find("a", attrs=({"id":"meterRank"})).text)

        for section in soup.find_all("section", attrs=({"class":"ipc-page-section"})):
            if((section.find("h3") != None) and (section.find("h3").text == "Storyline" or section.find("h3").text == "Details" or section.find("h3").text == "Box office" or section.find("h3").text == "Technical specs")):
                sections.append(section)
            else:
                section.decompose()
        
        soup2 = soup.find_all("section", attrs=({"class":"ipc-page-section"}))[0]
        soup3 = soup.find_all("section", attrs=({"class":"ipc-page-section"}))[1]
        soup4 = soup.find_all("section", attrs=({"class":"ipc-page-section"}))[2]
        if(len(soup.find_all("section", attrs=({"class":"ipc-page-section"}))) == 4):
            soup5 = soup.find_all("section", attrs=({"class":"ipc-page-section"}))[3]
        else:
            soup5 = soup4

        genres_raw = soup2.find_all("li", attrs=({"class":"ipc-metadata-list__item"}))[1].text
        if(genres_raw[:5] != "Genre"):
            genres_raw = soup2.find_all("li", attrs=({"class":"ipc-metadata-list__item"}))[0].text
        cut = 0
        if(genres_raw[:6] == "Genres"):
            cut = 6
        else:
            cut = 5
        genres_raw = genres_raw[cut:]

        #found help to quickly separate words by capitals after google search
        #found the tutorial at: https://www.geeksforgeeks.org/python-add-space-between-potential-words/
        #re is an import

        genres_raws = re.sub(r"(\w)([A-Z])", r"\1 \2", genres_raw)
        genres.append(genres_raws)

        contry_of_origin_raw = soup3.find_all("li", attrs=({"class":"ipc-metadata-list__item"}))[1].text
        cut = 0
        if(contry_of_origin_raw[:9] == "Countries"):
            cut = 19
        else:
            cut = 17
        contry_of_origin_raw = contry_of_origin_raw[cut:]
        contry_of_origin_raw = re.sub(r"(\w)([A-Z])", r"\1 \2", contry_of_origin_raw)
        contry_of_origin.append(contry_of_origin_raw)

        language_raw = soup3.find_all("li", attrs=({"class":"ipc-metadata-list__item"}))[2].text
        if(language_raw[:8] == "Official"):
                language_raw = soup3.find_all("li", attrs=({"class":"ipc-metadata-list__item"}))[3].text
        if(language_raw[:9] == "Languages"):
            language_raw = language_raw[9:]
            languages = re.sub(r"(\w)([A-Z])", r"\1 \2", language_raw)
            language.append(languages)
        else:
            language_raw = language_raw[8:]
            language.append(language_raw)

        if(soup4.find("h3").text == "Box office"):

            for i in range(len(soup4.find_all("li", attrs=({"class":"ipc-metadata-list__item"})))):
                    gross_raw = soup4.find_all("li", attrs=({"class":"ipc-metadata-list__item"}))[i].text
                    if(gross_raw[:15] == "Gross worldwide"):
                        gross_raw = gross_raw[16:]
                        gross_raw = gross_raw.replace(",", "")
                        gross.append(int(gross_raw))
                    elif(i == len(soup4.find_all("li", attrs=({"class":"ipc-metadata-list__item"})))-1):
                        gross.append(np.nan)

            budget_raw = soup4.find_all("li", attrs=({"class":"ipc-metadata-list__item"}))[0].text
            if(budget_raw[:6] == "Budget"):
                if(budget_raw[6:7] == "$"):
                    budget_raw = budget_raw[7:-12]
                    budget_raw = budget_raw.replace(",", "")
                    budget.append(int(budget_raw))
                    
                else:
                    budget.append(np.nan)

                
            else:
                budget.append(np.nan)
        else:
            budget.append(np.nan)
            gross.append(np.nan)

        if(len(soup5.find_all("li", attrs=({"class":"ipc-metadata-list__item"}))) == 1):
            color.append("color")
        else:
            if(soup5.find_all("li", attrs=({"class":"ipc-metadata-list__item"}))[1].text[0:5] == "Color"):
                color_raw = soup5.find_all("li", attrs=({"class":"ipc-metadata-list__item"}))[1].text
                color_raw = color_raw[5:]
                colors = re.sub(r"(\w)([A-Z])", r"\1/\2", color_raw)
                color.append(colors)
            else:
                color.append("color")
                
    df = pd.DataFrame({"movie_title": movie_title, "imdb_rating": imdb_rating, "number_of_users_rating": number_of_users_rating, "director_name": director_name, "director_rated": director_rated, "star_1_name": star_1_name, "star_1_rated": star_1_rated, "star_2_name": star_2_name, "star_2_rated": star_2_rated, "star_3_name": star_3_name, "star_3_rated": star_3_rated, "genres": genres, "motion_picture_rating": motion_picture_rating, "relese_year": relese_year, "contry_of_origin": contry_of_origin, "language": language, "budget": budget, "gross": gross, "run_time": run_time, "color": color})
    #df = pd.DataFrame({"genres": genres, "contry_of_origin": contry_of_origin, "budget": budget, "gross": gross, "run_time": run_time, "color": color})
    return df



def build_column(url_list):

    metascore_rating = list()
    score = ""

    for url in url_list:
        
        soup = load_soup_object(url)

        soup = soup.find("section", attrs=({"class":"ipc-page-section"}))
        soup = soup.find("ul", attrs=({"data-testid":"reviewContent-all-reviews"}))

        if(soup == None):
            continue

        for li in soup.find_all("li", attrs=({"class":"ipc-inline-list__item"})):
            score = "0"
            for item in li.find_all("span", attrs=({"class":"three-Elements"})):
                if item.find("span", attrs=({"class":"label"})).text == "Metascore":
                    score = item.find("span", attrs=({"class":"score-meta"})).text
        metascore_rating.append(score)
    column = pd.DataFrame({"metascore_rating": metascore_rating})
    return column



for i in range(4201, 4801, 50):
    url = 'https://www.imdb.com/search/title/?title_type=feature&num_votes=25000,&sort=user_rating,desc&start=' + str(i) + '&ref_=adv_nxt'
    soup = load_soup_object(url)
    movie_url_list = list_movies(soup)
    df_new = build_df(movie_url_list)
    df = pd.concat([df, df_new], ignore_index=True)
    # column_new = build_column(movie_url_list)
    # column = pd.concat([column, column_new], ignore_index=True)
df.to_csv('df_raw/df7.csv')
# column.to_csv('column_raw/column7.csv')