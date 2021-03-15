# MIET Schedule API

## Description
The goal of this project is to write an API to communicate with https://miet.ru/schedule page. \
The API is needed to create Telegram bot and app, that will create ```.ics``` files for e-calendars, such as Google Calendar, iCalendar or other alternatives. \
The problem is that needed content on the page is controlled by JavaScript, which makes it impossible to write such an API in a simple way.

## Task List
- [x] Get needed HTML tags from page.
- [ ] Parse table with schedule in HTML format.
- [ ] Be able to show schedule for today (in any format)
- [ ] Be able to show schedule for a week (in any format)
- [ ] Be able to show schedule for exact date (in any format)
- [ ] Create fully working API
- [ ] Cache results
