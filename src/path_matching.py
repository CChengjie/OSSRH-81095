from collections import  Counter
class Match:
    def __init__(self,file:str, sdir_lst = []):
        self.file = file
        self.sdir_lst = sdir_lst
        self.sdir, self.bscore = self.match_score()
    def match_score(self):
        bscore = 0
        sdir = ""
        for dir in self.sdir_lst:
            score = self.get_score(dir,self.file)
            if score>self.bscore:
                bscore = score
                sdir = dir
        return sdir, bscore

    def get_score(self, sdir: str, rdir: str):
        if "test" in rdir:
            return 0
        sdir = [s for s in sdir.split('/')]
        rdir = [s for s in rdir.split('/')]
        Rdir = list(rdir)
        # issue:路径只有两个a/b.file 只要后面的match就行
        if sdir[-1] != rdir[-1] or sdir[0] not in rdir:
            return 0
        for dir in rdir:
            if dir == sdir[0]:
                break
            Rdir.remove(dir)
        N = (len(Rdir) + len(sdir)) / 2
        # [(n/N) * (LLCS(sdir,rdir)/N] * [(LLCS(rsdir,rrdir)/N)]
        n = len(list((Counter(sdir) & Counter(Rdir)).elements()))
        L_LLCS = self.LLCS(sdir, Rdir)
        R_LLCS = self.LLCS(list(reversed(sdir)), list(reversed(Rdir)))
        score = n / N * L_LLCS / N  # * R_LLCS / N
        return score

    def LLCS(self, sdir: list, rdir: list):
        slen = len(sdir)
        rlen = len(rdir)
        record = [[0 for i in range(rlen + 1)] for j in range(slen + 1)]
        for i in range(slen):
            for j in range(rlen):
                if sdir[i] == rdir[j]:
                    record[i + 1][j + 1] = record[i][j] + 1
                elif record[i + 1][j] > record[i][j + 1]:
                    record[i + 1][j + 1] = record[i + 1][j]
                else:
                    record[i + 1][j + 1] = record[i][j + 1]
        return record[-1][-1]
