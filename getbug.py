
import urllib.request, json
import subprocess
import pandas as pd
import time
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import re
from urllib import error
from tqdm import tqdm

token = "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" #no expiration limit

BUG_KEYWORDS = ['error', 'bug', 'defect', 'patch', 'mistake', 'fault', 'failure', 'fix' , 'issue', 'incorrect','flaw']#,'triaged'

def IsNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False

def checkLabel(labels):
    is_bug = False
    for label in labels:
        for bug in BUG_KEYWORDS:
            if label['name'].lower().find(bug) != -1:
                is_bug = True
                break
        if is_bug:
            break
    return is_bug



repo_info = pd.read_csv('./javac_commits.csv',sep=',',header=None,names=['sha','repo_fullname', 'issune_num'])
sha_list = repo_info['sha']
repo_list = repo_info['repo_fullname']
issue_list = repo_info['issune_num']


new_sha = []
new_repo = []
issue_tag = []

for i in tqdm(range(len(sha_list))):
    # print(issue_list[i].split(','))
    found_bug = False
    for issue_No in issue_list[i].split(','):
        if found_bug:
            break
        if IsNumber(issue_No):
            url_issue = "https://api.github.com/repos/"+ repo_list[i] +"/issues/" + issue_No
            print(url_issue)
            req = urllib.request.Request(url=url_issue)
            req.add_header('Authorization', 'token %s' % token)
            try:
                resp = urllib.request.urlopen(req)
                issue = json.loads(resp.read())
            except error.URLError as e:
                if repo_list[i] == "python/cpython":
                    url_bug = "https://bugs.python.org/issue"+str(issue_No)
                    print(url_bug)
                    opener = urllib.request.build_opener()
                    opener.addheaders = [('User-agent','Mozilla/49.0.2')]
                    try:
                        opener.open(url_bug)
                        issue = {'labels': [{'name':'bug'}]}
                    except urllib.error.HTTPError:
                        issue = {'labels': []}
                        print("HTTPerror")
                    except urllib.error.URLError:
                        issue = {'labels': []}
                        print("URLerror")
                else:
                    issue = {'labels': []}
                    print(e)

            time.sleep(1)
            if len(issue['labels']) != 0:
                if checkLabel(issue['labels']):
                    types = ""
                    for j in range(0, len(issue['labels'])):
                        label = issue['labels'][j]['name']
                        types = types + ',' + issue['labels'][j]['name']
                    new_sha.append(sha_list[i])
                    new_repo.append(repo_list[i])
                    issue_tag.append(types)
                    found_bug = True



commits_list = pd.DataFrame({'sha': new_sha,
                             'repo': new_repo,
                             'issue':issue_tag})
commits_list.to_csv("javac_bug_commits.csv", mode='a', header=False, index=False, sep=',')

