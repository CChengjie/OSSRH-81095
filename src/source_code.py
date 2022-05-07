from pydriller import RepositoryMining, GitRepository
from repo_util import LocalRepo


class CommitSourceCode:
    def __init__(self, repo: LocalRepo, f_lst):
        self.local_repo = repo
        self.repo = repo.repo
        self.repo_path = repo.path
        self.f_lst = f_lst

    def only_commit_souce_code(self, cmt):  # 传参为一个commit，得到该commit中modify file和file code
        pre_file_code = dict()
        bef_file_code = dict()
        commit = GitRepository(self.repo_path).get_commit(cmt)
        # for commit in RepositoryMining(self.repo_path, only_commits=[cmt]).traverse_commits():
        # print("commit:",commit.hash)
        for m in commit.modifications:
            if m.new_path == None:
                continue
            filepath = m.new_path.replace('\\','/')
            if filepath not in self.f_lst: # 保证filepath 有对应的sourcefile
                continue

            source = m.source_code
            source_bef = m.source_code_before
            if source!=source_bef:
                pre_file_code[filepath] = source
                bef_file_code[filepath] = source_bef
        return bef_file_code, pre_file_code

class FileSourceCode:
    def get_file_code(file):
        with open(file, "r", encoding='ISO-8859-1') as f:
            data = f.read()
        return data

# import pydriller
# from config import Config
# g = pydriller.GitRepository(Config.repo_path)
# cmt = g.get_commit('93e1b161efcc9ef782cf808f4a2b9ed459b89d15')._get_branches()
# print(cmt)
# print()