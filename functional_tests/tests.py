import time

from selenium.webdriver.common.keys import Keys
from selenium import webdriver

from django.test import LiveServerTestCase

class NewVisitorTest(LiveServerTestCase):
    
    def tearDown(self):
        time.sleep(3)
        self.browser.refresh()
        self.browser.quit()
    
    def fill_input(self, id, text):
        input = self.browser.find_element_by_id(id)
        input.send_keys(text)
    
    def test_can_register(self):
        self.browser = webdriver.Firefox()
        time.sleep(2)
        
        self.browser.get(self.live_server_url)
        
        link = self.browser.find_element_by_id('registration')
        link.click()
        
        self.assertRegex(self.browser.current_url, '/register')
        
        self.fill_input('id_username', 'mary123')
        self.fill_input('id_password', 'Goldeneye')
        self.fill_input('id_email', 'mary@lou.com')
        self.fill_input('id_first_name', 'Mary')
        self.fill_input('id_last_name', 'Lou')
        
        select = self.browser.find_element_by_tag_name('select')
        for option in select.find_elements_by_tag_name('option'):
            if option.text == "Europe/Warsaw":
                option.click()
                break
        
        self.browser.find_element_by_tag_name('button').click()
        
        self.assertRegex(self.browser.current_url, '/profile/mary123')
        name = self.browser.find_element_by_tag_name('h2')
        self.assertEqual(name.text, 'Mary Lou')
   

class UserTest(LiveServerTestCase):
    
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
        
    def test_user_login_and_logout(self):
        self.browser.get(self.live_server_url)
        self.register()
        time.sleep(2)
        
        # after registration you're logged in
        logout = self.browser.find_element_by_id('logout')
        logout.click()
        time.sleep(2)
        
        self.fill_input('id_username', 'mary123')
        self.fill_input('id_password', 'JingleBellsBatmanSmells')
        
        submit = self.browser.find_element_by_tag_name('button')
        submit.click()
                
        self.assertRegex(self.browser.current_url, '/profile/mary123')
        time.sleep(2)
        
        logout = self.browser.find_element_by_id('logout')
        logout.click()
        
        self.assertEqual(self.browser.current_url, self.live_server_url + '/')

        
if __name__ == '__main__':
    unittest.main()   