# coding=utf-8

#####################################
#
# IF THE GOD HAVE NO MERCY, THEN EVERYTHING TURNS INTO TRASH
# 天 地 不 仁 以 万 物 为 刍 狗
#
# requirements:
#   1. PhantomJS 2.1.1
#   2. selenium
#
#####################################
import argparse
import random
from time import sleep

import datetime

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


def has_page_load(driver):
    return driver.execute_script("return document.readyState") == 'complete'


jin_goal_login_url = ('https://sso.jingoal.com/#/login')
jin_goal_log_edit_url = ('https://web.jingoal.com/module/worklog/editEndSegment.do')
jin_goal_domain = 'web.jingoal.com'


def jingoal_sign(username, password):
    driver = webdriver.PhantomJS('phantomjs')
    driver.get(jin_goal_login_url)
    driver.set_window_size(1024, 1024)
    try:
        WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.ID, "email")))

        username_input = driver.find_element_by_id('email')
        password_input = driver.find_element_by_id('password')
        login_button = driver.find_element_by_xpath('//*[@id="main_wraper"]/div/div[8]/a')

        username_input.send_keys(username)
        password_input.send_keys(password)
        login_button.click()
        driver.save_screenshot('./haha.png')
        btn_xpath = '//*[@id="attend_table"]/div/div[contains(@class, "attend-btn")]/button'
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, btn_xpath)))
        attend_btn = driver.find_element_by_xpath(btn_xpath)
        attend_btn.click()
    except:
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()


def today_is_holiday():
    """ 判定今天是不是假期
    :return bool: 
    """
    day_str = datetime.datetime.now().strftime('%Y%m%d')
    resp = requests.get('http://www.easybots.cn/api/holiday.php', params={'d': day_str})
    resp = resp.json()
    return int(resp.values()[0])


if __name__ == '__main__':
    # 脚本每天8:53 / 6:40 运行
    if today_is_holiday():
        print u'today is holiday'
    else:
        parser = argparse.ArgumentParser(description=u'JinGoal Sign in/out script.')
        parser.add_argument('username', metavar='<USERNAME>', type=str, help='JinGoal username')
        parser.add_argument('password', metavar='<PASSWORD>', type=str, help='JinGoal password')
        args = parser.parse_args()
        wait_sec = random.randint(0, 60 * 6)
        sleep(wait_sec)
        jingoal_sign(args.username, args.password)
