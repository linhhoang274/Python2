from datetime import date

import pandas
import requests

with open("postcodes-fin", mode="r", encoding="utf-8-sig") as f:
    postcodes = (f.readlines())

postcodes = list(map(lambda pc: pc.replace('\n', ''), postcodes))

today_date = date.today()
current_year = today_date.year

years = []
for l in range(5):
    years.append(current_year - l)


def create_pxweb_url_from_year(y):
    return 'https://pxnet2.stat.fi:443/PXWeb/api/v1/en/Postinumeroalueittainen_avoin_tieto/' + str(
        y) + '/paavo_pxt_12f1.px'


def create_pxweb_json_from_postcode(pc):
    return {
        "query": [
            {
                "code": "Postinumeroalue",
                "selection": {
                    "filter": "item",
                    "values": [
                        str(pc)
                    ]
                }
            },
            {
                "code": "Tiedot",
                "selection": {
                    "filter": "item",
                    "values": [
                        "hr_ktu"
                    ]
                }
            }
        ],
        "response": {
            "format": "json-stat2"
        }
    }


# years = [2022, 2021, 2020, 2019, 2018]

table = []

for postcode in postcodes:
    for year in years:
        try:
            response = requests.post(
                create_pxweb_url_from_year(year),
                json=create_pxweb_json_from_postcode(postcode)
            )
            if response.json().get('value') is None:
                table.append([postcode, year, None])
            else:
                table.append([postcode, year, response.json().get('value')[0]])

        except requests.exceptions.RequestException:
            table.append([postcode, year, None])

df = pandas.DataFrame(table)

df.columns = ['Postcode', 'Year', 'Avg_income']

Pt = df.pivot_table('Avg_income', index='Postcode', columns='Year', fill_value=0)

Pt['Income_change_in_5years_%'] = (Pt[2022] - Pt[2020]) / Pt[2020] * 100

print(Pt[Pt['Income_change_in_5years_%'] == Pt['Income_change_in_5years_%'].max()])
