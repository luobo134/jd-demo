from tkinter import Image
import scrapy
import json
import base64
import time
from io import BytesIO
from PIL import Image
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import cv2

class JdSpiderSpider(scrapy.Spider):
    name = "jd_spider"
    allowed_domains = ["jd.com"]
    start_urls = []

    for i in range(1, 100):
        url = ' https://list.jd.com/list.html?cat=1318,12099,9756&page=' + str(1+(i-1)*2)
        start_urls.append(url)
    def parse(self, response):

        # 获取商品url
        products = response.xpath('//*[@id="J_goodsList"]/ul/li')
        for product in products:
            bthrf=product.xpath('//div[@class="gl-i-wrap"]/div[@class="p-img"]/a/@href').get()
        yield scrapy.Request(url='https:'+bthrf, callback=self.sp_parse,cookies=self.do_cookies)


    def sp_parse(self,response):
        item = {}
        items=[]
        # 提取字段
        print('-------------------')
        item['title'] = response.xpath('/html/body/div[6]/div/div[2]/div[1]/string()').get()#标题
        print('title')
        item['price'] = response.xpath('/html/body/div[6]/div/div[2]/div[4]/div/div[1]/div[2]/span[1]/span[2]/string()').get()#价格
        print('price')
        color=[]
        colors=response.xpath('//*[@id="choose-attr-1"]/div[2]/div')
        for c in colors:
            color.append(str(c.xpath('//i/string()').get()))
        item['color'] = color  # 颜色字段
        size=[]
        sizes=response.xpath('//*[@id="choose-attr-2"]/div[2]/div')
        for s in sizes:
            size.append(str(s.xpath('//a/string()').get()))
        item['size'] = size  # 尺码字段
        item['sku'] = str(response.url).split("/")[-1].split(".")[0]  # 网站货号字段
        item['details'] = response.xpath('//*[@id="detail"]/div[2]/div[1]/div[1]/ul[2]').get()  # 详情字段
        item['img_urls'] = response.xpath('//*[@id="J-detail-content"]/style/text()').get()

        items.append(item)
        print("===========================================")
        json_data = json.dumps(items, ensure_ascii=False)
        with open('scraped_data.json', 'w', encoding='utf-8') as f:
            f.write(json_data)
    def start_requests(self):
        self.do_cookies={}
        _cookies=self.get_cookies()

        for co in _cookies:
            c_name = co["name"]
            c_value = co["value"]

            if self.is_chinese(c_value):
                c_value = c_value.encode('utf-8').decode('latin-1')
            self.do_cookies[c_name] = c_value
        # for url in self.start_urls:
        yield scrapy.Request(url=self.start_urls[0], callback=self.parse,cookies=self.do_cookies)

    def is_chinese(self, char):
        """
        处理cook判断是否有中文
        :param char:
        :return:
        """
        if '\u4e00' <= char <= '\u9fff':
            return True
        else:
            return False
    def solve_slider_captcha(self,background_image, slider_image):
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

    def get_cookies(self):
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
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.get(url)
        self.driver.maximize_window()
        try:
            self.driver.find_element(By.XPATH, '//*[@id="ttbar-login"]/a[1]').click()
        except Exception:
            print('跳转')

        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="loginname"]')))

        self.driver.find_element(By.XPATH, '//*[@id="loginname"]').send_keys(name)

        self.driver.find_element(By.XPATH, '//*[@id="nloginpwd"]').send_keys(password)

        self.driver.find_element(By.XPATH, '//*[@id="formlogin"]/div[6]/div').click()
        WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located(
            (By.XPATH, '//*[@id="JDJRV-wrap-loginsubmit"]/div/div/div/div[1]/div[2]/div[1]/img')))
        a=True
        while a:
            zsrc = self.driver.find_element(By.XPATH,'//*[@id="JDJRV-wrap-loginsubmit"]/div/div/div/div[1]/div[2]/div[1]/img').get_attribute(
                'src')  # 背景图
            csrc = \
            self.driver.find_element(By.XPATH,
                                            '//*[@id="JDJRV-wrap-loginsubmit"]/div/div/div/div[1]/div[2]/div[2]/img').get_attribute(
                'src')  # 滑动图
            zimage_bytes = base64.b64decode(zsrc.split(':')[1].split(',')[1])
            zimage = Image.open(BytesIO(zimage_bytes))
            zimage.save("decoded_image.png")
            cimage_bytes = base64.b64decode(csrc.split(':')[1].split(',')[1])
            cimage = Image.open(BytesIO(cimage_bytes))
            cimage.save("cdecoded_image.png")
            offset = self.solve_slider_captcha('decoded_image.png', 'cdecoded_image.png')
            slider_elem = \
            self.driver.find_element(By.XPATH, '//*[@id="JDJRV-wrap-loginsubmit"]/div/div/div/div[2]/div[3]')
            action_chains = ActionChains(
            self.driver)
            action_chains.click_and_hold(slider_elem).move_by_offset(offset[0], 0).perform()
            action_chains.release().perform()
            time.sleep(4)
            html = self.driver.page_source
            if "完成拼图验证" in html:
                a=True
            else:
                a=False
        try:
            WebDriverWait(self.driver,30).until(EC.visibility_of_element_located((By.XPATH,'//*[@id="J_user"]/div')))
        except:
            WebDriverWait(self.driver,30).until(EC.visibility_of_element_located((By.XPATH,'//*[@id="J_crumbsBar"]')))
        cookies = self.driver.get_cookies()
        self.driver.quit()
        return cookies




