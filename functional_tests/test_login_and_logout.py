import time

from selenium import webdriver

from .base import FunctionalTest


class UserTest(FunctionalTest):
          
    def test_login_and_logout_to_the_same_site(self):
        self.browser.get(self.live_server_url)
        self.register()
        time.sleep(2)
        
        # after registration you're logged in
        logout = self.browser.find_element_by_id('logout')
        logout.click()
        
        self.assertRegex(self.browser.current_url, '/profile/mary123')
        time.sleep(2)
        
        self.browser.get(self.live_server_url)
        
        self.fill_input('id_username', 'mary123')
        self.fill_input('id_password', 'JingleBellsBatmanSmells')
        
        submit = self.browser.find_element_by_tag_name('button')
        submit.click()
                
        self.assertEqual(self.browser.current_url, self.live_server_url + '/')
        time.sleep(2)
        
        logout = self.browser.find_element_by_id('logout')
        logout.click()
        
        self.assertEqual(self.browser.current_url, self.live_server_url + '/')

    
if __name__ == '__main__':
    unittest.main()   