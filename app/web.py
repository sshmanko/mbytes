from datetime import datetime, timedelta, timezone

import requests
from flask import Flask, redirect, render_template
from flask import request

app = Flask(__name__)


def api_request(url, timeout=1):
    try:
        r = requests.get(url, timeout=timeout)
        r.raise_for_status()
        return r.json()

    except Exception as err:
        app.logger.exception(f"{url} API error: {err}")


def ip_to_country(ip):
    country = {}
    if ip == '127.0.0.1':  # ipwhois.info treats 127.0.0.1 as Singapore
        country['country'] = 'United States'
        country['country_code'] = 'US'
    else:
        country = api_request(f'http://ipwhois.app/json/{ip}')

    return country


@app.route('/<country>')
def get_country(country):
    covid_countries = sorted(api_request('https://api.covid19api.com/countries'), key=lambda x: x['Country'])

    country_uri, country_name = '', ''

    for c in covid_countries:
        if c['ISO2'] == country:
            country_name = c['Country']
            country_uri = c['Slug']
            break

    if country_uri:
        covid_data = api_request(f'https://api.covid19api.com/total/country/{country_uri}', 5)
        if covid_data:
            # Find peak date
            peak = max(covid_data, key=lambda x: x['Active'])
            peak_date = datetime.strptime(peak['Date'], '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d')

            today = datetime.now().replace(tzinfo=timezone.utc)
            yesterday = today - timedelta(days=1)
            yesterday_midnight = yesterday.strftime('%Y-%m-%d')

            if peak_date == yesterday_midnight:
                text = f'Most covid-infected people were at <b>{peak_date}</b>.<br> ' \
                       f'This country hasn\'t reached the peak infections yet. :(<br>'
            else:
                text = f'Most covid-infected people were at <b>{peak_date}</b>.<br> ' \
                       f'This country has passed infections peak. :)<br>'

            new_active_cases = covid_data[-1]['Active'] - covid_data[-2]['Active']
            total_cases = covid_data[-1]['Active']

            if new_active_cases >= 0:
                text += f'<p>Yesterday the number of sick people (recovered-infected) increased by ' \
                        f'<b>{new_active_cases}</b> to a total of {total_cases}</p>'
            else:
                text += f'<p>Yesterday the number of sick people (recovered-infected) decreased by ' \
                        f'<b>{abs(new_active_cases)}</b> to a total of {total_cases}</p>'

            return render_template("country.html",
                                   graph_data_x=[x['Active'] for x in covid_data],
                                   graph_data_y=[y['Date'][:-10] for y in covid_data],
                                   country_name=country_name,
                                   covid_countries=covid_countries,
                                   text=text)

    return f'No data for country {country}', 404


@app.route('/')
def get_root():
    country_code = ip_to_country(request.remote_addr)['country_code']
    return redirect(f'/{country_code}', code=302)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)
