# Music scraper

This is a scraper that collects audio tracks data from iTunes and saves chords and lyrics from e-chords.com.

## Description

Based on the artist name and track title scraper searches for all albums that contain tracks with those input data. Then scraper collects data about songs that exist in albums that match the previous conditions. All output data is stored in a CSV file.

Using artist name and track title values scraper searches for songs chords and lyrics at e-chords.com. Then it stores data in a TXT file.

## Usage

Input artist name and track title pair to search_input.xlsx file. You can input as many pairs as you want.

Then launch runner.py file. It will start both scripts that collect data on iTunes and on e-chords.com.

Check the routings to mention files in the description below.

### Path to input data
- scr
  - data_files
    - search_input.xlsx

### Path to launcher
- src
  - runner.py

### Path to output files
- scr
  - data_files
    - itunes_test.csv
    - ***.txt

### Path to spiders
- scr
  - webscraper
    - spiders
      - itunes_test_spider.py
      - chords_spider.py