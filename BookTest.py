from time import sleep
from playwright.sync_api import sync_playwright
import easyocr
import subprocess

class TeamsLogin:
    url = 'https://www.pxw1.snb.ca/snb9000/product.aspx?ProductID=A014SN9000a&l='
    driverLicenseNumber = ''
    birthDay = ''
    email = ''
    searchTimes = 1
    location = 'Fredericton'

    def __init__(self):
        self.page = None
        self.playwright = None
        self.browser = None
        self.captcha_img = None

    def handleStep1(self):
        print("enter handleStep1", self.page.url)
        handle = self.page.query_selector("#DEX_TestTypeID")
        handle.select_option(label="Road test - car (Class 7, Level 2 or Class 5)")
        sleep(1)

        self.page.eval_on_selector("#confirmeligible", "element => element.click()")
        sleep(1)
        handle = self.page.query_selector("#ResourceID")
        handle.select_option(label=self.location)
        sleep(1)
        self.page.eval_on_selector("#DEX_LangChoice", "element => element.click()")
        sleep(1)
        self.page.locator("#_ctl4_DEX_btnSubmit").click()
        sleep(10)
        self.handleStep2()


    def handleStep2(self):
        print("enter handleStep2", self.page.url)
        self.page.locator("#DriverLicenseNumber").fill(self.driverLicenseNumber)
        sleep(1)
        self.page.locator("#des_DOB").fill(self.birthDay)
        sleep(1)
        self.page.locator("#DEX_Email").fill(self.email)
        sleep(2)
        self.page.keyboard.press("Tab")
        self.page.keyboard.type(self.email)
        self.submitStep2()
        sleep(5)

    def submitStep2(self):
        try:
            sleep(1)
            self.handleCaptcha()
            sleep(1)
            self.page.locator("#_ctl4_DEX_btnSubmit").click()
            sleep(5)

            message_elem = self.page.query_selector('.ErrorDetail')

            print('.............ErrorDetail')
            print(str(message_elem))

            if message_elem != None:
                print("Captcha is wrong. Try again.")
                self.handleStep2()
                return

            self.handleStep3()
        except Exception as e:
            print('###############')
            print(e)
            sleep(5)
            self.page.reload()
            sleep(5)
            self.handleStep2()


    def handleStep3(self):
        print("enter handleStep3", self.page.url)
        message_elem = self.page.get_by_text('No available slot found for this test type at this location, try searching on a different location.')
        if message_elem.count() == 1:
            print("Slot not found for "+ str(self.searchTimes)+" times, Searching again")
            self.page.screenshot(path='screenshot/result'+str(self.searchTimes)+'.png')
            self.searchTimes +=1
            self.page.locator("#_ctl4_DEX_btnSearchAgain").click()
            # search every 5 minutes
            sleep(5*60)
            self.handleStep1()
        else:
            self.page.screenshot(path='screenshot/success.png')
            print("Slot found")
            subprocess.call(['open', 'alarm.mp3'])

    def handleCaptcha(self):
        self.captcha_img = self.page.wait_for_selector('xpath=//label[text()="Enter the CAPTCHA code exactly as it appears:"]/../following-sibling::div/img')
        captcha_img_box = self.captcha_img.bounding_box()
        imagePath ='screenshot/captcha.png'
        self.page.screenshot(path=imagePath, clip=captcha_img_box)
        sleep(3)
        captchaText = self.recognizeCaptcha(imagePath)
        sleep(1)
        self.page.locator("#DEX_captcha").fill(captchaText)


    def getCaptchaText(self, path):
        with open(path, 'rb') as file:
            image = file.read()
        reader = easyocr.Reader(['en'])
        result = reader.readtext(image, allowlist='0123456789', beamWidth=15)
        return result[0][1]

    def recognizeCaptcha(self, path):
        captchaText = None
        captchaText = self.getCaptchaText(path)
        print("CAPTCHA code is: "+ captchaText)
        if(captchaText==None or len(captchaText) != 6):
            raise Exception("Failed to recognize CAPTCHA")
        else:
            return captchaText

    def start(self):
        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=False,  # Set headless=False for testing
                ignore_default_args=["--mute-audio"]
            )

            context = self.browser.new_context(permissions=['microphone', 'camera'])
            self.page = context.new_page()
            self.page.goto(self.url, wait_until="networkidle")
            print('Browser should be running')
            self.page.locator("#_ctl4_DEX_chooseEnglish").click()
            sleep(1)
            self.page.locator("#btnWritten").click()
            sleep(1)
            self.page.locator("#DEX_btnBook").click()
            sleep(1)

            self.handleStep1()
        except Exception as e:
            self.browser.close()
            self.playwright.stop()
            print('Error')
            print(e)
            self.start()
        sleep(1000)

    def login(self, url):
        if url == None:
            return
        self.start()


if __name__ == "__main__":
    TeamsLogin().login(TeamsLogin.url)


