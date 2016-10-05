import datetime
import time
import pytz


from selenium import webdriver

from functional_tests.base import FunctionalTest


class AllDayTest(FunctionalTest):
    
    def test_when_all_day_hours_and_timezone_dont_display(self):
        self.register()
        cal_pk = self.add_calendar()
        event_pk = self.add_event(calendar_pk=cal_pk, all_day=True)
        
        self.browser.get(self.live_server_url + '/event/{}'.format(event_pk))
        page_text = self.get_page_text()
        self.assertFalse("<p>Timezone:" in page_text)
        
        europe = pytz.timezone("Europe/Warsaw")
        utc_date = europe.localize(datetime.datetime.now()).astimezone(pytz.utc)
        self.assertFalse(("<p>" + utc_date.strftime('%m/%d/%Y %H:%M') + "</p>") in page_text)
        self.assertTrue(("<p>" + utc_date.strftime('%m/%d/%Y') + "</p>") in page_text)
        

if __name__ == '__main__':
    unittest.main() 