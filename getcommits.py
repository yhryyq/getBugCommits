import os
import pandas as pd
import subprocess
from subprocess import Popen, PIPE, STDOUT
import shutil
import re
import stat
from tqdm import tqdm

def remove_readonly(func, path, _):
    "Clear the readonly bit and reattempt the removal"
    os.chmod(path, stat.S_IWRITE)
    func(path)

def rmdir(path):
    shutil.rmtree(path, onerror=remove_readonly)
    folder = os.path.exists(path)
    if not folder:
        print("folder removed")
    else:
        print("folder remove failed")

def exe_command(command):
    print("command: "+command)
    process = Popen(command, stdout=PIPE, stderr=STDOUT, shell=True)
    result = ""
    with process.stdout:
        for line in iter(process.stdout.readline, b''):
            try:
                result = result + line.decode().strip() + "$#$"
                print(line.decode().strip())
            except Exception as e:
                pass
    exitcode = process.wait()
    return result, process, exitcode


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

def ParseLogSmp(LogFile,repo):
    print("ParseLog...")
    sha_list = []
    proj_name_list = []
    issue_id_list = []
    sha = ""
    issue_id = ""
    with open(LogFile, 'r', encoding='latin1') as Lfile:
        for line in Lfile:
            if line[0:7] == "commit ":
                if sha != "" and issue_id != "":
                    sha_list.append(sha)
                    proj_name_list.append(repo)
                    issue_id_list.append(issue_id.strip(','))
                sha = line[7:-1]
                issue_id = ""

            elif line[0:8] != "Author: " and line[0:7] != "Merge: " and line[0:6] != "Date: ":
                if len(line) < 6:
                    continue

                issue = re.findall(r"#(\d+?)[\s\r\n]", line)
                if len(issue) == 0:
                    issue = re.findall(r"/issues/(\d+?)[\s\r\n]", line)
                if len(issue) == 0:
                    issue = re.findall(r"/pull/(\d+?)[\s\r\n]", line)
                if len(issue) != 0:
                    issue = issue[0]
                    if IsNumber(issue) == True:
                        issue_id = issue_id  + ","+ issue
    commits_list = pd.DataFrame({'sha': sha_list,
                                 'repo_fullname': proj_name_list,
                                 'issueId': issue_id_list})
    commits_list.to_csv("./javac_commits.csv", mode='a', header=False, index=False, sep=',')
    print("project "+repo+ " done")





#repo_info = pd.read_csv('../(C)Cpp&C+Python_repo_list_1000+.csv',sep=',', header=None,names=['id','html_url', 'api_url','full_name','open_issues','pushed_at', 'created_at','topics','description','commits_url'])
#repo_list = repo_info['full_name']
repo_list = ['ninia/jep','fusesource/jansi','java-native-access/jna','odnoklassniki/one-nio','luben/zstd-jni']


for i in tqdm(range(0,len(repo_list))):
    print("project number",i+1)
    repo = repo_list[i]
    cloneurl="https://github.com/" + repo + ".git"
    exe_command("git clone "+ cloneurl)
    proj_name = repo.split('/')[1]
    cmt_count = exe_command("cd " + proj_name + " && git rev-list --all --count")[0].strip("$#$")
    exe_command("cd "  + proj_name + " && git log -" + cmt_count + f" --date=iso > proj.mylog")
    ParseLogSmp("./"+ proj_name+"/proj.mylog",repo)
    rmdir("./"+ proj_name)

print("==========All DONE==========")
