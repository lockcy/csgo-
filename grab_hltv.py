#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Disallow: /stats
import time
import random
import string
import requests
import numpy as np
from bs4 import BeautifulSoup

def get_html(url,data=None):

    header={
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.235'
    }
    #设定超时时间，防止被网站认为是爬虫
    timeout=random.choice(range(80,180))
    while True:
        try:
            rep=requests.get(url,headers=header,timeout=timeout)
            rep.encoding="utf-8"
            return rep
        except socket.timeout as e:
            print("3:",e)
            time.sleep(random.choice(range(8,15)))
        except socket.error as e:
            print("4:",e)
            time.sleep(random.choice(range(20,60)))
        except http.client.BadStatusLine as e:
            print("5:",e)
            time.sleep(random.choice(range(30,80)))
        except http.client.IncompleteRead as e:
            print("6:",e)
            time.sleep(random.choice(range(5,15)))

def get_result(start_date='2019-03-14',end_date='2019-03-14',stars=None,filename=None):
    #四个参数：开始日期 结束日期 比赛星级  文件名称
    root_url='https://www.hltv.org/'
    if filename == None:
        filename = 'result' + time.strftime('%Y-%m-%d %H.%M.%S', time.localtime(time.time())) + '.csv'
    offset=0
    total_page=10000000
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('比赛编号'+','+'比赛日期'+','+'比赛名称'+','+'队伍1'+','+'队伍2'+','+'大比分'+','+'胜利队伍'+','+('地图'+','+'比分'+',')*3+'\n')
    while total_page>0:
        result_url='https://www.hltv.org/results?offset={0}&startDate={1}&endDate={2}'.format(str(offset),str(start_date),str(end_date))
        if stars!=None:
            result_url=result_url+'&'+str(stars)
        #获取比赛综合页面
        rep=get_html(url=result_url)
        soup = BeautifulSoup(rep.content, "lxml")
        total_page_label=soup.find_all(name='span',attrs={"class":"pagination-data"})[0].text
        total_page = int(total_page_label.strip().split(' ')[-1])
        total_page=int(total_page/100)-1
        offset=offset+100
        for link in soup.find_all('a'):
            if '/matches/' in str(link.get('href')):
                data=[]
                new_url=root_url+str(link.get('href'))
                temp=str(link.get('href')).split('/')
                print (new_url)
                #获取比赛详细数据
                rep1=get_html(url=new_url)
                soup1 = BeautifulSoup(rep1.content, "lxml")
                #获取比赛编号
                data.append(temp[2])
                #获取比赛日期
                date=soup1.find_all(name='div',attrs={"class":"date"})
                data.append(date[0].text)
                team=soup1.find_all(name='div',attrs={"class": "teamName"})

                #获取比赛名称
                team1_temp=team[1].text.replace(' ','-').lower()
                match_name=new_url.split(team1_temp)[-1][1:]
                data.append(match_name)
                #获取队伍名称
                if 'female' in match_name:
                    data.append(team[0].text + '-female')
                    data.append(team[1].text + '-female')
                else:
                    data.append(team[0].text)
                    data.append(team[1].text)
                # 获取比分
                tie=soup1.find_all(name='div',attrs={"class": "tie"})
                won=soup1.find_all(name='div',attrs={"class": "won"})
                lost = soup1.find_all(name='div', attrs={"class": "lost"})
                if tie==[] and won==[]:
                    break
                if tie==[]:
                    data.append(won[0].text+'::'+lost[0].text)
                else:
                    data.append(tie[0].text+'::'+tie[1].text)
                # 获取胜利队伍
                if tie==[]:
                    team0_temp = ('<div class="teamName">' + team[0].text).lower()
                    index_won = rep1.text.find('<div class="won">')
                    if rep1.text[index_won - 100:index_won].lower().find(team0_temp) > 0:
                        if 'female' in match_name:
                            data.append(team[0].text+'-female')
                        else:
                            data.append(team[0].text)
                    else:
                        if 'female' in match_name:
                            data.append(team[1].text+'-female')
                        else:
                            data.append(team[1].text)
                else:
                    data.append('draw')
                #获取比赛地图
                # 获取比赛小分
                mapname=soup1.find_all(name='div',attrs={"class": "mapname"})
                map_won = soup1.find_all(name='span', attrs={"class": "won"})
                map_lost = soup1.find_all(name='span', attrs={"class": "lost"})
                count=0
                for i in mapname:
                    data.append(i.text.lower())
                    if count<=int(won[0].text)+int(lost[0].text):
                        if int(map_won[count].text)<0 or int(map_lost[count].text)<0:
                            break
                        if 'default' in i.text.lower():
                            break
                        map_result=str(map_won[count].text)+'::'+str(map_lost[count].text)
                        data.append((str(map_result)))
                        count += 1
                with open(filename,'a') as f:
                    for j in data:
                        f.write(j+',')
                    f.write('\n')
                f.close()
                print (data)

def get_rank(rank_url,filename=None):
    url_split=rank_url.split('/')
    if filename==None:
        filename=url_split[-3]+'.'+url_split[-2]+'.'+url_split[-1]+'.csv'

    rep = get_html(url=rank_url)
    soup = BeautifulSoup(rep.content, "lxml")
    teamnames = soup.find_all(name='span', attrs={"class": "name"})
    points = soup.find_all(name='span', attrs={"class": "points"})
    count=1
    with open(filename,'w') as f:
        f.write('排名'+','+'队伍'+','+'分数'+'\n')
        for teamname in teamnames:
            f.write(str(count)+','+teamname.text+','+points[count-1].text+'\n')
            count+=1
    f.close()

def get_player(rank_url,filename=None):
    #hltv没什么api，抓取也不太友好，现在只有top30队伍的队员信息
    rep = get_html(rank_url)
    soup = BeautifulSoup(rep.content, "lxml")
    temp = soup.find_all('a')
    if filename == None:
        filename = 'player' + time.strftime('%Y-%m-%d %H.%M.%S', time.localtime(time.time())) + '.csv'
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('姓名' + ',' + '年龄' + ',' + 'Rating2.0' + ',' + '每回合杀敌' + ',' + '选手爆头率' + ',' + '每回合死亡' + ',' + '每回合贡献值' + '\n')
    for link in temp:
        if '/player/' in str(link.get('href')):
            data = []
            new_url = root_url + str(link.get('href'))
            rep1 = get_html(new_url)
            soup1 = BeautifulSoup(rep1.content, "lxml")
            # 获取选手名字
            name = soup1.find_all(name='h1', attrs={"class": "playerNickname"})
            if name==[]:
                name=soup1.find_all(name='h1', attrs={"class": "player-nick text-ellipsis"})
            data.append(name[0].text)
            # 获取选手年龄
            age = soup1.find_all(name='span', attrs={"class": "listRight"})
            data.append(str(age[0].text).strip().split(' ')[0])
            # 获取选手当前队伍
            # 获取选手rating 2.0
            statsval = soup1.find_all(name='span', attrs={"class": "statsVal"})
            data.append(statsval[0].text)
            # 获取选手每回合杀敌
            data.append(statsval[1].text)
            # 获取选手爆头率
            data.append(statsval[2].text)

            # 获取选手每回合死亡
            data.append(statsval[4].text)
            # 获取选手每回合贡献值
            data.append(statsval[5].text)

            with open(filename, 'a') as f:
                for j in data:
                    f.write(j + ',')
                f.write('\n')
            f.close()
            print(data)


if __name__=="__main__":
    root_url='https://www.hltv.org/'

    #测试抓取比赛结果
    # result_url=root_url+'results'
    # get_result()
    # match_url=root_url+'matches'
    #测试抓取队伍排名结果
    # rank_url='https://www.hltv.org/ranking/teams/2019/march/11'
    # get_rank(rank_url)
    #测试抓取选手结果
    rank_url='https://www.hltv.org/ranking/teams/'
    get_player(rank_url)
    #print (time.strftime('%Y-%m-%d %H.%M.%S',time.localtime(time.time())))
