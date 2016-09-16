import time

from selenium import webdriver
from selenium.common.exceptions import (InvalidElementStateException,
    InvalidSelectorException)

from .base import FunctionalTest


class CalendarEventTest(FunctionalTest):
    
    def test_add_calendar_and_event(self):
        self.browser.get(self.live_server_url)
        self.register()
        
        button = self.browser.find_element_by_id("add_calendar")
        button.click()
        
        self.fill_input("id_name", "First calendar! Wowowow!")
        colors = self.browser.find_elements_by_class_name("colors")
        colors[2].click()
        time.sleep(2)
        
        submit = self.browser.find_element_by_id("save_calendar")
        submit.click()
        
        calendar_url = self.browser.current_url
        self.assertRegex(calendar_url, '/calendar/\d+')
        
        edition = self.browser.find_element_by_id("edit_calendar")
        edition.click()
        self.fill_input("id_name", "Stupid name. Had to changed it. Color too.")
        colors = self.browser.find_elements_by_class_name("colors")
        colors[1].click()
        time.sleep(2)
        
        submit = self.browser.find_element_by_id("save_calendar")
        submit.click()
        
        self.assertEqual(calendar_url, self.browser.current_url)
        
        button = self.browser.find_element_by_id("add_event")
        button.click()
        
        self.fill_input("id_title", "A little party never killed nobody.")
        self.fill_input("id_desc", "You're very welcome.")
        select = self.browser.find_element_by_tag_name('select')
        for option in select.find_elements_by_tag_name('option'):
            if option.text == "Europe/Warsaw":
                option.click()
                break
        self.fill_input("id_start_hour", "20:05")
        self.fill_input("id_start_date", "10/10/2016")
        self.fill_input("id_end_hour", "12:00")
        self.fill_input("id_end_date", "11/10/2016")
        
        all_day = self.browser.find_element_by_id("id_all_day")
        all_day.click()
        # changing hour or timezone should be disabled
        with self.assertRaises(InvalidElementStateException):
            self.browser.find_element_by_id("id_start_hour").clear()
            self.fill_input("id_start_hour", "20:15")
        with self.assertRaises(InvalidElementStateException):
            self.browser.find_element_by_id("id_end_hour").clear()
            self.fill_input("id_end_hour", "20:25")
        select = self.browser.find_element_by_tag_name('select')
        self.assertFalse(select.is_enabled())
        all_day.click()
        
        submit = self.browser.find_element_by_id("save_event")
        submit.click()
        
        event_url = self.browser.current_url
        self.assertRegex(event_url, '/event/\d+')
        page_text = self.browser.find_element_by_tag_name(
            'body').get_attribute('innerHTML')
        self.assertIn("<p>Europe/Warsaw</p>", page_text)
        
        edition = self.browser.find_element_by_id("edit_event")
        edition.click()
        # fields should be filled in
        self.browser.find_element_by_id("id_desc").clear()
        self.fill_input("id_desc", "Come to my place for my birthday!")
        
        all_day = self.browser.find_element_by_id("id_all_day")
        all_day.click()
        # changing hour or timezone should be disabled
        with self.assertRaises(InvalidElementStateException):
            self.browser.find_element_by_id("id_start_hour").clear()
            self.fill_input("id_start_hour", "20:15")
        with self.assertRaises(InvalidElementStateException):
            self.browser.find_element_by_id("id_end_hour").clear()
            self.fill_input("id_end_hour", "20:25")
        select = self.browser.find_element_by_tag_name('select')
        self.assertFalse(select.is_enabled())
        time.sleep(2)
        
        submit = self.browser.find_element_by_id("save_event")
        submit.click()
        time.sleep(2)
        
        page_text = self.browser.find_element_by_tag_name(
            'body').get_attribute('innerHTML')
        self.assertIn("<p>Come to my place for my birthday!</p>", page_text)
        

if __name__ == '__main__':
    unittest.main() 