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
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "email")))

        username_input = driver.find_element_by_id('email')
        password_input = driver.find_element_by_id('password')
        login_button = driver.find_element_by_xpath('//*[@id="main_wraper"]/div/div[8]/a')

        username_input.send_keys(username)
        password_input.send_keys(password)
        login_button.click()
        sign_model_xpath = '//*[@id="container"]/div/div[1]/div[2]/div[1]/a[3]'
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, sign_model_xpath)))
        sign_model = driver.find_element_by_xpath(sign_model_xpath)
        sign_model.click()
        driver.save_screenshot('./haha1.png')
        sleep(10)
        frame_element = driver.find_element_by_xpath('//*[@id="main_attend"]/iframe')
        driver.switch_to.frame(frame_element)
        driver.save_screenshot('./haha.png')
        btn_xpath = '//div[contains(@class, "clockbtn")]'
        attend_btn = driver.find_element_by_xpath(btn_xpath)
        attend_btn.click()
    except:
        raise
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


def send_self_email(email_address, password, content, username=''):
    import smtplib
    from email.mime.text import MIMEText
    _user = email_address
    _pwd = password
    _to = email_address

    msg = MIMEText(content)
    msg["Subject"] = '%s jingoal sign failed' % username + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    msg["From"] = _user
    msg["To"] = _to

    try:
        s = smtplib.SMTP_SSL("smtp.qq.com", 465)
        s.login(_user, _pwd)
        s.sendmail(_user, _to, msg.as_string())
        s.quit()
    except smtplib.SMTPException, e:
        pass


if __name__ == '__main__':
    # 脚本每天8:53 / 6:40 运行
    parser = argparse.ArgumentParser(description=u'JinGoal Sign in/out script.')
    parser.add_argument('username', metavar='<USERNAME>', type=str, help='JinGoal username')
    parser.add_argument('password', metavar='<PASSWORD>', type=str, help='JinGoal password')
    parser.add_argument('-e', dest='email', default='', help='error email address')
    parser.add_argument('-ep', dest='email_pass', default='', help='error email password (必须是授权码)')
    args = parser.parse_args()
    try:
        if today_is_holiday():
            print u'today is holiday'
        else:
            wait_sec = random.randint(0, 60 * 2)
            sleep(wait_sec)
            error_times = 0
            success = False
            while error_times < 3 and not success:
                try:
                    jingoal_sign(args.username, args.password)
                    success = True
                except:
                    error_times += 1
    except:
        import traceback

        if not (args.email and args.email_pass):
            traceback.print_exc()
        else:
            error_str = traceback.format_exc()
            send_self_email(args.email, args.email_pass, error_str, username=args.username)
