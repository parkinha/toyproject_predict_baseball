#iot application
from bs4 import BeautifulSoup
import urllib.request as req
import pandas as pd
import tensorflow as tf
import numpy as np
tf.random.set_seed(777)#set_random_seed(777)
x_data = []
pd_count=0
start_year=2014
y_count=2023-start_year

x_pd = pd.DataFrame(columns=("war", "score", "hit", "homerun", "runbat", "OPS"))

for w in range(y_count-1):
    year=start_year+w
    print(year)

    url ="http://www.statiz.co.kr/stat.php?opt=0&sopt=0&re=0&ys="+str(year)+"&ye="+str(year)+"&se=0&te=&tm=&ty=0&qu=auto&po=0&as=&ae=&hi=&un=&pl=&da=1&o1=WAR_ALL_ADJ&o2=TPA&de=1&lr=5&tr=&cv=&ml=1&sn=30&si=&cn="

    # urlopen()으로 데이터 가져오기, 에러가 나도 진행하기위해 try, except문 사용
    try:
        res = req.urlopen(url)
    except:
        print("500")
        
    # BeautifulSoup으로 분석하기 
    soup = BeautifulSoup(res, "html.parser")
    
    #페이지에서 보는 코드와 soup로 추출한 코드가 달라 직접 출력해서 태그를 체크했다.
    #print(soup)
    
    # 원하는 데이터 추출하기 
    a_list = soup.select("#mytable > tr")
    #print(len(a_list))
    
    i=0
    j=0
    for a in a_list:
        i = i+1
        #8개 구단 내에서의 정보
        if i>7 and i<16:
            #print(a)
            b_list = a.select("td")
            #print(b_list)
            j=0
            for b in b_list:
                j = j+1
                #여러가지 데이터중 필요한 war, 득점, 안타, 홈런, 타점, OPS 정보를 얻기위한 코드이다.
                if j==4 or j==8 or j==9 or j==12 or j==14 or j==27:
                    c_list = b.select("font > span")
                    for c in c_list:
                        #print(c.string)
                        x_data.append(c.string)
                        if j==27:
                            x_data[5] = x_data[5].split('.')[1];
                    
            #print(x_data)
            x_pd.loc[pd_count] = [x_data[q] for q in range(6)]
            pd_count = pd_count+1   
            x_data=[]


print(x_pd)

#추출한 데이터로 작성한 DataFrame을 csv파일로 저장
x_pd.to_csv(r'C:\Users\Administrator\iotapplication_project\baseball_data.csv', mode='w', header=True)


import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'


xy = np.loadtxt(r'C:\Users\Administrator\iotapplication_project\baseball_data.csv', delimiter=',', dtype=np.float32,skiprows=0)

x_data = xy[:, 0:-1]
y_data = xy[:, [-1]]

X = tf.placeholder(tf.float32, shape=[None, 6])
Y = tf.placeholder(tf.float32, shape=[None, 1])

W = tf.Variable(tf.random_normal([6, 1]), name='weight')
b = tf.Variable(tf.random_normal([1]), name='bias')

hypothesis = tf.matmul(X, W) + b

cost = tf.reduce_mean(tf.square(hypothesis - Y))

optimizer = tf.train.GradientDescentOptimizer(learning_rate=0.01)
train = optimizer.minimize(cost)

sess = tf.Session()

sess.run(tf.global_variables_initializer())

for step in range(1000001):
    cost_val, hy_val, _ = sess.run(
        [cost, hypothesis, train], feed_dict={X: x_data, Y: y_data})
    if step % 10000 == 0:
        print(step, "Cost: ", cost_val)
    if step % 100000 == 0:
        print("\nPrediction:\n", hy_val)