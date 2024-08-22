# WeatherPi v2
#### A weather display program for Inky pHat e-ink display


## Setup

### 1. Clone repository on to rasberry pi (or run locally to see a PNG version)
### 2. Install required packages
   - Note that Inky and several other dependancies are **only** required/installable on a Rasperry Pi 
### 3. Run the program! 

Run with `python main.py`
On first start, it will prompt you to add a WeatherUnderground API key, nearby WU station ID's and a zipcode for conditions / forecasting. These will be stored in a .env file so you'll only have to do it once!

With no flags, the program will display the current conditions and summarise the forecast
With flag `-I` or `--Image` it will show an image
With flag `-T <sample text>` or `--Text <sample text>` it will display text.
With flag `-L <log level>` or `--Loglevel <log level>` will set the logging level (options are DEBUG | INFO | WARN | ERROR)

### 4. Configure crontab to run it automatically

Append the following to your crontab job list (accessed by entering `crontab -e` in the terminal)

`0,30 * * * * <path to python3.11> <path to main.py file> 2>&1 | logger -t mycmd`

This will run the program each hour at the top of the hour and at the half hour and output the logs to the standard log file in the system. 

Note: when using crontab it's key that you use the full path both to the python executable (which you can find using `which python3`) as well as the file itself (ex. `~/WeatherPi_v2/main.py`).

## Error handling & troubleshooting
   - Once running on a pi, you can check the log output by entering `jounralctl` in the command line or by accessing `/var/log/syslog`.
   - If everything is working but you're having issues with running the script via crontab, you may need to add `SHELL=/bin/bash` at the top of the crontab file as the script should be run via bash, not sh. If that doesn't solve it, check the crontab logs and ensure you're using the correct full paths to your executable and `main.py` file


## ToDos:

- ~~Add weather symbols bottom right~~
- ~~Utilise yellow color on display~~
- ~~Remove extra narative after 3pm~~
- Update images to display with correct colours
- ~~decrease font size at certain narative string length~~
- ~~decrease font size at certain short narative string length~~
- Specify exception on line 165
- Find better font?
- Automatically attempt refresh on error after set time
- ~~show relative humidity~~
