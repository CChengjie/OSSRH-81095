import json

from repo_util import LocalRepo, RepoConfig

class FileCommitRecord:
    def __init__(self, name: str):
        self.file_name = name
        self.cmt_add = []
        self.cmt_rmv = []


# f1 ->  f2  是否合并，判断是否为rn， rnm 映射
class FileHis:
    def __init__(self, repo: LocalRepo, rename_from=None, record_lst=None):
        if record_lst is None:
            record_lst = []
        if rename_from is None:
            rename_from = {}

        self.repo = repo
        self.rename_from = rename_from
        self.record_lst = record_lst

    def get_record_lst(self):
        record_lst = dict()
        for i in range(0, len(self.repo.commit_objects)):
            print(i)
            if i == 0:
                add = [f for f in self.repo.commit_objects[i].stats.files]
                rmv = []
                print(add)
            else:
                add, rmv = self.difference(i)
            for it in add:
                if it == None:
                    continue
                if it not in record_lst:
                    record_lst[it] = FileCommitRecord(name=it)
                record_lst[it].cmt_add.append(self.repo.commits[i])
            for it in rmv:
                if it == None:
                    continue
                if it not in record_lst:
                    record_lst[it] = FileCommitRecord(name=it)
                record_lst[it].cmt_rmv.append(self.repo.commits[i])
        self.record_lst = record_lst

    def file_commit_lst(self, file_name: str):  # 包含file_name文件的commit列表,
        add = self.record_lst[file_name].cmt_add
        rmv = self.record_lst[file_name].cmt_rmv
        return add, rmv

    # get the difference of the parents of commit[i] with commit[i]
    def difference(self, i):
        p = self.repo.parents[i][0]
        add = [diff.a_path for diff in
               self.repo.commit_objects[p].diff(self.repo.commit_objects[i]).iter_change_type('A')]
        rmv = [diff.a_path for diff in
               self.repo.commit_objects[p].diff(self.repo.commit_objects[i]).iter_change_type('D')]
        rnma = [diff.a_path for diff in
                self.repo.commit_objects[p].diff(self.repo.commit_objects[i]).iter_change_type('R')]
        rnmb = [diff.b_path for diff in
                self.repo.commit_objects[p].diff(self.repo.commit_objects[i]).iter_change_type('R')]
        for j, p in enumerate(self.repo.parents[i]):
            if j != 0:
                add = list(set(add).intersection(set([diff.a_path for diff in self.repo.commit_objects[p].diff(
                    self.repo.commit_objects[i]).iter_change_type('A')])))
                rmv = list(set(rmv).intersection(set([diff.a_path for diff in self.repo.commit_objects[p].diff(
                    self.repo.commit_objects[i]).iter_change_type('D')])))
                rnma = rnma + [diff.a_path for diff in
                               self.repo.commit_objects[p].diff(self.repo.commit_objects[i]).iter_change_type('R')]
                rnmb = rnmb + [diff.b_path for diff in
                               self.repo.commit_objects[p].diff(self.repo.commit_objects[i]).iter_change_type('R')]

        for k, it in enumerate(rnma):
            self.rename_from[rnmb[k]] = rnma[k]
            rmv.append(rnma[k])
            add.append(rnmb[k])
        return add, rmv

    def get_all_file_list(self):
        return [f for f in self.record_lst]  # commit历史中出现过的文件

    @staticmethod
    def save_json(file_his, filename, iref):
        file_record_list = list()
        for it in file_his.record_lst:
            file = dict()
            file['file_name'] = file_his.record_lst[it].file_name
            file['add_commit'] = file_his.record_lst[it].cmt_add
            file['rmv_commit'] = file_his.record_lst[it].cmt_rmv
            file_record_list.append(file)
        rename = [{'a_path': a_path, 'b_path': file_his.rename_from[a_path]} for a_path in file_his.rename_from]
        data = {'repo_url': file_his.repo.github_url,'ref_id':iref, 'rename_from': rename, 'file_record_list': file_record_list}
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
        print(" save file record succeed ! ")

    @staticmethod
    def read_json(filename):
        with open(filename, 'r', encoding='utf8')as fp:
            json_data = json.load(fp)
        repo_url = json_data['repo_url']
        iref = json_data['ref_id']
        file_record = []
        for data in json_data['file_record_list']:
            record = FileCommitRecord(name=data['file_name'])
            record.cmt_add = data['add_commit']
            record.cmt_rmv = data['rmv_commit']
            file_record.append(record)
        rename_dict = json_data['rename_from']
        rename_from = {rename_pair['a_path']: rename_pair['b_path'] for rename_pair in rename_dict}
        return FileHis(LocalRepo(repo_url, RepoConfig.LOCAL_REPO_PATH + '/' + repo_url.split('/')[-1], iref), rename_from,
                       file_record)
