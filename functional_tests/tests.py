from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from django.test import LiveServerTestCase

class NewVisitorTest(LiveServerTestCase):
    
    def tearDown(self):
        self.browser.quit()
    
    def fill_input(self, id, text):
        input = self.browser.find_element_by_id(id)
        input.send_keys(text)
    
    def test_can_register(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)
        
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
   

if __name__ == '__main__':
    unittest.main()   