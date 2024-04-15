from flask import Flask, render_template, request, jsonify
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.stem.porter import PorterStemmer
from langdetect import detect

app = Flask(__name__)


data = pd.read_csv('Coursera_Course_Recommendation/coursera_data.csv')


data['Ratings'].fillna(data['Ratings'].median(), inplace=True)
data['Skills_Gained'].fillna('Unknown', inplace=True)
data['Number_of_Ratings'].fillna(0, inplace=True)


data['tags'] = data['Course_Name'] + ',' + data['Skills_Gained'] + ',' + data['Course_Link']


ps = PorterStemmer()
data['tags'] = data['tags'].apply(lambda x: ' '.join([ps.stem(word) for word in x.split()]))


cv = CountVectorizer(max_features=15000, stop_words='english')
vectors = cv.fit_transform(data['tags']).toarray()


similarity = cosine_similarity(vectors)





def recommend(query, rating_weight=0.1):
    # Convert query to lowercase
    query = query.lower()
    
    exact_match = data[data['Course_Name'].str.lower() == query]

    if not exact_match.empty:
        course_index = exact_match.index[0]
    else:
        skill_matches = data[data['Skills_Gained'].str.lower().str.contains(query)]
        if skill_matches.empty:
            return [], []
        course_index = skill_matches.index[0]

    cos_sim_query_course = similarity[course_index]

    # Define a list of indices from 0 to the length of cos_sim_query_course
    indices = range(len(cos_sim_query_course))

    # Define a lambda function to use as the key for sorting
    def sorting_key(i):
        # Tuple containing the cosine similarity score and negative of the ratings
        return (cos_sim_query_course[i], -data.iloc[i]['Ratings'])

    # Sort the indices based on the sorting key
    sorted_indices = sorted(indices, key=sorting_key, reverse=True)

    recommended_courses = []
    recommended_links = []
    
    # Choose the top courses based on sorted indices
    for i in sorted_indices[1:15]:  # Exclude the query course itself
        recommended_course_name = data.iloc[i]['Course_Name']
        recommended_courses.append(recommended_course_name)
        recommended_course_link = data.iloc[i]['Course_Link']
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
