from git import Repo
from repo_util import LocalRepo
from file_record import FileHis
from processing import Match


class CommitTree:
    def __init__(self, r: LocalRepo, ref=0):
        self.repo = r.repo
        self.commit_ids = [str(c) for c in list(self.repo.iter_commits(self.repo.refs[ref]))]
        self.commit_id_2_parent = r.parents
        self.commit_id_2_date = r.commit_id_2_date
        # for commit in self.repo.iter_commits(self.repo.refs[ref]):
        #     self.commit_id_2_parent[str(commit)] = [str(c) for c in commit.parents]
        #     self.commit_id_2_date[str(commit)] = commit.committed_date


class CommitsSearcher:

    def __init__(self, commit_tree: CommitTree, start_commits, end_commits):
        self.tree = commit_tree
        self.add_commits = start_commits
        self.rmv_commits = end_commits
        self.oldest_time = min([self.tree.commit_id_2_date[commit] for commit in start_commits])
        self.stack = []
        self.commits_in_range_paths = []
        self.commits_in_range = set()

    def search(self):
        if len(self.rmv_commits) == 0:
            latest_commit_id = self.tree.commit_ids[0]
            self.dfs(latest_commit_id, self.add_commits)
        else:
            rmv_commits = self.rmv_commits
            used_add_commits = set()
            for rmv_cmt in rmv_commits:
                add_commits = [cmt for cmt in self.add_commits
                               if self.tree.commit_id_2_date[cmt] < self.tree.commit_id_2_date[rmv_cmt]]
                used_add_commits = used_add_commits.union(add_commits)
                parent_commits = self.tree.commit_id_2_parent[rmv_cmt]
                for parent_commit in parent_commits:
                    self.dfs(parent_commit, add_commits)
            left_add_commits = [cmt for cmt in self.add_commits if cmt not in used_add_commits]
            if left_add_commits:
                latest_commit_id = self.tree.commit_ids[0]
                self.dfs(latest_commit_id, self.add_commits)
        return self

    def dfs(self, commit, target_commit):
        main_stack = []
        neibor_stack = []
        paths = []
        main_stack.append(commit)
        # 栈中节点的父节点，回溯时访问
        neibor_stack.append(self.tree.commit_id_2_parent[commit])
        # 在commit区间内的
        labeled = set()
        # 所有已经遍历过的
        visited = set()
        while len(main_stack) != 0:
            neibors = neibor_stack.pop()
            if neibors:
                main_stack.append(neibors[0])
                neibor_stack.append(neibors[1:])
                neibor_stack.append(self.tree.commit_id_2_parent[main_stack[-1]])
            else:
                cmt_top = main_stack.pop()
                for parent in self.tree.commit_id_2_parent[cmt_top]:
                    if parent in labeled:
                        labeled.add(cmt_top)
                visited.add(cmt_top)

            if len(main_stack) == 0:
                break

            main_top = main_stack[-1]
            if main_top in target_commit or main_top in labeled:
                path = main_stack.copy()
                path.reverse()
                paths.append(path)
                labeled.add(main_top)
                visited.add(main_top)
                main_stack.pop()
                neibor_stack.pop()
                continue
            if main_top in visited:
                main_stack.pop()
                neibor_stack.pop()
                continue
            if self.tree.commit_id_2_date[main_top] < self.oldest_time:
                visited.add(main_top)
                main_stack.pop()
                neibor_stack.pop()
                continue
        self.commits_in_range_paths.extend(paths)

    def get_commits_in_range_paths(self):
        return self.commits_in_range_paths

    def get_commits_in_range(self):
        all_commits = []
        for commits_path in self.commits_in_range_paths:
            all_commits.extend(commits_path)
        return sorted(list(set(all_commits)), key=lambda c: self.tree.commit_id_2_date[c])


class GetSourcesCommits:

    def __init__(self, tree: CommitTree, file_his: FileHis, sources: list):
        self.tree = tree
        self.file_his = file_his
        self.repo_filename_2_all_repo_file = {file_record.file_name: file_record for file_record in
                                              self.file_his.get_all_file_list()}

        self.repo_filenames = self.repo_filename_2_all_repo_file.keys()
        self.sources = sources

        self.repo_2_source, self.repo_file_2_best_match_score = self.match_repo_2_source()

        self.source_2_repo_files = self.get_source_2_repo_files()

        self.source_file_2_commits = self.get_source_file_2_commits()

    def match_repo_2_source(self):
        repo_file_2_best_match_score = {}
        repo_2_source = {}
        for repo_filename in self.repo_filenames:
            match = Match(repo_filename, self.sources)

            if match.bscore > 0.6:
                if repo_filename not in repo_file_2_best_match_score:
                    repo_file_2_best_match_score[repo_filename] = {match.sdir: match.bscore}
                    repo_2_source[repo_filename] = match.sdir
                else:
                    repo_file_2_best_match_score[repo_filename][match.sdir] = match.bscore
                    repo_2_source[repo_filename] = match.sdir
        return repo_2_source, repo_file_2_best_match_score

    def get_source_2_repo_files(self):
        # 遍历代码仓文件映射到的匹配度最高的源码包文件，可能有多个
        source_2_repo_files = {}
        for repo_filename in self.repo_2_source:
            source_file_name = self.repo_2_source[repo_filename]
            if (source_file_name not in source_2_repo_files):
                source_2_repo_files[source_file_name] = [repo_filename]
            else:
                # 最新的相似度比较大，就取最新的
                best_match_repo_file = source_2_repo_files[source_file_name][0]
                if (self.repo_file_2_best_match_score[best_match_repo_file][source_file_name] <
                        self.repo_file_2_best_match_score[repo_filename][source_file_name]):
                    source_2_repo_files[source_file_name] = [repo_filename]
                # 最新的相似度跟已有的一样，就添加到匹配列表
                if (self.repo_file_2_best_match_score[best_match_repo_file][source_file_name] ==
                        self.repo_file_2_best_match_score[repo_filename][source_file_name]):
                    source_2_repo_files[source_file_name].append(repo_filename)
        return source_2_repo_files

    def get_source_file_2_commits(self):
        # 获取所有源码文件可能存在的commit范围
        source_file_2_commits = {}
        for source_file in self.source_2_repo_files:
            repo_files = self.source_2_repo_files[source_file]
            for repo_file in repo_files:
                repo_file_record = self.repo_filename_2_all_repo_file[repo_file]
                searcher = CommitsSearcher(self.tree, repo_file_record.cmt_add, repo_file_record.cmt_rmv).search()
                commits = searcher.get_commits_in_range()
                if source_file not in source_file_2_commits:
                    source_file_2_commits[source_file] = commits
                else:
                    # 源码包文件匹配到多个代码仓文件的，可能的commit区间作并集
                    source_file_2_commits[source_file] = list(set(source_file_2_commits[source_file]).union(commits))
        return source_file_2_commits

    def get_common_commits(self):
        # 文件匹配，拿着代码仓的文件去源码包找对应的匹配对
        common_commits = set(self.tree.commit_ids)
        for source_file in self.source_file_2_commits:
            file_emerge_commits = set(self.source_file_2_commits[source_file])
            common_commits = common_commits.intersection(file_emerge_commits)
            print("s_f: ",source_file)
            print(self.source_2_repo_files[source_file])
            print(len(file_emerge_commits))
            print(len(common_commits))
            print()
        return sorted(common_commits, key=lambda x: self.tree.commit_id_2_date[x])

    def get_commit_range_for_source(self):
        source_commits_range = self.get_common_commits()
        return source_commits_range