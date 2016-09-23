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
        input.clear()
        input.send_keys(text)
     
    def get_page_text(self):
        return self.browser.find_element_by_tag_name('body'
            ).get_attribute('innerHTML')
    
    def add_calendar(self, name="Example", can_read=None, can_modify=None):
        self.browser.get(self.live_server_url + '/calendar/new')
        self.fill_input("id_name", name)
        if can_read != None:
            inputs = self.browser.find_elements_by_name("can_read")
            for username in can_read:
                for input in inputs:
                    parent = input.find_element_by_xpath('..')
                    if username in parent.text:
                        input.click()
        if can_modify != None:
            inputs = self.browser.find_elements_by_name("can_modify")
            for username in can_modify:
                for input in inputs:
                    parent = input.find_element_by_xpath('..')
                    if username in parent.text:
                        input.click()
        submit = self.browser.find_element_by_id("save_calendar")
        submit.click()
        return self.browser.current_url[-1]
        
    def add_event(self, calendar_pk=1, title="New event"):
        self.browser.get(self.live_server_url + '/event/new/{}'.format(calendar_pk))
        self.fill_input("id_title", title)
        submit = self.browser.find_element_by_id("save_event")
        submit.click()
        return self.browser.current_url[-1]
    
    def logout(self):
        logout = self.browser.find_element_by_id("logout")
        logout.click()
    
    def register(self, username='mary123'):
        self.browser.get(self.live_server_url)
        link = self.browser.find_element_by_id('registration')
        link.click()
        self.fill_input('id_username', username)
        self.fill_input('id_password', 'JingleBellsBatmanSmells')
        self.fill_input('id_email', 'mary@lou.com')
        self.fill_input('id_first_name', 'Mary')
        self.fill_input('id_last_name', 'Lou')
        self.browser.find_element_by_tag_name('button').click()
       
    
if __name__ == '__main__':
    unittest.main()   