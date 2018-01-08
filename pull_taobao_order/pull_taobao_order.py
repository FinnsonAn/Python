from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver import ActionChains
import time
from bs4 import BeautifulSoup

#火狐浏览器驱动路径
browser_path = "/Users/ansh/Downloads/工具文件/开发相关/python/firefox_diriver/geckodriver"
#淘宝账号
username = ""
#淘宝密码
passwd = ""
#登陆页面地址 无需修改
login_path = "https://login.taobao.com/member/login.jhtml"
#我的订单页面地址 无需修改
orders_path = "https://buyertrade.taobao.com/trade/itemlist/list_bought_items.htm"

driver = None

def login():

    #打开登陆页面
    driver.get(login_path)
    while True:
        if _mock_login_submit() is True:
            break
    print("登陆成功")


def _mock_login_submit():
    print("正在尝试登陆")

    try:
        # 取得账号登陆按钮 触发点击事件 默认打开页面是需要手机淘宝扫二维码的
        username_login_btn = driver.find_element_by_xpath("//a[@class='forget-pwd J_Quick2Static']")
        username_login_btn.click()
    except exceptions.ElementNotInteractableException:
        pass

    # 取得账号密码输入框
    username_input = driver.find_element_by_id("TPL_username_1")
    passwd_input = driver.find_element_by_id("TPL_password_1")
    # 为input赋值
    username_input.clear()
    username_input.send_keys(username)
    passwd_input.send_keys(passwd)
    #取得滑块所在div，判断是否display，一般第一次登陆不需要滑动滑块
    slide_div = driver.find_element_by_id("nocaptcha")
    action_chain = ActionChains(driver)
    action_chain.click().perform()
    if slide_div.is_displayed() is True:
        # 取得滑块span
        slide_span = driver.find_element_by_id("nc_1_n1z")
        #鼠标左键按住span
        action_chain.click_and_hold(slide_span)
        # 向右拖动258像素完成验证
        action_chain.move_by_offset(258, 0)
        action_chain.perform()

    time.sleep(3)
    # 取得登陆按钮 并 触发点击事件
    submit_btn = driver.find_element_by_id("J_SubmitStatic")
    submit_btn.click()
    #取得提示信息
    try:
        message = driver.find_element_by_id("J_Message").find_element_by_class_name("error")
        if message.text == "为了你的账户安全，请拖动滑块完成验证":
            return False
    except exceptions.NoSuchElementException:
        pass
    return True

def _get_page_orders():

    beautiful_soup = BeautifulSoup(driver.page_source,"html5lib")
    #取得所有的订单div
    order_div_list = beautiful_soup.find_all("div", {"class": "index-mod__order-container___1ur4- js-order-container"})
    data_array = []
    for order_div in order_div_list:
        order_date = order_div.find("span", {"class": "bought-wrapper-mod__create-time___yNWVS"}).text
        order_product_name = order_div.find("span", {"style": "line-height:16px;"}).text
        order_amount = order_div.find("strong").contents[1].text
        data_array.append((order_date, order_product_name, order_amount, ))
    return data_array

def get_orders():
    result = []
    driver.get(orders_path)
    while True:
        #获取当前页面的订单信息
        orders = _get_page_orders()
        result.extend(orders)
        #取得下一页按钮
        next_page_li = driver.find_element_by_class_name("pagination-next")
        #判断按钮是否可点击，否则不在继续循环
        try:
            next_page_li.get_attribute("class").index("pagination-disabled")
            print("到达最后一页")
            break
        except ValueError:
            # 跳转到下个页面
            print("跳转到下一页")
            print(next_page_li.find_element_by_tag_name("a").text)
            next_page_li.click()
            time.sleep(1)
    return result



def main():
    global driver
    driver = webdriver.Firefox(executable_path=browser_path)
    #先登陆
    login()
    #爬取历史订单
    result = get_orders()
    total_amount = 0.00
    for tuple in result:
        print("订单日期：%s\t订单商品名：%s\t订单金额：%s"%tuple)
        total_amount = total_amount + float(tuple[2])
    print("共花费：", str(total_amount))


if __name__ == '__main__':
    main()