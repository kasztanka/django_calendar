import time

from selenium import webdriver

from .base import FunctionalTest


class CalendarEventTest(FunctionalTest):
    
    def test_add_calendar_and_event(self):
        self.browser.get(self.live_server_url)
        self.register()
        
        button = self.browser.find_element_by_id("add_calendar")
        button.click()
        
        self.fill_input("title", "First calendar! Wowowow!")
        colors = self.browser.find_elements_by_class("colors")
        colors[2].click()
        time.sleep(2)
        
        submit = self.browser.find_element_by_id("save_calendar")
        submit.click()
        
        calendar_url = self.browser.current_url
        self.assertRegex(url, '/calendar/')
        
        edition = self.browser.find_element_by_id("edit_calendar")
        edition.click()
        self.fill_input("title", "Stupid title. Had to changed it. Color too.")
        colors = self.browser.find_elements_by_class("colors")
        colors[1].click()
        time.sleep(2)
        
        submit = self.browser.find_element_by_id("save_calendar")
        submit.click()
        
        self.assertEqual(calendar_url, self.browser.current_url)
        
        button = self.browser.find_element_by_id("add_event")
        button.click()
        
        self.fill_input("id_title", "A little party never killed nobody.")
        self.fill_input("id_description", "You're very welcome.")
        select = self.browser.find_element_by_tag_name('select')
        for option in select.find_elements_by_tag_name('option'):
            if option.text == "Europe/Warsaw":
                option.click()
                break
        self.fill_input("id_start_hour", "20:05")
        self.fill_input("id_start_date", "2016.10.10")
        self.fill_input("id_end_hour", "12:00")
        self.fill_input("id_end_date", "2016.10.11")
        submit = self.browser.find_element_by_id("save_event")
        submit.click()
        
        event_url = self.browser.current_url
        self.assertRegex(url, '/event/')
        
        edition = self.browser.find_element_by_id("edit_event")
        edition.click()
        self.fill_input("id_description", "Come to my place to celebrate my birthday!")
        all_day = self.browser.find_element_by_id("all_day")
        all_day.click()
        # expected to fail, not sure how to check if input disabled right now
        self.fill_input("id_start_hour", "20:15")
        submit = self.browser.find_element_by_id("save_event")
        submit.click()
        
        self.assertEqual(event_url, self.browser.current_url)     
        

if __name__ == '__main__':
    unittest.main() 