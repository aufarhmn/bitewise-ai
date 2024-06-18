import pandas as pd
from flask import Blueprint, jsonify, request
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy import create_engine

ai_blueprint = Blueprint('ai', __name__, url_prefix='/api/ai')

# LOAD DATA FROM DB
DATABASE_URL = "postgresql+psycopg2://user:pass@host/db-name"
engine = create_engine(DATABASE_URL)
df = pd.read_sql('SELECT * FROM bitewise', engine)

# DATA PREPROCESSING
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(df['describe'])
cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
count = CountVectorizer(stop_words='english')
count_matrix = count.fit_transform(df['soup'])
cosine_sim2 = cosine_similarity(count_matrix, count_matrix)
df = df.reset_index()
indices = pd.Series(df.index, index=df['name']).drop_duplicates()

@ai_blueprint.route('/highest-choices', methods=['POST'])
def highest_food_choices():
    data = request.get_json()
    veg_non = data['veg_non']
    c_type = data['c_type']

    if veg_non not in ['veg', 'non-veg']:
        return jsonify({'error': 'Invalid veg_non value'}), 400
    if c_type not in ['Healthy Food', 'Snack', 'Dessert', 'Japanese', 'Indian', 'French', 'Mexican', 'Italian', 'Chinese', 'Beverage', 'Thai', 'Korean', 'Vietnames', 'Nepalese', 'Spanish']:
        return jsonify({'error': 'Invalid c_type value'}), 400

    filtered_updated_food_data = df[(df['veg_non'] == veg_non) & (df['c_type'] == c_type)]
    sorted_filtered_data = filtered_updated_food_data.sort_values(by='average_rating', ascending=False)
    return jsonify(sorted_filtered_data[['name', 'describe', 'average_rating']].head(5).to_dict(orient='records')), 200

@ai_blueprint.route('/random-choices', methods=['POST'])
def random_food_choices():
    data = request.get_json()
    veg_non = data['veg_non']
    c_type = data['c_type']
    num_choices = data.get('num_choices', 5)

    if veg_non not in ['veg', 'non-veg']:
        return jsonify({'error': 'Invalid veg_non value'}), 400
    if c_type not in ['Healthy Food', 'Snack', 'Dessert', 'Japanese', 'Indian', 'French', 'Mexican', 'Italian', 'Chinese', 'Beverage', 'Thai', 'Korean', 'Vietnames', 'Nepalese', 'Spanish']:
        return jsonify({'error': 'Invalid c_type value'}), 400

    filtered_updated_food_data = df[(df['veg_non'] == veg_non) & (df['c_type'] == c_type)]
    sorted_filtered_data = filtered_updated_food_data.sort_values(by='average_rating', ascending=False)
    
    if len(sorted_filtered_data) <= num_choices:
        return jsonify(sorted_filtered_data[['name', 'describe', 'average_rating']].to_dict(orient='records')), 200
    else:
        return jsonify(sorted_filtered_data[['name', 'describe', 'average_rating']].sample(n=num_choices, random_state=1).to_dict(orient='records')), 200

@ai_blueprint.route('/recommendations', methods=['POST'])
def get_recommendations():
    data = request.get_json()
    title = data['title']
    
    if title not in indices:
        return jsonify({'error': 'Title not found'}), 404

    idx = indices[title]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:6]
    
    food_indices = [i[0] for i in sim_scores]

    recommended_recipes = []
    for idx in food_indices:
        recommended_recipes.append({
            'Name': df.loc[idx, 'name'],
            'Describe': df.loc[idx, 'soup']
        })
    
    return jsonify(recommended_recipes), 200
