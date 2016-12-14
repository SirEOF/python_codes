# coding=utf-8

#####################################
#
# IF THE GOD HAVE NO MERCY, THEN EVERYTHING TURNS INTO TRASH
# 天 地 不 仁 以 万 物 为 刍 狗
#
# requirements:
#   1. PhantomJS
#   2. Git
#   3. selenium
#
#####################################

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

USERNAME = '**'
PASSWORD = '**'
PROJ_PATH = '../../'
GIT_USERNAME = 'weidwonder'


def has_page_load(driver):
    return driver.execute_script("return document.readyState") == 'complete'


jin_goal_login_url = ('https://sso.jingoal.com/#/login')
jin_goal_log_edit_url = ('https://web.jingoal.com/module/worklog/editEndSegment.do')
jin_goal_domain = 'web.jingoal.com'


def jingoal_sign():
    driver = webdriver.Firefox()
    driver.get(jin_goal_login_url)
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "email")))

        username_input = driver.find_element_by_id('email')
        password_input = driver.find_element_by_id('password')
        login_button = driver.find_element_by_xpath('//*[@id="main_wraper"]/div/div[8]/a')

        username_input.send_keys(USERNAME)
        password_input.send_keys(PASSWORD)
        login_button.click()
        # WebDriverWait(driver, timeout=5).until(lambda driver: driver.current_url.startswith('https://web.jingoal.com/#workbench~type=timeline'))
        btn_xpath = '//*[@id="attend_table"]/div/div[contains(@class, "attend-btn")]/button'
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, btn_xpath))
        )
        attend_btn = driver.find_element_by_xpath(btn_xpath)
        attend_btn.click()

    except:
        driver.quit()

if __name__ == '__main__':
    jingoal_sign()