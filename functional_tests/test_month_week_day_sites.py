import datetime
import time

from selenium import webdriver

from functional_tests.base import FunctionalTest


class UserTest(FunctionalTest):
    
    def test_month_week_day_sites(self):
        self.browser.get(self.live_server_url)
        self.register()
        time.sleep(2)
        
        timeline = self.browser.find_element_by_id('timeline')
        timeline.click()
        
        self.assertRegex(self.browser.current_url, '/month')
        page_text = self.get_page_text()
        date_ = datetime.datetime.now()
        time.sleep(2)
        self.assertIn("<td>" + date_.strftime("%d %b"), page_text)
        
        week_ = self.browser.find_element_by_id('week')
        week_.click()
        self.assertRegex(self.browser.current_url, '/week')
        page_text = self.get_page_text()
        time.sleep(2)
        self.assertIn(date_.strftime("%A %m/%d"), page_text)
        
        
        day_ = self.browser.find_element_by_id('day')
        day_.click()
        self.assertRegex(self.browser.current_url, '/day')
        page_text = self.get_page_text()
        time.sleep(2)
        self.assertIn(date_.strftime("%A %m/%d"), page_text)
        
    
if __name__ == '__main__':
    unittest.main()   