from flask import Flask, render_template, request, jsonify
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.stem.porter import PorterStemmer
from langdetect import detect

app = Flask(__name__)


data = pd.read_csv('coursera_data.csv')


data['Ratings'].fillna(data['Ratings'].median(), inplace=True)
data['Skills_Gained'].fillna('Unknown', inplace=True)
data['Number_of_Ratings'].fillna(0, inplace=True)


data['tags'] = data['Course_Name'] + ',' + data['Skills_Gained'] + ',' + data['Course_Link']


ps = PorterStemmer()
data['tags'] = data['tags'].apply(lambda x: ' '.join([ps.stem(word) for word in x.split()]))


cv = CountVectorizer(max_features=15000, stop_words='english')
vectors = cv.fit_transform(data['tags']).toarray()


similarity = cosine_similarity(vectors)


'''
def recommend(course, rating_weight=0.5):
    course_index = data[data['Course_Name'] == course].index[0]
    distances = similarity[course_index]

    ratings = data['Ratings']
    ratings_numeric = pd.to_numeric(ratings, errors='coerce')
    ratings_numeric.fillna(0, inplace=True)
    normalized_ratings = (ratings_numeric - ratings_numeric.min()) / (ratings_numeric.max() - ratings_numeric.min())
    rating_similarity = cosine_similarity([normalized_ratings])[0]

    combined_similarity = (1 - rating_weight) * distances + rating_weight * rating_similarity
    course_list = sorted(list(enumerate(combined_similarity)), reverse=True, key=lambda x: x[1])[1:15]

    recommended_courses = []
    recommended_links = []
    for i in course_list:
        recommended_course_name = data.iloc[i[0]]['Course_Name']
        recommended_courses.append(recommended_course_name)
        recommended_course_link = data.iloc[i[0]]['Course_Link']
        recommended_links.append(recommended_course_link)
    
    return recommended_courses, recommended_links


'''

def recommend(query, rating_weight=0.5):
    # Check if the query exactly matches a course name
    exact_match = data[data['Course_Name'] == query]


    if not exact_match.empty:
        course_index = exact_match.index[0]
    else:
        # If no exact match, assume it's a skill and find courses related to it
        skill_matches = data[data['Skills_Gained'].str.contains(query)]
        if skill_matches.empty:
            return [], []
        # Take the first matched course
        course_index = skill_matches.index[0]

    distances = similarity[course_index]

    ratings = data['Ratings']
    ratings_numeric = pd.to_numeric(ratings, errors='coerce')
    ratings_numeric.fillna(0, inplace=True)
    normalized_ratings = (ratings_numeric - ratings_numeric.min()) / (ratings_numeric.max() - ratings_numeric.min())
    rating_similarity = cosine_similarity([normalized_ratings])[0]

    combined_similarity = (1 - rating_weight) * distances + rating_weight * rating_similarity
    course_list = sorted(list(enumerate(combined_similarity)), reverse=True, key=lambda x: x[1])[1:15]

    recommended_courses = []
    recommended_links = []
    for i in course_list:
        recommended_course_name = data.iloc[i[0]]['Course_Name']
        recommended_courses.append(recommended_course_name)
        recommended_course_link = data.iloc[i[0]]['Course_Link']
        recommended_links.append(recommended_course_link)
    
    return recommended_courses, recommended_links









@app.route('/')
def home():
    return render_template('index.html')


@app.route('/recommend', methods=['POST'])
def get_recommendations():
    course = request.form['course']
    recommended_courses, recommended_links = recommend(course)
    return jsonify({'recommended_courses': recommended_courses, 'recommended_links': recommended_links})



if __name__ == '__main__':
    app.run(debug=True)
