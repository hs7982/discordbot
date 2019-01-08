import discord  
import requests 
from bs4 import BeautifulSoup as bs
import pymysql

import general_settings

import random
import re
import sys, os
import time
import datetime

Setting = general_settings.Settings()

def mysql_conn():
    try:
        global conn, curs
        # db연결
        conn = pymysql.connect(host="localhost", user="root", passwd=Setting.db_passwd, db="jungang_meal", charset='utf8')
        #curs생성
        curs = conn.cursor()
    except:
        print("db연결 중 오류가 발생했습니다. mysql_del")


def mysql_lunch(day):
    mysql_conn()
    sql=("""SELECT meal FROM `week_meal_2`""")
    curs.execute(sql)
    n = 0
    while n < day+1:
        lunch = curs.fetchone()
        n = n+1
    conn.commit()
    conn.close()

    return lunch

    

def mysql_dinner(day):
    mysql_conn()
    sql=("""SELECT meal FROM `week_meal_3`""")
    curs.execute(sql)
    n = 0
    while n < day+1:
        dinner = curs.fetchone()
        n = n+1
    conn.commit()
    conn.close()

    return dinner


def log_db_msg(ch_name, ch_id, author_name, author_id, content):
    # db연결
    conn = pymysql.connect(host="localhost", user="root", passwd=Setting.db_passwd, db="discordbot", charset='utf8')

    #curs생성
    curs = conn.cursor()

    #데티어 생성
    now = str(datetime.datetime.now())
    sql=("""INSERT INTO chat_log (time, channel_name, channel_id, author_name, author_id, content) VALUES ('"""+ now + "', '" + ch_name + "', '" + ch_id + "', '" + author_name + "', '" + author_id + "', '" + str(content) + """')""")
    curs.execute(sql)
    conn.commit()
    conn.close()
        

print("lodng...")

app = discord.Client() 

# 이벤트영역

@app.event
async def on_ready():
    print(app.user.name, "(%s)" % app.user.id)
    await app.change_presence(activity=discord.Game(name="사용법은 '!help'로 확인★", type=0))



# 메시지
@app.event
async def on_message(message):
    #채팅창 메시지 수신

    log_db_msg(str(message.channel), str(message.channel.id),
        str(message.author.name), str(message.author.id),
        str(message.content))

    if message.author.id == app.user.id: return   

    #관리자모드
    if "!!검색제외" == message.content.split(" ")[0]:
        await app.trigger_typing(message.channel)
        try:
            if Setting.adminid == message.author.id or Setting.server_admin == message.author.id:
                f = open("black_list_search.txt", 'a+t')
                text = message.content.split(" ")[1:]
                black = " ".join(text)
                f.write(black+"\n")
                print("검색어 블랙리스트 추가됨")
                embed = discord.Embed(title=" :wrench: 관리자모드: 검색제외", description="<@"+message.author.id+"> **제외 처리완료**", color=0x00ff00)
                await app.send_message(message.channel, embed=embed)
                del text, f
            else:
                print('\n등록된 관리자가 아닙니다, 관리자모드 취소합니다!\n')
                embed = discord.Embed(title=" :wrench: 관리자모드: 등록된 관리자가 아닙니다!", description="<@"+message.author.id+"> 이 기능은 관리자만 사용할 수 있습니다.", color=0xFF4500)
                await app.send_message(message.channel, embed=embed)
        except:
            embed = discord.Embed(title="오류", description="<@"+message.author.id+"> 검색어 블랙리스트 파일 처리중 오류가 발생하였습니다.", color=0xFF4500)
            await app.send_message(message.channel, embed=embed)
            
        

    if "!지우개" == message.content.split(" ")[0]:
        if Setting.adminid == message.author.id or Setting.server_admin == message.author.id:

            try:
                await app.trigger_typing(message.channel)
                num = int(message.content.split(" ")[1])
                if num<100:
                    deleted = await app.purge_from(message.channel, limit=num+1)
                    embed = discord.Embed(title="지우개", description="<@"+message.author.id+"> 명령어를 정상적으로 실행하였습니다.\n{}개의 메시지를 삭제하였습니다.".format(len(deleted)-1), color=0x00ff00)
                    await app.send_message(message.channel, embed=embed)
                else:
                    embed = discord.Embed(title="오류", description="<@"+message.author.id+"> 삭제할 메시지는 100개 이상일 수 없습니다.", color=0xFF4500)
                    await app.send_message(message.channel, embed=embed)

            except discord.errors.Forbidden:
                embed = discord.Embed(title="권한이 부족합니다!", description="<@"+message.author.id+"> 이 기능을 이용하기 위해선 봇이 **메시지 관리**권한이 필요합니다.", color=0xFF4500)
                await app.send_message(message.channel, embed=embed)
            except ValueError:
                embed = discord.Embed(title="오류", description="<@"+message.author.id+"> `[삭제할 메시지 개수]`는 정수로 이루어져야 합니다.", color=0xFF4500)
                await app.send_message(message.channel, embed=embed)
            except discord.errors.HTTPException as error:
                print (error)
                embed = discord.Embed(title="오류", description="<@"+message.author.id+"> 최근 15일 이내의 메시지만 삭제할 수 있습니다.\n", color=0xFF4500)
                embed.add_field(name="오류코드:", value=error, inline=False)
                await app.send_message(message.channel, embed=embed)
            except:
                embed = discord.Embed(title="명령어를 다시 확인해보세요!", description="", color=0xFF4500)
                embed.add_field(name="아래의 방법을 확인해보세요.", value="<@"+message.author.id+"> 명령어 형식이 올바른지 확인해주세요.\n명령어는 `!지우개` `[삭제할 메시지 개수]` 로 이루어져야 합니다.", inline=False)
                await app.send_message(message.channel, embed=embed)
        else:
            embed = discord.Embed(title="관리자 권한이 없습니다.", description="<@"+message.author.id+"> 관리자에게 권한을 부여받아야 이용할 수 있습니다.", color=0xFF4500)
            await app.send_message(message.channel, embed=embed)

    #단순 명령어
    if "안녕" == message.content or "ㅎㅇ" == message.content:
        await app.trigger_typing(message.channel)
        msg=['안녕하세요 :)', '안녕안녕:wave:', '하이욤 :raised_hands: ']
        await app.send_message(message.channel, random.choice(msg))
        print("[송신] 채널: %s(%s) | 명령어: %s | 메시지: %s" %(message.channel, message.channel.id[:5], message.content, msg))
        del msg
        


    if "!명령어" == message.content:
        await app.trigger_typing(message.channel)
        embed = discord.Embed(title="도움말", description="<@"+message.author.id+"> 사용가능한 명령어입니다 :wink: \n```[일반]\n!급식, !검색, !나무위키, !지우개, !정리, !봇초대\n\n"
        +"[뮤직봇]\n!help, !np, !권한, !볼륨, !스킵, !스트리밍, !시작, !연결, !연결종료, !일시중지, !재생, !재생목록, !추가```", color=0x00ff00)
        
        await app.send_message(message.channel, embed=embed)
        print("[송신] 채널: %s(%s) | 명령어: %s | 메시지: 임베드메시지(명령어)" %(message.channel, message.channel.id[:5], message.content))

    if "<:bloodtrail:371160221478944768>" == message.content:
        await app.trigger_typing(message.channel)
        msg="블라드뚜레일 <:bloodtrail:371160221478944768> "
        await app.send_message(message.channel, msg)
        print("[송신] 채널: %s(%s) | 명령어: %s | 메시지: %s" %(message.channel, message.channel.id[:5], message.content, msg))
        del msg

    if "<:biblethump:371160644268851202>" == message.content:
        await app.trigger_typing(message.channel)
        msg="비불쌈푸 <:biblethump:371160644268851202> "
        await app.send_message(message.channel, msg)
        print("[송신] 채널: %s(%s) | 명령어: %s | 메시지: %s" %(message.channel, message.channel.id[:5], message.content, msg))
        del msg

    if "!나무위키" == message.content.split(" ")[0]:
        await app.trigger_typing(message.channel)
        text = message.content.split(" ")[1:]
        serch = "%20".join(text)
        embed = discord.Embed(title="나무위키", description="<@"+message.author.id+"> 나무위키에서 찾아봤어요!\n"+"https://namu.wiki/go/"+serch, color=0x00ff00)
        await app.send_message(message.channel, embed=embed)
        print("[송신] 채널: %s(%s) | 명령어: %s | 메시지: 임베트메시지[나무위키]" %(message.channel, message.channel.id[:5], message.content))
        del serch, text

    # Google 이미지 보내기
    if "!검색" == message.content.split(" ")[0]:
        await trigger_typing(message.channel)
        text = message.content.split(" ")[1:]
        group = " ".join(text)
        black_list=[]
        try:
            f = open("black_list_search.txt", 'r')
            while True:
                line = f.readline()
                if not line: break
                black_list.append(line[:-1])
        except:
            embed = discord.Embed(title="오류", description="<@"+message.author.id+"> 검색어 블랙리스트 파일을 불러올 수 없습니다.", color=0xFF4500)
            await app.send_message(message.channel, embed=embed)

        if group in black_list:
            print("블랙리스트 검색어: 처리하지 않습니다.")
            embed = discord.Embed(title="검색할 수 없습니다!", description="<@"+message.author.id+"> 관리자에 의하여 이 검색어는 처리할 수 없습니다.", color=0xFF4500)
            await app.send_message(message.channel, embed=embed)
        else:
            try:
                print("google이미지 검색: "+group)
                google_data = requests.get("https://www.google.co.kr/search?q=" + group + "&dcr=0&source=lnms&tbm=isch&sa=X")
                soup = bs(google_data.text, "html.parser")
                imgs = soup.find_all("img")

                await app.send_message(message.channel, random.choice(imgs[1:])['src'])
                print("[송신] 채널: %s(%s) | 명령어: %s | 메시지: %s" %(message.channel, message.channel.id[:5], message.content, "https://www.google.co.kr/search?q=" + group + "&dcr=0&source=lnms&tbm=isch&sa=X"))
                del group, google_data, soup, imgs
            except:
                embed = discord.Embed(title="오류", description="<@"+message.author.id+"> 명령어를 처리할 수 없습니다!", color=0xFF4500)
                embed.add_field(name="아래의 방법을 확인해보세요.", value="명령어 형식이 올바른지 확인해주세요.\n명령어는 `!검색` `[검색어]`로 이루어져야 합니다.", inline=False)
                await app.send_message(message.channel, embed=embed)

        del line, f, black_list, text

    if "!급식" == message.content.split(" ")[0]:
        await app.trigger_typing(message.channel)
        try:
            dt = datetime.datetime.now()
        
            if "오늘" == message.content.split(" ")[1]:
                day = dt.weekday()
                if day == 6:
                    lunch = mysql_lunch(0)
                    dinner = mysql_dinner(0)
                else:
                    lunch = mysql_lunch(day+1)
                    dinner = mysql_dinner(day+1)
                embed = discord.Embed(title="급식", description="<@"+message.author.id+"> 오늘의 식단표 입니다.\n\n**[중식]**\n"+str(lunch[0])+"\n**[석식]**\n"+str(dinner[0]), color=0x00ff00)
                await app.send_message(message.channel, embed=embed)
        
            elif "내일" == message.content.split(" ")[1]:
                day = dt.weekday()
                if day == 6:
                    lunch = mysql_lunch(1)
                    dinner = mysql_dinner(1)
                elif day == 5:
                    lunch = mysql_lunch(0)
                    dinner = mysql_dinner(0)
                else:
                    lunch = mysql_lunch(day+2)
                    dinner = mysql_dinner(day+2)
                embed = discord.Embed(title="급식", description="<@"+message.author.id+"> 내일의 식단표 입니다.\n\n**[중식]**\n"+str(lunch[0])+"\n**[석식]**\n"+str(dinner[0]), color=0x00ff00)
                await app.send_message(message.channel, embed=embed)

            elif "일" == message.content.split(" ")[1]:
                lunch = mysql_lunch(0)
                dinner = mysql_dinner(0)
                embed = discord.Embed(title="급식", description="<@"+message.author.id+"> 일요일의 식단표 입니다.\n\n**[중식]**\n"+str(lunch[0])+"\n**[석식]**\n"+str(dinner[0]), color=0x00ff00)
                await app.send_message(message.channel, embed=embed)        

            elif "월" == message.content.split(" ")[1]:
                lunch = mysql_lunch(1)
                dinner = mysql_dinner(1)
                embed = discord.Embed(title="급식", description="<@"+message.author.id+"> 월요일의 식단표 입니다.\n\n**[중식]**\n"+str(lunch[0])+"\n**[석식]**\n"+str(dinner[0]), color=0x00ff00)
                await app.send_message(message.channel, embed=embed)  
        
            elif "화" == message.content.split(" ")[1]:
                lunch = mysql_lunch(2)
                dinner = mysql_dinner(2)
                embed = discord.Embed(title="급식", description="<@"+message.author.id+"> 화요일의 식단표 입니다.\n\n**[중식]**\n"+str(lunch[0])+"\n**[석식]**\n"+str(dinner[0]), color=0x00ff00)
                await app.send_message(message.channel, embed=embed)  
            
            elif "수" == message.content.split(" ")[1]:
                lunch = mysql_lunch(3)
                dinner = mysql_dinner(3)
                embed = discord.Embed(title="급식", description="<@"+message.author.id+"> 수요일의 식단표 입니다.\n\n**[중식]**\n"+str(lunch[0])+"\n**[석식]**\n"+str(dinner[0]), color=0x00ff00)
                await app.send_message(message.channel, embed=embed)              

            elif "목" == message.content.split(" ")[1]:
                lunch = mysql_lunch(4)
                dinner = mysql_dinner(4)
                embed = discord.Embed(title="급식", description="<@"+message.author.id+"> 목요일의 식단표 입니다.\n\n**[중식]**\n"+str(lunch[0])+"\n**[석식]**\n"+str(dinner[0]), color=0x00ff00)
                await app.send_message(message.channel, embed=embed)  
            
            elif "금" == message.content.split(" ")[1]:
                lunch = mysql_lunch(5)
                dinner = mysql_dinner(5)
                embed = discord.Embed(title="급식", description="<@"+message.author.id+"> 금요일의 식단표 입니다.\n\n**[중식]**\n"+str(lunch[0])+"\n**[석식]**\n"+str(dinner[0]), color=0x00ff00)
                await app.send_message(message.channel, embed=embed)  

            elif "토" == message.content.split(" ")[1]:
                lunch = mysql_lunch(6)
                dinner = mysql_dinner(6)
                embed = discord.Embed(title="급식", description="<@"+message.author.id+"> 토요일의 식단표 입니다.\n\n**[중식]**\n"+str(lunch[0])+"\n**[석식]**\n"+str(dinner[0]), color=0x00ff00)
                await app.send_message(message.channel, embed=embed)
            
            else:
                embed = discord.Embed(title="오류", description="<@"+message.author.id+"> 명령어를 처리할 수 없습니다!", color=0xFF4500)
                embed.add_field(name="아래의 방법을 확인해보세요.", value="명령어 형식이 올바른지 확인해주세요.\n`오늘, 내일, 월, 화, 수, 목, 금, 토, 일`만 사용할 수 있습니다.", inline=False)
                await app.send_message(message.channel, embed=embed)

        except IndexError:
            day = dt.weekday()
            if day == 6:
                lunch = mysql_lunch(0)
                dinner = mysql_dinner(0)
            else:
                lunch = mysql_lunch(day+1)
                dinner = mysql_dinner(day+1)
            embed = discord.Embed(title="급식", description="<@"+message.author.id+"> 오늘의 식단표 입니다.\n\n**[중식]**\n"+str(lunch[0])+"\n**[석식]**\n"+str(dinner[0]), color=0x00ff00)
            await app.send_message(message.channel, embed=embed)
        
        except:
            embed = discord.Embed(title="오류", description="<@"+message.author.id+"> 오류가 발생했습니다!", color=0xFF4500)
            embed.add_field(name="아래의 방법을 확인해보세요.", value="명령어 형식이 올바른지 확인해주세요.\n`오늘, 내일, 월, 화, 수, 목, 금, 토, 일`만 사용할 수 있습니다.", inline=False)
            await app.send_message(message.channel, embed=embed)

# 봇 실행
app.run(Setting.token)

executable = sys.executable
args = sys.argv[:]
args.insert(0, sys.executable)
print('\n\n대기시간 초과로 종료되었습니다. 연결을 재시도합니다.\n\n')
os.execvp(executable, args)

#봇 종료
sys.exit()