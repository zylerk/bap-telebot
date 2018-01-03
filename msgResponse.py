# coding: utf-8

import os
import datetime
import MySQLdb

from model import *

# These environment variables are configured in app.yaml.
CLOUDSQL_CONNECTION_NAME = os.environ.get('CLOUDSQL_CONNECTION_NAME')
CLOUDSQL_USER = os.environ.get('CLOUDSQL_USER')
CLOUDSQL_PASSWORD = os.environ.get('CLOUDSQL_PASSWORD')

def connect_to_cloudsql():
    # When deployed to App Engine, the `SERVER_SOFTWARE` environment variable
    # will be set to 'Google App Engine/version'.
    if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'):
        # Connect using the unix socket located at
        # /cloudsql/cloudsql-connection-name.
        cloudsql_unix_socket = os.path.join(
            '/cloudsql', CLOUDSQL_CONNECTION_NAME)

        db = MySQLdb.connect(
            unix_socket=cloudsql_unix_socket,
            user=CLOUDSQL_USER,
            passwd=CLOUDSQL_PASSWORD           )

    # If the unix socket is unavailable, then try to connect using TCP. This
    # will work if you're running a local MySQL server or using the Cloud SQL
    # proxy, for example:
    #
    #   $ cloud_sql_proxy -instances=your-connection-name=tcp:3306
    #
    else:
        db = MySQLdb.connect(
            host='127.0.0.1', user=CLOUDSQL_USER, passwd=CLOUDSQL_PASSWORD )

    return db


def process_msg(text, chat_id=None):


    text = text.lower()

    if 'who' in text:
        return 1, u'I am Bitoin Trade Bot'

    elif 'time' in text or u'시간' in text:
        time_utc = datetime.datetime.now().replace(microsecond=0).isoformat(' ')
        time_seoul = datetime.datetime.now() + datetime.timedelta(hours=9)
        time_seoul = time_seoul.replace(microsecond=0).isoformat(' ')
        time_result = u'utc = {0} \n 서울 = {1}'.format(time_utc, time_seoul)
        return 1, time_result

    elif 'btc' in text or u'비트' in text:
        db = connect_to_cloudsql()
        cursor = db.cursor()
        current_spread = 0.0

        cursor.execute('select Time, btc_bittrex_usd, btc_bithumb_usd, fx_usdkrw,btc_gap_bittrex_bithumb, btc_spread_bittrex_bithumb  from bap.Price order by Time desc limit 1')
        rows = cursor.fetchall()
        result = ""
        for r in rows:
            time_seoul = r[0] + datetime.timedelta(hours=9)
            r_str = u'서울시간={v_time}\n비트렉스={v_bittrex:,.0f}\n빗섬={v_bithumb:,.0f} ({v_bithumb_krw:,.0f})\n갭={v_gap:,.0f}  스프레드={v_spread:.1f}%'\
                .format(v_time=time_seoul, v_bittrex= r[1], v_bithumb= r[2], v_bithumb_krw=r[2]*r[3],v_gap = r[4], v_spread=r[5]*100)
            current_spread = r[5]
            result += r_str + '\n'

        cursor.execute(
            'select min(btc_spread_bittrex_bithumb), avg(btc_spread_bittrex_bithumb), max(btc_spread_bittrex_bithumb) from bap.Price  where Time > adddate(CURRENT_DATE, -7)')
        rows = cursor.fetchall()
        for r in rows:
            r_str = u'최근7일 스프레드 동향\n최소={v_min:,.0f}% / 평균={v_avg:,.0f}% / 최대={v_max:,.0f}% : 현재={v_current:,.0f}% '\
                .format(v_min=r[0]*100, v_avg= r[1]*100, v_max= r[2]*100, v_current=current_spread*100)
            result += r_str + '\n'

        cursor.execute(
            'select count(Time) from bap.Price  where Time > adddate(CURRENT_DATE, -7)')
        row_total = cursor.fetchone()

        cursor.execute(
            'select count(Time) from bap.Price  where Time > adddate(CURRENT_DATE, -7) and btc_spread_bittrex_bithumb >= {v_spread}'.format(v_spread = current_spread))
        row_current = cursor.fetchone()

        where_percent = float(row_current[0]) / float(row_total[0])
        result += u'{0:.0f}% 구간에 위치'.format(where_percent * 100) + '\n'

        return 1, result

    elif 'eth' in text or u'이더' in text:
        db = connect_to_cloudsql()
        cursor = db.cursor()
        cursor.execute('select Time, eth_bittrex_usd, eth_bithumb_usd, fx_usdkrw, eth_gap_bittrex_bithumb, eth_spread_bittrex_bithumb  from bap.Price order by Time desc limit 1')

        rows = cursor.fetchall()
        result = ""
        for r in rows:
            time_seoul = r[0] + datetime.timedelta(hours=9)
            r_str = u'서울시간={v_time}\n비트렉스={v_bittrex:,.0f}\n빗섬={v_bithumb:,.0f} ({v_bithumb_krw:,.0f})\n갭={v_gap:,.0f}  스프레드={v_spread:.1f}%'\
                .format(v_time=time_seoul, v_bittrex= r[1], v_bithumb= r[2], v_bithumb_krw=r[2]*r[3],v_gap = r[4], v_spread=r[5]*100)
            result += r_str + '\n'

        cursor.execute(
            'select min(eth_spread_bittrex_bithumb), avg(eth_spread_bittrex_bithumb), max(eth_spread_bittrex_bithumb) from bap.Price  where Time > adddate(CURRENT_DATE, -7)')
        rows = cursor.fetchall()
        for r in rows:
            r_str = u'최근7일 스프레드 동향\n최소={v_min:,.0f}% / 평균={v_avg:,.0f}% / 최대={v_max:,.0f}%' \
                .format(v_min=r[0] * 100, v_avg=r[1] * 100, v_max=r[2] * 100)
            result += r_str + '\n'


        return 1, result


    elif 'xrp' in text or u'리플' in text:
        db = connect_to_cloudsql()
        cursor = db.cursor()
        cursor.execute('select Time, xrp_bittrex_usd, xrp_bithumb_usd, fx_usdkrw, xrp_gap_bittrex_bithumb, xrp_spread_bittrex_bithumb  from bap.Price order by Time desc limit 1')

        rows = cursor.fetchall()
        result = ""
        for r in rows:
            time_seoul = r[0] + datetime.timedelta(hours=9)
            r_str = u'서울시간={v_time}\n비트렉스={v_bittrex:,.2f}\n빗섬={v_bithumb:,.2f} ({v_bithumb_krw:,.0f})\n갭={v_gap:,.0f}  스프레드={v_spread:.1f}%'\
                .format(v_time=time_seoul, v_bittrex= r[1], v_bithumb= r[2], v_bithumb_krw=r[2]*r[3],v_gap = r[4], v_spread=r[5]*100)
            result += r_str + '\n'

        cursor.execute(
            'select min(xrp_spread_bittrex_bithumb), avg(xrp_spread_bittrex_bithumb), max(xrp_spread_bittrex_bithumb) from bap.Price  where Time > adddate(CURRENT_DATE, -7)')
        rows = cursor.fetchall()
        for r in rows:
            r_str = u'최근7일 스프레드 동향\n최소={v_min:,.0f}% / 평균={v_avg:,.0f}% / 최대={v_max:,.0f}%' \
                .format(v_min=r[0] * 100, v_avg=r[1] * 100, v_max=r[2] * 100)
            result += r_str + '\n'

        return 1, result


    elif 'all' in text or u'모두' in text:
        db = connect_to_cloudsql()
        cursor = db.cursor()
        res = {}
        cursor.execute('select Time, xrp_bittrex_usd, xrp_bithumb_usd, fx_usdkrw, xrp_gap_bittrex_bithumb, xrp_spread_bittrex_bithumb  from bap.Price order by Time desc limit 1')
        res['XRP'] = cursor.fetchall()
        cursor.execute('select Time, eth_bittrex_usd, eth_bithumb_usd, fx_usdkrw, eth_gap_bittrex_bithumb, eth_spread_bittrex_bithumb  from bap.Price order by Time desc limit 1')
        res['ETH'] = cursor.fetchall()
        cursor.execute('select Time, btc_bittrex_usd, btc_bithumb_usd, fx_usdkrw,btc_gap_bittrex_bithumb, btc_spread_bittrex_bithumb  from bap.Price order by Time desc limit 1')
        res['BTC'] = cursor.fetchall()

        time_seoul = res['BTC'][0][0] + datetime.timedelta(hours=9)
        r_str = u'서울시간={0}\n'.format(time_seoul)

        def makeResult(vfx):
            str = vfx + ': '
            if vfx is 'XRP':
                str += u'{v_bittrex:,.3f} ({v_bithumb_krw:,.0f}) {v_spread:.1f}%\n' \
                    .format(v_bittrex=res[vfx][0][1], v_bithumb_krw=res[vfx][0][2] * res[vfx][0][3], v_spread=res[vfx][0][5] * 100)
            else:
                str += u'{v_bittrex:,.0f} ({v_bithumb_krw:,.0f}) {v_spread:.1f}%\n' \
                    .format(v_bittrex=res[vfx][0][1], v_bithumb_krw=res[vfx][0][2] * res[vfx][0][3], v_spread=res[vfx][0][5] * 100)
            return str

        r_str += makeResult('BTC')
        r_str += makeResult('ETH')
        r_str += makeResult('XRP')

        diff_spread = u'BTC기준 상대스프레드 ETH={0:.1f}% XRP={1:.1f}%'.format(
            (res['ETH'][0][5] - res['BTC'][0][5])*100, (res['XRP'][0][5]-res['BTC'][0][5])*100 )

        r_str += diff_spread

        # r_str = u'서울시간={v_time}\nBTC={v_btc:,.0f} ({v_btc_krw:,.0f} {v_spread:.1f}%\n'\
        #     .format(v_time=time_seoul, v_btc= res['BTC'][1], v_btc_krw= res['BTC'][2]*res['BTC'][3], v_spread=r[2]*r[3],v_spread=r[5]*100)

        return 1, r_str

    elif 'user' in text or u'사용자' in text:
        r_str = u'사용자 리스트 \n'

        for chat in get_all_user():
            r_str += chat.key.string_id() + u'\n'

        return 1, r_str

    return -1, ''

