from commit import CommitTree
from commit import GetSourcesCommits
from file_record import FileHis
from repo_util import RepoUtil
from source_util import get_source
from source_code import CommitSourceCode, FileSourceCode
from search import SearchCommits
from config import Config
from pydriller import RepositoryMining, GitRepository
from repo_util import LocalRepo
from processing import Match
import os
import re

def p_version(ref=str, tag=str):
    ref = [re for re in ref.split('.')]  # 分隔不一定是‘.’ 还有‘-’‘_‘
    tag = [ta for ta in tag.split('.')]
    for i in range(0, len(ref)):
        if ref[i] == 'x':
            break
        if ref[i] == tag[i]:
            continue
        return False
    return True


def ref_match(ref):
    ref = [r for r in ref.split('/')][-1]
    # 提取 ref 和 path 版本号
    ref = re.search(Config.pattern, ref)
    if ref == None:
        return False
    ref = ref.group(0)
    # print("ref: ",ref)
    return p_version(ref, Config.ver)

def find_tag(repo):
    print(Config.ver)

# ref=0 默认指向主分支，可以只调用only_ref
def only_ref(repo, ref=0):
    commits = []
    commit_ids = []
    match_file_num = 0

    tree = CommitTree(repo, ref)  # build tree
    file_his_url = Config.file_his_url + str(ref) + '_' + Config.s_name + '_file_his.json'
    LocalRepo(Config.github_url, Config.repo_path, ref)
    # if not exists file_his
    if not os.path.exists(file_his_url):
        get_file_his = FileHis()
        get_file_his.get_record_lst()
        get_file_his.save_json(get_file_his, file_his_url, ref)

    file_his = FileHis.read_json(file_his_url)

    sources = get_source(Config.s_path)
    get_source_commits = GetSourcesCommits(tree, file_his, sources)
    common_commits = get_source_commits.get_commit_range_for_source()

    cmt_s_code = CommitSourceCode(file_his.repo, get_source_commits.repo_2_source)
    commits, commit_ids, match_file_num = SearchCommits(common_commits, cmt_s_code, file_his,
                                                        Config.s_path).search()
    print(commits, '\n', commit_ids, '\n', match_file_num)
    return commits, commit_ids, match_file_num


# 遍历多分支 建树应该建成一棵树？ 或者把分支看成独立的 取最
def multi_ref(repo):
    commits = []
    commit_ids = []
    match_file_num = 0
    tag = 'master'
    branches = [str(r).split('/')[-1] for r in repo.refs if r not in repo.tags]
    refs = list(set(branches))
    refs.sort(key=branches.index)
    print(refs)
    for i, ref in enumerate(repo.refs):
        if i==0:
            continue
        if ref in repo.tags:
            break
        if i == 0 or ref_match(str(ref)):
            print("ref: ", ref)
            commits_i, commit_ids_i, match_file_num_i = only_ref(repo, i)
            if match_file_num_i > match_file_num:
                commits = commits_i
                commit_ids = commit_ids_i
                match_file_num = match_file_num_i
                tag = ref
    print(tag)
    print(commits, '\n', commit_ids, '\n', match_file_num)
    return commits, commit_ids, match_file_num

def inver(commits:[]):
    output = []
    for cmt in commits:
        msg = GitRepository(Config.repo_path).get_commit(cmt).msg
        if Config.ver in msg:
            output.append(cmt)
    if len(output)!=0:
        return output
    return commits

if __name__ == '__main__':
    # 需要新增refs的遍历。
    repo = RepoUtil.get_repo(github_url=Config.github_url, path=Config.repo_path)  # repo

    commits, commit_ids, match_file_num = multi_ref(repo)

    print("cmt num: ", len(commits))
    print("commits: ", commits)
    print("commits id: ", commit_ids)
    print("match file num: ", match_file_num)

    commits = inver(commits)
    print(commits)
    print()
    # for x, y, z in zip(commits, commit_ids, match_file_num):
    #     print("match file num: ",match_file_num[z])
    #     print("cmt num = ", len(commits[x]))
    #     if len(commits[x]):
    #         print(commits[x])
    #         print(commit_ids[y])
    #         print("commit[{},{}]".format(commits[x][0], commits[x][-1]))
    #         print("cmt[{},{}] ".format(commit_ids[y][0], commit_ids[y][-1]))
