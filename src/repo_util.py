import os
from git import Repo


class RepoConfig:
    LOCAL_REPO_PATH = os.getenv('LOCAL_REPO_PATH', '../repo')


class RepoUtil(object):

    @staticmethod
    def get_repo(github_url, path):
        if not os.path.exists(path):  # clone to path
            return Repo.clone_from(url=github_url, to_path=path)
        else:
            return Repo.init(path)

# master 记录内容
class LocalRepo:
    def __init__(self, github_url: str, path: str, ref=0): # ref 为分支refs下标，初始为0，代表主分支
        self.github_url = github_url
        self.path = path
        if not os.path.exists(self.path):  # clone to path
            self.repo = Repo.clone_from(url=github_url, to_path=self.path)
        else:
            self.repo = Repo.init(self.path)
        self.git = self.repo.git
        self.refs = self.repo.refs
        self.commit_objects = list(self.repo.iter_commits(self.refs[ref]))[::-1]
        self.commits = [str(c) for c in list(self.repo.iter_commits(self.refs[ref]))][::-1]
        self.tree = self.repo.tree(self.repo.heads[0])
        self.it_tree = [str(t) for t in list(self.repo.iter_trees())][::-1]
        ##
        self.parents = dict()
        self.commit_id_2_date=dict()
        for commit in self.repo.iter_commits(self.refs[ref]):
            self.parents[str(commit)] = [str(c) for c in commit.parents]
            self.commit_id_2_date[str(commit)] = commit.committed_date

        self.commit_2_index = dict()
        self.index_2_commit = list()

        ##
        self.commits = sorted(self.commits, key=lambda x: self.commit_id_2_date[x])
        for idx in range(0, len(self.commits)):
            self.commit_2_index[self.commits[idx]] = idx
            self.index_2_commit.append(self.commits[idx])
        # for idx in range(0, len(self.commits)):
        #     if self.commit_objects[idx].parents:
        #         self.parents[idx] = [self.commit_2_index[str(p)] for p in self.commit_objects[idx].parents]  # commit_2_index[str(p)] 可能还未出现
        self.commit_2_file_list = dict()