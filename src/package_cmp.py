import json
from source_util import get_source
from parsing import CmpParse
from source_code import FileSourceCode
from processing import Match
import os
source_lst = [s for s in os.listdir('../pkg') if '.jar' not in s]
# source_lst = ['commons-io-1.3.2-sources','commons-io-2.11.0-sources']
class cmp_pkg:
    def __init__(self):
        self.a_source=""
        self.b_source=""

    def cmp_path(self, a_file_lst:[], b_file_lst:[]):
        a_to_b = dict()
        b_to_a = dict()
        b_to_a_s = dict()
        for a in a_file_lst:
            match = Match(a,b_file_lst)
            if match.bscore > 0.5:
                a_to_b[a] = match.sdir
                if match.sdir in b_to_a and match.bscore>b_to_a_s[match.sdir]:
                    b_to_a[match.sdir] = a
                    b_to_a_s[match.sdir] = match.bscore
                if match.sdir not in b_to_a:
                    b_to_a[match.sdir] = a
                    b_to_a_s[match.sdir] = match.bscore
        #path_rate = min(len(a_to_b),len(b_to_a))/max(len(a_file_lst),len(b_file_lst))
        path_rate = len(b_to_a)/max(len(a_file_lst),len(b_file_lst))
        return a_to_b, b_to_a, path_rate

    def cmp_files(self, b_to_a):
        b_cmp = dict()
        file_rate = 0
        for b in b_to_a:
            if '.java' in b:
                a = b_to_a[b]
                a_code = FileSourceCode.get_file_code(self.a_source+'/'+a)
                b_code = FileSourceCode.get_file_code(self.b_source+'/'+b)
                #print(a_code)
                #print(b)
                b_cmp[b] = CmpParse(a_code,b_code).cmp
                print("file a:{}\nfile b:{}\ncmp:{}".format(a,b,b_cmp[b]))
        if b_cmp:
            file_rate = len([c for c in b_cmp if b_cmp[c]])/len(b_cmp)
        return b_cmp, file_rate
    def cmp_source(self, a_s, b_s):
        self.a_source='../pkg/'+a_s
        self.b_source='../pkg/'+b_s
        print(self.a_source)
        print(self.b_source)
        a_file_lst = get_source(self.a_source)
        b_file_lst = get_source(self.b_source)
        a_to_b, b_to_a, path_rate = self.cmp_path(a_file_lst, b_file_lst)
        b_cmp, file_rate = self.cmp_files(b_to_a)
        final_rate = path_rate * file_rate
        return len(a_file_lst), len(b_file_lst), len(b_to_a), path_rate, len([c for c in b_cmp if b_cmp[c]]), file_rate
if __name__ == '__main__':
    source_cmp_dicts = []
    s_num = len(source_lst)
    for i in range(0,s_num):
        for j in range(i+1,s_num):
            a_s = source_lst[i]
            b_s = source_lst[j]
            print(a_s)
            print(b_s)
            numa, numb, match_path, path_rate, match_file, file_rate = cmp_pkg().cmp_source(a_s,b_s)
            pre = (path_rate>=0.1)
            source_cmp_dict = {'a_source':a_s,'b_source':b_s,'a_file_num':numa,'b_file_num':numb,
                              'match_path':match_path,'path rate': path_rate,'match_file':match_file,
                               'file rate':file_rate,'predict':pre}
            source_cmp_dicts.append(source_cmp_dict)
    with open('../test/pkg_cmp.json', 'w') as outfile:
        json.dump(source_cmp_dicts, outfile)