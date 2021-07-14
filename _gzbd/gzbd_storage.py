# -*- coding: utf-8 -*-
__author__ = "ShiinaClariS"

'''
四川卫健委冠状病毒数据存储
'''

from util import mysql_util
from datetime import datetime
from pandas import DataFrame
from pyecharts.faker import Faker
from pyecharts import options as opts
from pyecharts.charts import Bar, Bar3D, Line, Line3D, Pie


# 将数据存储到数据库
def save_mysql(all_data):
    # mysql 准备一张表来保存数据
    conn, cur = None, None
    try:
        conn, cur = mysql_util.get_connect_cursor()
        # 批量操作
        for gzbd in all_data:
            query_sql = "select * from xinji_coronavirus where date = '%s'" % gzbd["日期"]
            insert_sql = "insert into xinji_coronavirus (create_date, date, region, " \
                         "diagnosis, overseas_import, cure, death, therapy, observation) " \
                         "values ('%s', '%s', '%s', %s, %s, %s, %s, %s, %s)" % \
                         (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), gzbd["日期"],
                          gzbd["地区"], gzbd["确诊数"], gzbd["输入数"], gzbd["出院数"],
                          gzbd["死亡数"], gzbd["治疗数"], gzbd["观察数"])
            # 插入数据之前，以日期查询该数据是否存在，存在则不操作，不存在则插入
            temp = mysql_util.execute_query(cur, query_sql)
            if len(temp) == 0:
                mysql_util.execute_insert_update_delete(cur, insert_sql)
        mysql_util.commit_(conn)
    except Exception as e:
        print(e)
        mysql_util.rollback_(conn)
    finally:
        mysql_util.close_connect_cursor(conn, cur)


# 将数据保存到 csv 文件 ---- pandas
def save_csv(all_data):
    dataFrame_data = all_data
    column_list = ["id", "创建时间", "报告时间", "地区", "确诊数", "海外输入数", "治愈数", "死亡数", "治疗数", "观察数"]
    dataFrame = DataFrame(data=dataFrame_data, columns=column_list)
    dataFrame.to_csv(path_or_buf="gzbd.csv",
                     float_format=".2f", encoding="utf-8-sig")


# 将数据(确诊数、海外输入数、死亡数、治愈数)以图表的形式展示 ---- pyechart
# [{"确诊数":22, "z治愈数":11,...}]
# ((23,43,23),...)
def show_echarts(data):
    # x 轴显示日期 list
    # 图轨显示 确诊数、海外输入数、死亡数、治愈数 对应的 list
    # data:[('2021-06-10', 1044, 490, 1010, 3),...]
    x_list = []
    diagnosis_list = []
    overseas_import_list = []
    cure_list = []
    death_list = []
    for i in range(0, len(data)):
        gzbd = data[len(data) - 1 - i]
        x_list.append(gzbd[0])
        diagnosis_list.append(gzbd[1])
        overseas_import_list.append(gzbd[2])
        cure_list.append(gzbd[3])
        death_list.append(gzbd[4])
    print(x_list)
    print(diagnosis_list)
    print(overseas_import_list)
    print(cure_list)
    print(death_list)

    Line().add_xaxis(
        x_list
    ).add_yaxis(
        "确诊数",
        diagnosis_list,
        itemstyle_opts=opts.ItemStyleOpts(color=Faker.rand_color())
    ).add_yaxis(
        "海外输入数",
        overseas_import_list,
        itemstyle_opts=opts.ItemStyleOpts(color=Faker.rand_color())
    ).add_yaxis(
        "治愈数",
        cure_list,
        itemstyle_opts=opts.ItemStyleOpts(color=Faker.rand_color())
    ).add_yaxis(
        "死亡数",
        death_list,
        itemstyle_opts=opts.ItemStyleOpts(color=Faker.rand_color())
    ).set_global_opts(
        title_opts=opts.TitleOpts(title="冠状病毒图标", subtitle="最近七天数据")
    ).render("gzbd.html");


if __name__ == "__main__":
    # all_data = [{'确诊数': '1044', '输入数': '490', '出院数': '1010', '死亡数': '3', '治疗数': '31', '观察数': '405', '日期': '2021-06-10', '地区': '四川'}];
    # all_data = gzbd_spider.get_all_data();
    # save_mysql(all_data);
    # sql = "select id, DATE_FORMAT( create_date,'%Y-%m-%d %H:%i:%s'), date, region, diagnosis, overseas_import, cure, death, therapy, observation from xinji_coronavirus;";
    # data = mysql_util.execute_(sql);
    # print(data);
    # save_csv(data);
    sql = "select date, diagnosis, overseas_import, cure, death from xinji_coronavirus order by date desc limit 7;"
    data = mysql_util.execute_(sql)
    show_echarts(data)
