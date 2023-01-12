import argparse
import colorsys
import numpy as np
import pandas as pd
import plotly.express as px
import textwrap
from school_names_to_course_names import *
from filter_courses import *
from search_courses import *
from matplotlib import colors as mcolors
from sklearn.manifold import TSNE

parser = argparse.ArgumentParser("MIT Course Search")
parser.add_argument('--mode', default='search', choices=['all', 'filter', 'search'])
parser.add_argument('--term', type=int, default=0, choices=[0, 1]) 
parser.add_argument('--filter', action="store_true")
parser.add_argument('--grad', action="store_true")
args = parser.parse_args()
mode = args.mode
term = args.term
filt = args.filter
grad = args.grad

df = pd.read_csv('mit_professors_with_embeddings.csv')
def feature_matrix(df):
    print("Extracting Embedding Feature Matrix...")
    matrix = df.embedding_combined.apply(eval).to_list()
    matrix_empty = np.zeros((len(matrix), len(matrix[0])))
    for i in range(len(matrix)):
        try:
            matrix_empty[i, :] = np.array(matrix[i])
        except Exception as e:
            print(i, e)
            print(matrix[i])
            exit()
    matrix = matrix_empty
    return matrix

df['recent_publications']  = ["<br>".join(textwrap.wrap(d)) for d in list(df.keywords)]
df['course_number'] = [f'{course_names[g]}' for g in list(df.school_affiliation)]

css4_colors = mcolors.CSS4_COLORS
def sort_course(x):
     x = x.split()[0]
     try:
         x1 = int(''.join(filter(str.isdigit, x)))
     except:
         x1 = float('inf')
     x2 = str(''.join(filter(str.isalpha, x)))
     return x1, x2

all_courses = sorted(list(df.course_number.unique()), key=sort_course)
def get_hsv(color_name):
    hexrgb = css4_colors[color_name]
    hexrgb = hexrgb.lstrip("#")   # in case you have Web color specs
    r, g, b = (int(hexrgb[i:i+2], 16) / 255.0 for i in range(0,5,2))
    return colorsys.rgb_to_hsv(r, g, b)

colors = list(css4_colors.keys())
colors = np.random.choice(colors, len(all_courses), False)
colors = sorted(colors, key=get_hsv)


if mode in ["all", "filter"]:
    print("Evaluating TSNE on Dataset...")
    df['color'] = [css4_colors[colors[all_courses.index(i)]] for i in list(df.course_number)]
    tsne = TSNE(n_components=2, perplexity=15, random_state=42, init='random', learning_rate=200)
    matrix = feature_matrix(df)
    vis_dims = tsne.fit_transform(matrix)
    df['x'] = [x for x,y in vis_dims]
    df['y'] = [y for x,y in vis_dims]
    dm = {all_courses[i]: colors[i] for i in range(len(all_courses))}
if mode == "all":
    fig = px.scatter(df, x='x', y='y', color='course_number', hover_data=['name', 'recent_publications'], color_discrete_map=dm, category_orders={'course_number': all_courses}, template="plotly_dark", title="MIT Professors Grouped by Study Area and Research Interests")
    fig.show()

elif mode == "filter":
    df = filter_courses(df)
    fig = px.scatter(df, x='x', y='y', color='course', hover_data=['course_number', 'title', 'description', 'prereq'], color_discrete_map=dm, category_orders={'course': all_courses}, template="plotly_dark", title="Courses Excluding 6, 16, and Low Units")
    fig.show()

elif mode == "search":
    if filt:
        df = filter_courses(df, grad)
    print("Searching for classes...")
    df_query = pd.read_csv('queries_with_embeddings.csv')
    df_query['embedding'] = df_query.embedding_combined.apply(eval)
    df['embedding'] = df.embedding_combined.apply(eval)
    course_numbers = list(search_courses(df, df_query.iloc[term]).course_number)
    print(course_numbers)
    tsne = TSNE(n_components=2, perplexity=15, random_state=42, init='random', learning_rate=200)
    matrix = feature_matrix(df)
    vis_dims = tsne.fit_transform(matrix)
    df['x'] = [x for x,y in vis_dims]
    df['y'] = [y for x,y in vis_dims]
    df = filter_search(df, course_numbers)
    dm = {all_courses[i]: colors[i] for i in range(len(all_courses))}
    fig = px.scatter(df, x='x', y='y', color='course', hover_data=['course_number', 'title', 'description', 'prereq'], color_discrete_map=dm, category_orders={'course': all_courses}, template="plotly_dark", title="Course Search Results for \"{}\"".format(df_query.iloc[term].text))
    fig.show()
