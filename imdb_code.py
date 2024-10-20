#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import csv
import networkx as nx
import matplotlib.pyplot as plt
import os
import networkx as nx
import wordcloud
from imdb_helper_functions import build_full_credits_url, page_soup, find_actor_filmography_section, filter_released_movie, filter_feature_film, fix_url_prefix, save_distances, build_graph, save_descriptions

def get_actors_by_movie_soup(cast_page_soup, num_of_actors_limit=None):
    cast_page_soup = page_soup(cast_page_soup)
    cast = cast_page_soup.find_all('table', class_='cast_list')
    if not cast:
        return []
    actors = [(td.text.strip(), build_full_credits_url('https://www.imdb.com' + td.find('a')['href']))\
              for td in cast[0].find_all('td', attrs={'class': None})]
    if num_of_actors_limit is not None:
        return actors[:num_of_actors_limit]
    return actors

def get_movies_by_actor_soup(actor_page_soup, num_of_movies_limit=None):
   
    section_index = find_actor_filmography_section(actor_page_soup)
    filmography_section = actor_page_soup.find_all('div', class_='filmo-category-section')[section_index]

    potential_movies = [movie for movie in filmography_section.find_all('div', class_='filmo-row') 
                      if filter_released_movie(movie) and filter_feature_film(movie)]

    movies = [movie for movie in potential_movies]

    movies = [(td.contents[3].text.strip(), build_full_credits_url('https://www.imdb.com' + td.find('a')['href']))\
              for td in movies]

    if num_of_movies_limit is not None:
        return movies[:num_of_movies_limit]
    return movies

def get_movie_distance(actor_start_url, actor_end_url, num_of_actors_limit=None, num_of_movies_limit=None):

    actor_start_url = fix_url_prefix(actor_start_url)
    actor_end_url = fix_url_prefix(actor_end_url)

    current_level = 1
    seen_movies = set()
    seen_actors = set(actor_start_url)
    actors_to_explore = [actor_start_url]

    while current_level <= 3: 
        unexplored_actors = []
        print(f'Iteration: {current_level}. Actors to check: {len(actors_to_explore)}')
        
        for actor_url in actors_to_explore:
            movies = get_movies_by_actor_soup(page_soup(actor_url), num_of_movies_limit)
            movies = [m for m in movies if m[1] not in seen_movies]

            for movie in movies:
                title, link = movie
                seen_movies.add(link)
                try:
                    actors = get_actors_by_movie_soup(link, num_of_actors_limit)
                except:
                    continue
                actors = [a for a in actors if a[1] not in seen_actors] 

                for _, actor_url in actors:
                    if actor_url == actor_end_url:
                        return current_level
                    if actor_url not in seen_actors:
                        unexplored_actors.append(actor_url)

        seen_movies.update(actors_to_explore)
        actors_to_explore = unexplored_actors
        current_level += 1
    return -1

def get_movie_descriptions_by_actor_soup(actor_page_soup, user_agent={'User-agent': 'Mozilla 5.0'}):

    descriptions = []
    movies = get_movies_by_actor_soup(actor_page_soup)

    for movie, url in movies:
        url = url.replace('/fullcredits', '')
        response = requests.get(url, headers=user_agent)
        movie_soup = BeautifulSoup(response.text)
        desc = movie_soup.find('span', {'data-testid': 'plot-xl', 'role': 'presentation'})
        if desc:
            descriptions.append(desc.text.strip())

    return descriptions

