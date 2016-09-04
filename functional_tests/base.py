import time

from selenium import webdriver

from django.test import LiveServerTestCase

class FunctionalTest(LiveServerTestCase):
    
    def setUp(self):
        self.browser = webdriver.Firefox()
        time.sleep(2)
    
    def tearDown(self):
        time.sleep(3)
        self.browser.refresh()
        self.browser.quit()
    
    def fill_input(self, id, text):
        input = self.browser.find_element_by_id(id)
        input.send_keys(text)
    
    def register(self):
        link = self.browser.find_element_by_id('registration')
        link.click()
        self.fill_input('id_username', 'mary123')
        self.fill_input('id_password', 'JingleBellsBatmanSmells')
        self.fill_input('id_email', 'mary@lou.com')
        self.fill_input('id_first_name', 'Mary')
        self.fill_input('id_last_name', 'Lou')
        self.browser.find_element_by_tag_name('button').click()
       
    
if __name__ == '__main__':
    unittest.main()   