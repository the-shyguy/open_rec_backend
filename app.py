from flask import Flask, request, jsonify
import pandas as pd
import pickle

app = Flask(__name__)
app.debug = True

@app.route('/')
def hello():
    return '<h1>Hello, World!</h1>'

@app.route('/repo_list', methods=['POST'])
def repo_list():
    res = request.get_json()
    if res is None:
        return jsonify({"error": "Invalid JSON"}), 400
    
    if res['data'] == [] or res['data'] is None or res['data'] == "" or res['data'] == {}:
        return jsonify({"error": "Data is empty"}), 400
    
    random_selected_repos = res['data']
    similarity = pickle.load(open('models/similarity.pkl','rb'))
    new_df_dict = pickle.load(open('repo_database/repo_dict.pkl','rb'))
    new_df = pd.DataFrame(new_df_dict)

    def recommend_repo(repo_name, repo_name_set):
        repo_index = new_df[new_df['repository_name']==repo_name].index[0]
        distances = similarity[repo_index]
        repos_list = sorted(list(enumerate(distances)),reverse=True,key=lambda x:x[1])[1:11]
        for i in repos_list:
            repo_name_set.add((new_df.iloc[i[0]].account_name, new_df.iloc[i[0]].repository_name))
    
    repo_name_set = set()
    for i in random_selected_repos:
        recommend_repo(i,repo_name_set)
    repo_name_list = list(repo_name_set)

    cleaned_data = pd.read_csv('repo_database/cleaned_data.csv')

    repo_list_full_data = []
    for i in repo_name_list:
        filtered_data = cleaned_data.loc[(cleaned_data['repository_name']==i[1]) & (cleaned_data['account_name']==i[0])]
        repo_list_full_data.append({'account_name':filtered_data['account_name'].values[0],'repository_name':filtered_data['repository_name'].values[0],'tags':filtered_data['tags'].values[0],'languages':filtered_data['languages'].values[0],'link':filtered_data['link'].values[0],'issues':f"{filtered_data['issues'].values[0]}",'pull_requests':f"{filtered_data['pull_requests'].values[0]}",'forks':f"{filtered_data['forks'].values[0]}",'stars':f"{filtered_data['stars'].values[0]}",'contributors':f"{filtered_data['contributors'].values[0]}"})

    return {"repo_list":repo_list_full_data, "code": 200}

@app.route('/item_list', methods=['POST'])
def item_list():
    res = request.get_json()
    if res is None:
        return jsonify({"error": "Invalid JSON"}), 400
    
    if res['data'] == [] or res['data'] is None or res['data'] == "" or res['data'] == {}:
        return jsonify({"error": "Data is empty"}), 400
    
    random_selected_items = res['data']
    data_neighbours_dict = pickle.load(open('models/item_item_data.pkl','rb'))
    data_neighbours = pd.DataFrame(data_neighbours_dict)
    item_dict = {}
    for i in random_selected_items:
        item_dict[i] = data_neighbours.loc[i].to_dict()
    
    return jsonify({"item_list":item_dict, "code": 200})

@app.route('/random_repos', methods=['GET'])
def random_repos():
    new_df = pd.read_csv('repo_database/fractioned_shuffled_data.csv')
    random_repo_names = new_df[['account_name','repository_name']].sample(n=10)
    random_repo_names = [tuple(row) for row in random_repo_names.values]
    cleaned_data = pd.read_csv('repo_database/cleaned_data.csv')
    repo_list_full_data = []
    for i in random_repo_names:
        filtered_data = cleaned_data.loc[(cleaned_data['repository_name']==i[1]) & (cleaned_data['account_name']==i[0])]
        repo_list_full_data.append({'account_name':filtered_data['account_name'].values[0],'repository_name':filtered_data['repository_name'].values[0],'tags':filtered_data['tags'].values[0],'languages':filtered_data['languages'].values[0],'link':filtered_data['link'].values[0],'issues':f"{filtered_data['issues'].values[0]}",'pull_requests':f"{filtered_data['pull_requests'].values[0]}",'forks':f"{filtered_data['forks'].values[0]}",'stars':f"{filtered_data['stars'].values[0]}",'contributors':f"{filtered_data['contributors'].values[0]}"})
    return jsonify({"repo_list":repo_list_full_data, "code": 200})

