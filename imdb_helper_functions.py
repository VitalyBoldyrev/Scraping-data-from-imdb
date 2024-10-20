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

def build_full_credits_url(url):
    match = re.compile(r'\?.*')
    return re.sub(match, 'fullcredits', url)

def page_soup(url):
    user_agent = {'User-agent': 'Mozilla 5.0'}
    fullcredits = '/fullcredits'
    if fullcredits in url:
        response = requests.get(url, headers=user_agent)
    else:
        response = requests.get(url+fullcredits, headers=user_agent)
    return BeautifulSoup(response.text, 'html.parser')

def find_actor_filmography_section(soup, sections = 0):
    for i in range(len(soup.find_all(class_='filmo-category-section'))):
        section = soup.find_all('div')[i]
        if section.get('id') and section.get('id').split('-')[0] in ('actor', 'actress'):
            sections = i
    return sections

def filter_released_movie(movie):
    year_text = movie.find('span', class_= 'year_column').text.strip()
    return year_text not in ['????', ''] and movie.find('a', attrs={'class': 'in_production'}) is None

def filter_feature_film(movie):
    exclude_list = ['(TV Series)',
                    '(Short)',
                    '(Video Game)',
                    '(Video documentary)',
                    '(Video documentary short)',
                    '(Video short)', '(Video)',
                    '(TV Movie)', '(TV Mini Series)',
                    '(TV Mini-Series)', '(TV Series short)',
                    '(TV Series documentary)',
                    '(TV Special)',
                    '(Music Video)',
                    '(Music Video short)']
    return movie.contents[4].strip() not in exclude_list

def fix_url_prefix(url):
    if not url.startswith('https://www.'):
        url = 'https://www.' + url
    return url

def save_distances(path, actors_links):
    try:
        df = pd.read_csv(path)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        df = pd.DataFrame(columns=['first_actor_name', 'first_actor_page', 'second_actor_name', 'second_actor_page', 'distance'])
        df.to_csv(path, index=False, header=True)

    for first_actor_name, first_actor_page in actors_links.items():
        for second_actor_name, second_actor_page in actors_links.items():
            if first_actor_name != second_actor_name and (df[(df['first_actor_name'] == first_actor_name) & (df['second_actor_name'] == second_actor_name)].empty):
                print(f'Saving distance between {first_actor_name} and {second_actor_name}')
                with open(path, 'a') as f:
                    writer = csv.writer(f)
                    writer.writerow([first_actor_name, first_actor_page, second_actor_name, second_actor_page, get_movie_distance(first_actor_page, second_actor_page, 5, 5)])
            else:
                print(f'The distance between {first_actor_name} and {second_actor_name} is saved')
                
def build_graph(level, distance=None, layout="spring", node_size=900):

    try:
        df = pd.read_csv(level)
    except FileNotFoundError:
        print(f"Error: CSV file not found at {level}")
        return

    df = df[df['distance'] != -1]

    if distance:
        df = df[df['distance'] == distance]

    df.columns = ['first_actor_name', 'first_actor_page', 'second_actor_name', 'second_actor_page', 'distance']

    G = nx.DiGraph()
    for _, row in df.iterrows():
        G.add_edge(row['first_actor_name'], row['second_actor_name'], weight=row['distance'])

    layout_func = getattr(nx, f"{layout}_layout")
    layout = layout_func(G)

    plt.figure(figsize=(16, 9))
    nx.draw_networkx_nodes(G, layout, node_size=node_size)

    distance_to_color = {1: 'Tomato', 2: 'yellow', 3: 'blue'}

    edges = G.edges(data=True)
    colors = [distance_to_color[data['weight']] for _, _, data in edges]
    nx.draw_networkx_edges(G, layout, edge_color=colors)

    lab = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_labels(G, layout, font_size=12, alpha=0.9)
    nx.draw_networkx_edge_labels(G, layout, edge_labels=lab)

    plt.show()
    

def save_descriptions(path, actors_links):
    if not os.path.exists(path):
        os.makedirs(path)
    existing_files = os.listdir(path)
    if len(existing_files) >= len(actors_links):
        print(f'Descriptions already exist')
        return None
    actor_soups = {name: page_soup(url) for name, url in actors_links.items()}
    for name, soup in actor_soups.items():
        with open(f'./{path}/{name}.txt', 'w', encoding="utf-8") as f:
            for d in get_movie_descriptions_by_actor_soup(soup):
                f.write(d + '\n')

