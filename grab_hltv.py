#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Disallow: /stats
import time
import random
import string
import requests
import numpy as np
from bs4 import BeautifulSoup
import optparse
import calendar
version='1.0.0'
date_now=time.strftime('%Y-%m-%d', time.localtime(time.time()))
time_now=time.strftime('%Y-%m-%d %H.%M.%S', time.localtime(time.time()))
def get_html(url,data=None):

    header={
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.235'
    }
    #设定超时时间，防止被网站认为是爬虫
    timeout=random.choice(range(20,50))#80,180
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

def get_result(start_date=None,end_date=None,stars=None,filename=None):
    #四个参数：开始日期 结束日期 比赛星级  文件名称
    root_url='https://www.hltv.org/'
    if filename == '':
        filename = 'result' + time_now + '.csv'
    if start_date=='':
        start_date='2019-03-14'
    if end_date=='':
        end_date=date_now
    offset=0
    number=0
    total_page=1000000
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('比赛编号'+','+'比赛日期'+','+'比赛名称'+','+'队伍1'+','+'队伍2'+','+'大比分'+','+'胜利队伍'+','+('地图'+','+'比分'+',')*3+'\n')
    while total_page>0:
        result_url='https://www.hltv.org/results?offset={0}&startDate={1}&endDate={2}'.format(str(offset),str(start_date),str(end_date))
        if stars!='':
            result_url=result_url+'&'+str(stars)
        #获取比赛综合页面
        rep=get_html(url=result_url)
        soup = BeautifulSoup(rep.content, "lxml")
        if total_page==1000000:
            total_page_label=soup.find_all(name='span',attrs={"class":"pagination-data"})[0].text
            total_page = int(total_page_label.strip().split(' ')[-1])
            total_page=int(total_page/100)
        total_page=total_page-1
        offset=offset+100
        for link in soup.find_all('a'):
            if '/matches/' in str(link.get('href')):
                time1=time.time()
                data=[]


                new_url=root_url+str(link.get('href'))
                print (new_url)
                temp = str(link.get('href')).split('/')
                #获取比赛详细数据
                rep1=get_html(url=new_url)
                soup1 = BeautifulSoup(rep1.content, "lxml")
                #获取比赛编号
                data.append(temp[2])
                #获取比赛日期
                date=soup1.find_all(name='div',attrs={"class":"date"})
                data.append(date[0].text)
                date1 = time.mktime(time.strptime(start_date, '%Y-%m-%d'))
                date2 = time.mktime(time.strptime(end_date,'%Y-%m-%d'))
                temp=str(date[0].text).split(' ')
                print (temp)
                date3_temp = temp[-1] + '-' + str(list(calendar.month_name).index(temp[-2])) + '-' + temp[0][:-2]
                date3 = time.mktime(time.strptime(date3_temp,'%Y-%m-%d'))
                if date3>date2 or date3<date1:
                    break
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
                    if tie==[]:
                        if count<=int(won[0].text)+int(lost[0].text):
                            if 'default' in i.text.lower():
                                break
                            if int(map_won[count].text)<0 or int(map_lost[count].text)<0:
                                break
                            map_result=str(map_won[count].text)+'::'+str(map_lost[count].text)
                            data.append((str(map_result)))
                            count += 1
                    else:
                        if count<=int(tie[1].text)+int(tie[1].text):
                            if 'default' in i.text.lower():
                                break
                            if int(map_won[count].text)<0 or int(map_lost[count].text)<0:
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
                number=number+1
                time2=time.time()
                print(time2-time1)
    return number

def get_rank(rank_url=None,filename=None):
    if rank_url=='':
        rank_url='https://www.hltv.org/ranking/teams/2019/march/11'
    url_split=rank_url.split('/')
    if filename=='':
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
    return count-1
def get_player(rank_url=None,filename=None):
    #hltv没什么api，抓取也不太友好，现在只有top30队伍的队员信息
    if rank_url=='':
        rank_url='https://www.hltv.org/ranking/teams/2019/march/11'
    if filename == '':
        filename = 'player' + time.strftime('%Y-%m-%d %H.%M.%S', time.localtime(time.time())) + '.csv'
    rep = get_html(rank_url)
    soup = BeautifulSoup(rep.content, "lxml")
    temp = soup.find_all('a')
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('姓名' + ',' + '年龄' + ',' + 'Rating2.0' + ',' + '每回合杀敌' + ',' + '选手爆头率' + ',' + '每回合死亡' + ',' + '每回合贡献值' + '\n')
    count=0
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
            count=count+1
        return count

def welcome():
    print('欢迎来到csgo预测系统')
    input('按回车键继续...')

def main():
    while True:
        print('欢迎来到csgo预测系统，当前版本: '+version)
        print('请输入爬取的内容:')
        print('1.爬取比赛结果')
        print('2.爬取队伍排名')
        print('3.爬取选手信息')
        print('4.退出')
        print('本系统暂只支持以上功能，敬请谅解！')
        choose=input('请输入选项：')
        if choose=='1':
            time1=time.time()
            start_date=input('请输入开始日期（默认为2019-03-14）：')
            end_date=input('请输入结束日期（默认为当前日期）：')
            star=input('请输入比赛星级（默认为所有比赛）：')
            filename=input('请输入输出文件名（默认由系统自动生成）：')
            print('数据正在抓取中，请不要打开或者关闭输出的文件')
            count=get_result(start_date=start_date,end_date=end_date,stars=star,filename=filename)
            time2=time.time()
            print('数据抓取完成，共计'+str(count)+'条数据,'+'耗时'+str(int(time2-time1))+'s')
        elif choose=='2':
            time1=time.time()
            rank_url=input('请输入排名url（默认为https://www.hltv.org/ranking/teams/2019/march/11）')
            filename=input('请输入输出文件名（默认由系统自动生成）：')
            print('数据正在抓取中，请不要打开或者关闭输出的文件')
            count=get_rank(rank_url=rank_url,filename=filename)
            time2=time.time()
            print('数据抓取完成，共计'+str(count)+'条数据,'+'耗时'+str(int(time2-time1))+'s')
        elif choose=='3':
            time1 = time.time()
            rank_url = input('请输入排名url（默认为https://www.hltv.org/ranking/teams/2019/march/11）')
            filename = input('请输入输出文件名（默认由系统自动生成）：')
            print('数据正在抓取中，请不要打开或者关闭输出的文件')
            count = get_player(rank_url=rank_url, filename=filename)
            time2 = time.time()
            print('数据抓取完成，共计' + str(count) + '条数据,' + '耗时' + str(int(time2 - time1)) + 's')
            get_player()
        elif choose=='4':
            break
        else:
            print ('请重新输入选项')

if __name__=="__main__":

    # time1=time.time()
    # url='https://www.hltv.org//matches/2331754/astralis-vs-nip-ecs-season-7-europe-week-1'
    # rep=get_html(url=url)
    # soup = BeautifulSoup(rep.content, "lxml")
    # test = soup.find_all(name='div', attrs={"class": "date"})
    # print (test[0].text)
    # temp=[]
    # temp=test[0].text.split(' ')
    # a=temp[-1]+'-'+str(list(calendar.month_name).index(temp[-2]))+'-'+temp[0][:-2]
    # print (a)
    # time2=time.time()
    # print(str(time2-time1)+'s')

    welcome()
    main()
    # print ('test')
    # parser = optparse.OptionParser("usage%prog " + "-f <zipfile> -d <dictionary>")
    # parser.add_option('-f', dest='zname', type='string',help='specify zip file')
    # parser.add_option('-d', dest='dname', type='string',help='specify dictionary file')
    # (options, args) = parser.parse_args()
    #root_url='https://www.hltv.org/'
    #测试抓取比赛结果
    # result_url=root_url+'results'
    # get_result()
    # match_url=root_url+'matches'
    #测试抓取队伍排名结果
    # get_rank(rank_url)
    #测试抓取选手结果
    # rank_url='https://www.hltv.org/ranking/teams/'
    # get_player(rank_url)
    #print (time.strftime('%Y-%m-%d %H.%M.%S',time.localtime(time.time())))
