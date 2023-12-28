import urllib.request, json
import subprocess
import pandas as pd
import time
import requests

id=[]
html_url=[]
api_url=[]
full_name=[]
open_issues=[]
pushed_at=[]
created_at=[]
topics=[]
description=[]
commits_url=[]

# print("Github Username: ", end="")
# username = str(input())
# print("Github Password: ", end="")
# password = str(input())

#######################################
# put your personal access token here
#######################################
token = "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" #no expiration limit

url = "https://api.github.com/search/repositories?q=stars:>3200+language:java+is:public&per_page=100&order=asc&page="
#urlFront = "https://api.github.com/search/repositories?q=stars:"
#urlForks = "+forks:"
#urlEnd = "+language:c+is:public&per_page=100&order=asc&page="

# stars_split = [">2000", "1001..2000"] # C
# stars_split = [">3990","2301..3990", "1601..2300", "1251..1600", "1001..1250"] #python
# stars_split = ["831..1000","711..830","621..710","556..620","501..555","456..500","416..455","386..415","361..385"]#python
# stars_split = ["601..1000","431..600","321..430","261..320","221..260","182..220","155..181"]#C


for i in range(1):
    # for star_num in stars_split:
    star_num = str(i) + ".." + str(i)
    # for forks in ["<15",">=15"]:
    for fork_num in range(1):
        '''
        if fork_num == 10:
            forks = ">=10"
        else:
            forks = str(fork_num) + ".." + str(fork_num)
        print(star_num)
        print(forks)
        '''
        for page in range(1,11):
            id = []
            html_url = []
            api_url = []
            full_name = []
            open_issues = []
            pushed_at = []
            created_at = []
            topics = []
            description = []
            commits_url = []
            c_percent = []
            java_percent = []
            print(f"page:{page}")
            url = url + str(page)
            #url = urlFront + star_num + urlForks + forks + urlEnd + str(page)
            # print(url)
            # response = urllib.request.urlopen(url)
            # data = json.loads(response.read())

            # response = gh_session.get(url)
            # data = json.loads(response.text)

            # response = requests.get(url,
            #                       auth=(username, password),
            #                       headers={"Accept": "application/vnd.github.mercy-preview+json"})
            # data = json.loads(response.text)

            request = urllib.request.Request(url=url)
            request.add_header('Authorization', 'token %s' % token)
            response = urllib.request.urlopen(request)

            data = json.loads(response.read())
            if len(data['items']) == 0:
                break
            counter = 1
            for project in data['items']:
                # resp = urllib.request.urlopen(project['languages_url'])
                # languages = json.loads(resp.read())
                print(counter)
                counter += 1
                req = urllib.request.Request(url=project['languages_url'])
                req.add_header('Authorization', 'token %s' % token)
                resp = urllib.request.urlopen(req)
                languages = json.loads(resp.read())
                # print(languages)
                if 'C' in languages.keys() and 'Java' in languages.keys():
                    c_count = languages["C"]
                    java_count = languages["Java"]
                    total_count = sum(languages.values())
                    c_percentage = (c_count / total_count) * 100
                    java_percentage = (java_count / total_count) * 100
                    id.append(project['id'])
                    html_url.append(project['html_url'])
                    api_url.append(project['url'])
                    full_name.append(project['full_name'])
                    open_issues.append(project['open_issues'])
                    pushed_at.append(project['pushed_at'])
                    created_at.append(project['created_at'])
                    topics.append(project['topics'])
                    description.append(project['description'])
                    commits_url.append(project['commits_url'])
                    c_percent.append(c_percentage)
                    java_percent.append(java_percentage)
                time.sleep(5)


            repo_list = pd.DataFrame({'id':id,
                                      'html_url':html_url,
                                      'api_url':api_url,
                                      'full_name':full_name,
                                      'open_issues':open_issues,
                                      'pushed_at':pushed_at,
                                      'created_at':created_at,
                                      'topics':topics,
                                      'description':description,
                                      'commits_url':commits_url})
            repo_list.to_csv("javac_repo_list_3200+.csv",mode='a', header=False, index=False, sep=',')
            time.sleep(30)
        time.sleep(60)

print("-------------------DONE--------------------")
