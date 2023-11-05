import base64
import time
from io import BytesIO
import random
from PIL import Image
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import cv2


def solve_slider_captcha(background_image, slider_image):
    """
    登录验证
    :param background_image:
    :param slider_image:
    :return:
    """
    background_image = cv2.imread(background_image)
    slider_image = cv2.imread(slider_image)
    # 灰度化处理
    background_gray = cv2.cvtColor(background_image, cv2.COLOR_BGR2GRAY)
    slider_gray = cv2.cvtColor(slider_image, cv2.COLOR_BGR2GRAY)

    # 进行模板匹配
    match_result = cv2.matchTemplate(background_gray, slider_gray, cv2.TM_CCOEFF_NORMED)

    # 获取最佳匹配位置
    _, max_val, _, max_loc = cv2.minMaxLoc(match_result)
    offset = max_loc

    return offset
def get_cookies():
    """
    1、selenium模拟登录处理
    2、使用数据查询cookie写入
    :return:
    """
    url = "https://list.jd.com/list.html?cat=1318,12099,9756"
    name = "15154616652"  # 修改
    password = "a19941019."  # 修改
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    driver.maximize_window()
    try:
        driver.find_element(By.XPATH, '//*[@id="ttbar-login"]/a[1]').click()
    except Exception:
        print('跳转')

    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="loginname"]')))

    driver.find_element(By.XPATH, '//*[@id="loginname"]').send_keys(name)

    driver.find_element(By.XPATH, '//*[@id="nloginpwd"]').send_keys(password)

    driver.find_element(By.XPATH, '//*[@id="formlogin"]/div[6]/div').click()
    WebDriverWait(
    driver, 30).until(EC.visibility_of_element_located(
        (By.XPATH, '//*[@id="JDJRV-wrap-loginsubmit"]/div/div/div/div[1]/div[2]/div[1]/img')))
    a=True
    while a:
        zsrc = driver.find_element(By.XPATH,'//*[@id="JDJRV-wrap-loginsubmit"]/div/div/div/div[1]/div[2]/div[1]/img').get_attribute(
            'src')  # 背景图
        csrc = driver.find_element(By.XPATH,'//*[@id="JDJRV-wrap-loginsubmit"]/div/div/div/div[1]/div[2]/div[2]/img').get_attribute(
            'src')  # 滑动图
        zimage_bytes = base64.b64decode(zsrc.split(':')[1].split(',')[1])
        print(zsrc.split(':')[1].split(',')[1])
        zimage = Image.open(BytesIO(zimage_bytes))
        zimage.save("decoded_image.png")
        cimage_bytes = base64.b64decode(csrc.split(':')[1].split(',')[1])
        cimage = Image.open(BytesIO(cimage_bytes))
        cimage.save("cdecoded_image.png")
        offset = \
        solve_slider_captcha('decoded_image.png', 'cdecoded_image.png')
        slider_elem = \
        driver.find_element(By.XPATH, '//*[@id="JDJRV-wrap-loginsubmit"]/div/div/div/div[2]/div[3]')
        action_chains = ActionChains(
        driver)
        action_chains.click_and_hold(slider_elem).move_by_offset(offset[0], 0).perform()
        action_chains.release().perform()
        time.sleep(4)
        html = driver.page_source
        if "完成拼图验证" in html:
            a=True
        else:
            a=False
        print(html)
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="J_crumbsBar"]/div')))
    cookies = driver.get_cookies()
    driver.quit()
    return cookies
get_cookies()