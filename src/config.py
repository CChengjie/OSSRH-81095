import re
# 路径配置。
import pandas as pd
from urllib.request import urlretrieve
import zipfile

class Config:
    #pattern = r'\d+\.(?:\d+\.)*\w+'
    pattern = r'\d+(\.|\_|\-)(?:\w+(\.|\_|\-))*\d+'   # 数字 + 连接符(._-) + 符号 组成 结尾最好也是数字，否则会把文件名连接符也算进去，但是会损失类似'beta''final'结尾
    s_path = '../vsrc/undertow-core-1.4.9.Final-sources'  # 源码包地址
    ver = re.search(pattern, s_path).group(0)
    s_name = 'undertow'  # 软件名
    github_url = 'https://github.com/undertow-io/undertow'  # 软件github地址
    repo_path = '../repo/' + s_name  # repo存储地址(默认)
   # file_his_url = '../file_his/' + s_name + '_all_file_his.json'  # file_his存储地址(默认)
    file_his_url = '../file_his/'   # file_his存储地址(默认)

def id_to_name():
    df = pd.read_csv('C:/Users/c50021559/Desktop/dataset/open_source_software.csv')
    df = df.drop([index for index in range(df.shape[0]) if df.loc[index,'blackhole_type']!='MAVEN'])
    df.reset_index(drop=True, inplace=True)
    id2name = dict()
    id2url = dict()
    for index in range(df.shape[0]):
        id = df.loc[index,'id']
        name = df.loc[index,'name']
        url = df.loc[index,'http_url']
        id2name[id]=name
        id2url[id] = url
    return id2name, id2url
class ConfigTest:

    def __init__(self):
        self.load_file = 'pkg_repo_cmt.csv'  # 文件
        self.pattern = r'\d+(\.|\_|\-)(?:\w+(\.|\_|\-))*\d+'
        self.df = pd.read_csv(self.load_file) # dataflow
        self.ver = 0   # version
        self.s_path = str # source path
        self.github_url = str  # github url
        self.s_name = str  # software name
        self.id2name, _= id_to_name()
        self.file_his_url = '../file_his/'

    def get_path(self,index):
        self.ver = self.df.loc[index,'version']
        self.name = self.df.loc[index,'name']  # NAME
        self.pkg_name = self.df.loc[index,'pkg_name']   # download pag name
        download = self.df.loc[index,'pkg_url']    # download url
        self.dirname = '../download/'+self.pkg_name   # download dir
        self.s_path = '../download/'+self.pkg_name.replace('.jar','')   # unzip url
        urlretrieve(download , self.dirname)   # download
        with zipfile.ZipFile(self.dirname, 'r') as zip:   #unzip
            zip.extractall(self.s_path)
        self.github_url = self.df.loc[index,'github_url']
        self.s_name = str(self.id2name[self.df.loc[index,'id']])
        self.repo_path = '../repo/' + self.s_name

