from source_code import CommitSourceCode
from file_record import FileHis
from parsing import CmpParse
from source_code import FileSourceCode

from tqdm import tqdm
import time


class SearchCommits:
    def __init__(self, common_commits, cmt_s_code: CommitSourceCode, file_his: FileHis, s_path):
        self.file_his = file_his
        self.common_commits = common_commits  # sorted(common_commits, key=lambda x: file_his.repo.commit_2_index[x])
        self.cmt_s_code = cmt_s_code
        self.s_path = s_path  # source path 源码包路径

    #def search(self):
    def search(self,commit):
        match_num = 0
        maxnum = match_num
        commits = []
        commit_ids = []
        pre = 0
        deg = 0
        # f_cmp[f] f是否匹配
        f_cmp = dict()
        for cmt in tqdm(self.common_commits):
            #time.sleep(0.1)
            # 获取修改前后的代码
            bef_cmt_codes, pre_cmt_codes = self.cmt_s_code.only_commit_souce_code(cmt)
            for f in pre_cmt_codes:
                print("file: ",f)
                pre_code = pre_cmt_codes[f]
                bef_code = bef_cmt_codes[f]  # 如果前后没有变化，则不属于新增匹配文件
                if '.java' in f:  # 现在只能解析java file
                    # 判断前后是否有变化 如果没有变化，无需比较
                    # 任何一个为None， 都是有变化
                    if pre_code != None and bef_code != None:
                        if CmpParse(pre_code, bef_code).cmp:
                            continue
                    # 判断变化后和源文件是否相同
                    # print("s_file:",self.cmt_s_code.f_lst[f])
                    s_code = FileSourceCode.get_file_code(self.s_path + '/' + self.cmt_s_code.f_lst[f])
                    if pre_code==s_code:
                        f_cmp[f]=True
                        continue
                    f_cmp[f] = CmpParse(pre_code, s_code).cmp
                    print("好慢")
            num = len([f for f in f_cmp if f_cmp[f]])
            if cmt=='914e7c9f2cb8ce66724bf26a72adc7e958992497':
                print()
            if num > maxnum or (num==maxnum and pre>0):
                pre = 0
                maxnum = num
                commits = []
                commit_ids = []
            if num == maxnum and pre==0:
                commits.append(cmt)
                commit_ids.append(self.file_his.repo.commit_2_index[cmt])
            if num < maxnum: # 为什么num会变小?
                pre = pre+1
                if commit in commits:
                    break
        return commits, commit_ids, maxnum