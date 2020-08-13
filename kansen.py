import pygame
from pygame.locals import *
import sys
import random
import csv
import datetime

#定数
winX = 1500              # 広さ
winY = 1200
Speed = 10              # 最初の動き
Population = 300        # 人数
Healing_time = 300      # 感染してから治るまでのtick数(1tick = 1hr)
End_time = 2400         # 時間(1500tick)
hr_of_day =24           # 24tick=1day
Medical_resoueces = 10  # 医療資源
Critical_rate = 30      # 重症化率
Dt_now = datetime.datetime.now()  # ファイル名に使う
#色
Infect = (255, 150, 100)
Heavy = (255, 55, 55)
Danger = (255, 5, 5)
Dead = (5, 5, 5)
Safe = (10, 10, 255)
Recovered = (10,155,255)

class man():
    def __init__(self, id):
        self.px = random.randint(0, winX)
        self.py = random.randint(0, winY)
        self.vx = random.randint(Speed*-1, Speed)
        self.vy = random.randint(Speed*-1, Speed)
        self.state = 0
        self.id = id
        self.tick = 0
        self.medicated = 0 #重症時　1:入院 0:入院できない
    def update(self, mms, ag, spd):
        #print("total_critical=",total_critical)
        #移動
        if self.state == 4 or (self.state == 3 and self.medicated ==1 ):  # 死んでいる場合　入院できている
            pass # do nothing
        else:
            self.px += self.vx
            self.py += self.vy
            self.vx = random.randint(spd*-1, spd)
            self.vy = random.randint(spd*-1, spd)
        #状態遷移
        if self.state == 0: #未感染者
            #print("total_critical=",total_critical)
            #接近判定　→　感染
            for mm in mms:
                if self.id != mm.id and mm.state == 1:  
                    if self.px-10 < mm.px <self.px+10:
                        if self.py-10 < mm.py <self.py+10: 
                            #print("xys mm.id=",mm.id,"  self.id=",self.id)
                            # 感染した
                            #print("感染した")
                            if random.randint(0,100) < Critical_rate:
                                print("重症だ！")
                                self.state = 3  # 重症
                                #print("重症患者数＝",ag.ct3)
                                if ag.ct3 <  Medical_resoueces:
                                    print("入院できた！")
                                    self.medicated = 1
                                else:    
                                    print("医療崩壊！！")
                                    self.medicated = 0
                            else:    
                                #print("軽微")
                                self.state = 1  # 軽微
        elif self.state == 1:        #感染者　自然治癒 の判定       
            self.tick += 1
            if self.tick >= Healing_time:
                self.state = 2
        elif self.state == 2:  # 治癒　
            pass # do nothing
        elif self.state == 3:  # 重症患者の場合　
            self.tick += 1
            if self.tick >= Healing_time:
                #print("運命のとき　self.medicated=",self.medicated)
                if self.medicated == 1:  # 入院できている
                    if random.randint(0,100) < 20:#20%の確率で死ぬ
                        self.state = 4
                        print("病院で死亡")
                    else:#治癒
                        self.state = 2
                        print("治った！")
                else:  # 入院できてない
                    self.state = 4
                    print("野垂れ死")
        elif self.state == 4:  # 死んでいる場合　
            pass # do nothing


    def draw(self,screen):
        if self.state == 0:#未感染
            pygame.draw.circle(screen, Safe, (self.px, self.py),5)
        elif self.state == 1:#感染
            pygame.draw.circle(screen, Infect, (self.px, self.py),5)
        elif self.state == 2:#抗体獲得　治癒
            pygame.draw.circle(screen, Recovered, (self.px, self.py),5)
        elif self.state == 3:#重症
            if self.medicated == 1:
                pygame.draw.circle(screen, Heavy, (self.px, self.py),5)
            else: 
                pygame.draw.circle(screen, Danger, (self.px, self.py),8)
        elif self.state == 4:#死んでいる
            pygame.draw.circle(screen, Dead,(self.px, self.py),7)
        
#集計
class aggregage():
    def __init__(self):
        #村人がいまどの状態にある人が何人イルカ（ステージ0-5　→　ct0-5）
        self.ct0 = 0 #state=0の集計用（以下同様）
        self.ct1 = 0 #感染
        self.ct2 = 0 #抗体獲得　治癒
        self.ct3 = 0 #重症 (入院中＋非入院)
        self.ct4 = 0 #死んでいる
        self.ct3a = 0 #重症 (入院中)　　　

        # グラフエリア
        self.x0=100
        self.y0=500
        self.wx=600
        self.wy=100
        self.max_x= int(End_time/hr_of_day) +1
        self.max_y=300
        self.gr = [[0,0,0,0,0,0] for i in range(self.max_x)]
        # End_time = 1500         # 時間(1500tick)
        # hr_of_day =24           #24tick=1day

    def count(self, mms):
        self.ct0 = 0 # state=0のクリア（以下同様）
        self.ct1 = 0 #感染
        self.ct2 = 0 #抗体獲得　治癒
        self.ct3 = 0 #重症 (入院中＋非入院)
        self.ct4 = 0 #死んでいる
        self.ct3a = 0 #重症 (入院中＋非入院)

        for mm in mms:  # 集計開始　
            #集計
            if mm.state == 0:
                self.ct0 += 1
            elif mm.state == 1:
                self.ct1 += 1
            elif mm.state == 2:
                self.ct2 += 1
            elif mm.state == 3:
                self.ct3 += 1
                if mm.medicated == 1:
                    self.ct3a += 1
            elif mm.state == 4:
                self.ct4 += 1

    #結果の表示とセーブ            
    def draw(self, tc, writer): 
        if tc % hr_of_day == 0:
            days = int(tc/hr_of_day)
            #print(days,"day ",self.ct0,",",self.ct1,",",self.ct2,",",self.ct3,",",self.ct4)
            writer.writerow([days, self.ct0, self.ct1, self.ct2, self.ct3, self.ct4])
            self.gr[days] = [self.ct0, self.ct1, self.ct2, self.ct3, self.ct4, self.ct3a]
            #print(self.gr)

    #結果のグラフ表示 
    def graph(self, screen):
        pygame.draw.rect(screen, (255,0,0), Rect(self.x0,self.y0,self.wx,self.wy), 1)
        for i in range(0,self.max_x):
            #感染者
            my = self.gr[i][1]
            mx = i
            sx = mx/self.max_x
            sy = my/self.max_y
            gx = sx *  self.wx+self.x0
            gy = -sy * self.wy+ self.y0+ self.wy
            pygame.draw.line(screen, Infect, (gx, gy), (gx, self.y0 + self.wy), 4)

            #死んだ人
            my2 = self.gr[i][4]
            sy2 = my2/self.max_y
            gy2 = -sy2 * self.wy+ self.y0+ self.wy
            pygame.draw.line(screen, Dead, (gx+2, gy2), (gx+2, self.y0 + self.wy), 4)



def save_csv(writer):
    #条件書き込み
    writer.writerow(["広さ",winX,winY])
    writer.writerow(["動き",Speed])
    writer.writerow(["人数",Population])
    writer.writerow(["治るまで",Healing_time])
    writer.writerow(["終了まで",End_time])
    writer.writerow(["医療資源",Medical_resoueces])
    writer.writerow(["重症化率",Critical_rate])

    #列名書き込み
    writer.writerow(["", "未感染","感染","治癒","重症","死亡"])

def main():
    s2 = str(Dt_now).replace(":","").replace("-","")
    file_name = "c:\\udemy\\proj\\demo\\kansen\\data\\test" + s2 + ".csv"
    with open(file_name,"w",newline='',encoding='utf-8') as f:
        writer = csv.writer(f)
        save_csv(writer)
        pygame.init()                                 # Pygameの初期化
        screen = pygame.display.set_mode((winX, winY))  # 800*600の画面
        font = pygame.font.Font(None, 30)               # フォントの設定
        ck = pygame.time.Clock()
        tc=0    # この世界の時間
        #インスタンス作り
        mms = [man(i) for i in range(Population)]
        ag=aggregage() #集計用
        #最初の感染者（3人）
        mms[0].state = 1
        mms[10].state = 1
        mms[33].state = 1
        spd = Speed
        while (1):
            ck.tick(30) #1秒間で30フレームになるように33msecのwait
            screen.fill((255,255,255))  # 画面を白に
            #移動、状態遷移と描画
            for mm in mms:
                mm.update(mms, ag, spd)
                mm.draw(screen)
            #集計
            ag.count(mms)
            ag.draw(tc,writer)
            ag.graph(screen)
            #文字表示
            txt = font.render("Self-restraint:"+str((10-spd)*10)+"%", True, (5,5,255))   # 描画する文字列の設定
            screen.blit(txt, [20, 100])# 文字列の表示位置
            #残りの医療資源
            m_left = Medical_resoueces - ag.gr[int(tc/24)][5]
            if m_left>5:
                txt2 = font.render("Medical Resoueces(left):"+str(m_left), True, (5,5,5))   # 余裕
            else:
                txt2 = font.render("Medical Resoueces(left):"+str(m_left), True, (255,5,5))   # やばい
            screen.blit(txt2, [20, 130])# 文字列の表示位置
            pygame.display.update()     # 画面更新
            #世界の時間をすすめる
            tc+=1
            if tc > End_time:
                break
            # イベント処理
            for event in pygame.event.get():#イベントキューからキーボードやマウスの動きを取得
                if event.type == QUIT:      # 閉じるボタンが押されたら終了
                    pygame.quit()          # Pygameの終了(ないと終われない)
                    sys.exit()             #終了（ないとエラーで終了することになる）
                elif event. type == KEYDOWN: 
                    if event.key==K_LEFT:
                        if spd >= 2: 
                            spd -=2 #横方向の速度
                    elif event.key==K_RIGHT:
                        if spd <=10:
                            spd +=2 #横方向の速度
            #print(spd)            

if __name__ == "__main__":
    main()
