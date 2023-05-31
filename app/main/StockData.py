import requests, json
import pandas as pd

### GLOBAL VARIABLES

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'

USER_AGENT_2 = 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36'

### STOCK BASCI INFORMATION

def get_stock_basic_info(stock_id):
    try:
        basic = get_stock_basic_info_inner(stock_id)
    except Exception:
        basic = {'good': False}
    return basic


def get_stock_basic_info_inner(stock_id):
    '''
    stock_id: sh or sz + 6 numbers stock code\n
    '''
    headers = {
        'User-Agent': USER_AGENT,
        'host':'qt.gtimg.cn',
        'referer': 'https://gu.qq.com/',
    }
    url = 'http://qt.gtimg.cn/q=s_{}'.format(stock_id)
    response = requests.get(url, headers = headers)
    res = response.text
    '''
    response:
    v_s_{stockid}="{market}~{stockname}~{id(only number)}~{pricenow}~{increment}~{increment percent}~{lots}~{turnover(10^4)}~{status}~{market value(10^8)}~{type}";
    market: 1-sh 51-sz
    increment: compared with close of last trade day
    '''
    reslis = res.split('=')[1][1:-3].split('~')
    basic = {}
    if reslis[0] == 1:
        basic['market'] = 'sse'
    elif reslis[0] == 51:
        basic['market'] = 'szse'
    basic['stockid'] = stock_id
    basic['stockname'] = reslis[1]
    basic['type'] = reslis[10]
    basic['status'] = reslis[8]
    goodtypelis = ['GP-A', 'GP-A-KCB', 'GP-A-CYB', 'KCB', 'CYB']
    if basic['status'] == '' and basic['type'] in goodtypelis:
        basic['good'] = True
    else:
        basic['good'] = False
    return basic


### STOCK DATA

## NETEASE
## seems that netease finance service has been stopped this year

def get_stock_price_history_netease(stock_id):
    '''
    stock_id: sh or sz + 6 numbers stock code\n
    code : number 0 or 1 + 6 numbers stock code\n
    0 represents sh while 1 represents sz\n
    lack the data of about recent 4 months\n
    note: seems that netease finance service has been stopped this year\n
    date: 20230424
    '''
    if stock_id[:2] == 'sh':
        code = '0' + stock_id[2:]
    else:
        code = '1' + stock_id[2:]

    headers = {
        'User-Agent': USER_AGENT,
    }
    url = 'http://img1.money.126.net/data/hs/kline/day/times/{}.json'.format(code)
    response = requests.get(url, headers = headers)
    res = json.loads(response.text)
    '''
    {name, symbol, times, closes}\n
    {str, str, [str(yyyymmdd)], [float]}
    '''
    res.pop('name')
    res.pop('symbol')
    df = pd.DataFrame(res)
    # print(df)
    df['times'] = pd.to_datetime(df['times']).dt.date
    df.columns = ['date', 'close']
    return df


def get_stock_price_by_year_netease(stock_id, year):
    '''
    stock_id: sh or sz + 6 numbers stock code\n
    code : number 0 or 1 + 6 numbers stock code\n
    0 represents sh while 1 represents sz\n
    lack the data of about recent 3 months\n
    note: seems that netease finance service has been stopped this year\n
    date: 20230424
    '''
    if stock_id[:2] == 'sh':
        code = '0' + stock_id[2:]
    else:
        code = '1' + stock_id[2:]
    headers = {
        'User-Agent': USER_AGENT,
    }
    url = 'https://img1.money.126.net/data/hs/kline/day/history/{}/{}.json'.format(year, code)
    response = requests.get(url, headers = headers)
    res = json.loads(response.text)
    '''
    {name, data([date, open, close, high, low, volume, rate]), symbol}\n
    {str, [str(yyyymmdd), float, float, float, float, int, float], str}
    '''
    df = pd.DataFrame(res['data'], columns = ['date', 'open', 'close', 'high', 'low', 'volume', 'rate'])
    df.drop(columns = ['rate'], inplace = True)
    df['date'] = pd.to_datetime(df['date'], format = '%Y%m%d').dt.strftime('%Y-%m-%d')
    df['volume'] = round(df['volume'].astype('int64')/100)
    df['volume'] = df['volume'].astype('int64')
    return df


## TENCENT

def get_stock_price_by_from_to_tencent(stock_id, url_1 = True, from_date = None, to_date = None, days = 2000):
    '''
    stock_id: sh or sz + 6 numbers stock code\n
    from & to date: yyyy-mm-dd\n
    days: max 2000\n
    url_1 = 'https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={stock_id},day,{from_date},{to_date},{days},bfq'\n
    -- fqkline: fuquan kline, bfq: bufuquan\n
    url_2 = 'https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?_var=kline_daybfq&param={stock_id},day,{from_date},{to_date},{days},bfq'\n
    -- fqkline: fuquan kline, kline_daybfq: kline day bufuquan, bfq: bufuquan\n
    must have days\n
    date must be valid, needn't be a valid trade date\n
    (the from_date can be earlier than the issuing date and the to_date can be later than today)\n
    if there isn't a to_date attribute, it's today\n
    if the days between from_date and to_date larger than days, return data from days before the to_date
    '''
    headers = {
        'User-Agent': USER_AGENT_2,
        #'host':'web.sqt.gtimg.cn',
        'referer': 'https://gu.qq.com/',
        'Connection':'close',
    }
    if from_date is None:
        from_date = ''
    if to_date is None:
        to_date = ''
    url_1 = 'https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={},day,{},{},{},bfq'.format(stock_id, from_date, to_date, days)
    url_2 = 'https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?_var=kline_daybfq&param={},day,{},{},{},bfq'.format(stock_id, from_date, to_date, days)
    if url_1 == True:
        response = requests.get(url_1, headers = headers)
        res = json.loads(response.text)
    else:
        response = requests.get(url_2, headers = headers)
        res = json.loads(response.text[13:])
    '''
    Both url return data in a dictionary, url_2 with a 'kline_daybfq' in front of the dictionary while url_1 do not have it.\n
    The dictionaries' pattern is as follows:\n
    {code, msg, data} {int, str, dict}\n
    data: {stock_id} {dict}\n
    stockid: {day, qt, mx_price, prec, version} {list, dict, dict, str, str}\n
    day: [[date, open, close, high, low, volume]]\n
    day: [[str(yyyy-mm-dd), str(float), str(float), str(float), str(float), str(float)]] volume: {volume} hundreds\n
    some days will have an extra element in the list, normally a dictionary\n
    {nd(niandu), fh_sh(fenhong shuihou), djr(dengjiri), cqr(chuquanri), FHcontent(fenhong content)}\n
    {str(year), str(float), date(yyyy-mm-dd), date(yyyy-mm-dd), str}
    qt: {stock_id, market, zjlx} {list, list, list}\n
    market: [str], only one str in the list, describe markets' status at the very time\n
    mx_price: {mx, price} {list, list}\n
    the attributes didn't give information detail has unknown meaning now
    '''
    df = pd.DataFrame(res['data'][stock_id]['day'])
    try:
        df.columns = ['date', 'open', 'close', 'high', 'low', 'volume']
    except:
        df.columns = ['date', 'open', 'close', 'high', 'low', 'volume', 'addition']
        df.drop(columns = ['addition'], inplace = True)
        df['volume'] = df['volume'].astype('float64').astype('int64')
    # validate the from date
    if from_date != '':
        pass
    return df


def get_stock_price_by_year_tencent(stock_id, year):
    '''
    stock_id: sh or sz + 6 numbers stock code\n
    input year: yyyy\n
    year: yy\n
    can not query date of the current year\n
    not full
    date: 20230424
    '''
    year = str(year)[-2:]
    headers = {
        'User-Agent': USER_AGENT,
    }
    url = 'http://data.gtimg.cn/flashdata/hushen/daily/{}/{}.js?visitDstTime=1'.format(year, stock_id)
    response = requests.get(url, headers = headers)
    res = response.text
    '''
    response: data of the whole year, every trade day occupies one line.\n
    the first line: daily_data_{yy}="\n
    the last line: ";\n
    the middle lines: yymmdd open close high low volume\n
    volume: {volume} hundreds\n
    all the line are end with \\n\\
    '''
    res = [item.strip().split(' ') for item in res.split('\\n\\')[1:-1]]
    df = pd.DataFrame(res, columns = ['date', 'open', 'close', 'high', 'low', 'volume'])
    df['date'] = pd.to_datetime(df['date'], format = '%y%m%d').dt.strftime('%Y-%m-%d')
    return df


## SOHU

def get_stock_price_by_from_to_sohu(stock_id, from_date, to_date):
    '''
    stock_id: sh or sz + 6 numbers stock code
    code: countryname + _ + 6 numbers stock code\n
    china: cn\n
    input from & to date : yyyy-mm-dd\n
    from & to date : yyyymmdd\n
    this is only for A-shares of sh & sz\n
    lack some days' data for unknown reason
    '''
    headers = {
        'User-Agent': USER_AGENT,
        'referer': 'https://q.stock.sohu.com/',
    }
    from_date = ''.join(from_date.split('-'))
    to_date = ''.join(to_date.split('-'))
    code = 'cn_' + stock_id[2:]
    url = 'https://q.stock.sohu.com/hisHq?code={}&start={}&end={}&stat=1&order=D&period=d&callback=historySearchHandler&rt=jsonp'.format(code, from_date, to_date)
    response = requests.get(url, headers = headers)
    res = json.loads(response.text[21:-2])

    '''
    response: a list in historySearchHandler()\n
    [dict], dict: {status, hq, code, stat} {int, list, str, list}\n
    hq: [date(yyyy-mm-dd), open, close, close_increase, unknown_rate, low, high, volume, unknownrate, unknown]\n
    hq: [str, str(float), str(float), str(float), str(float%), str(float), str(float), int, str(float), str(float%)]\n
    volume: {volume} hundreds\n
    code: countryname + _ + 6 numbers stock code\n
    stat: statistics of the time span selected
    '''
    df = pd.DataFrame(res[0]['hq'])
    df = df[[0, 1, 2, 5, 6, 7]]
    df.columns = ['date', 'open', 'close', 'low', 'high', 'volume']
    df[['high', 'low']] = df[['low', 'high']]
    df.columns = ['date', 'open', 'close', 'high', 'low', 'volume']
    return df


## SINA

def get_stock_price_by_past_days_sina(stock_id, days = None):
    '''
    stock_id: sh or sz + 6 numbers stock code
    '''
    if days is None:
        days = 30000
    headers = {
        'User-Agent': USER_AGENT,
        'referer': 'https://finance.sina.com.cn/',
    }
    url = 'http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol={}&scale=240&ma=no&datalen={}'.format(stock_id, days)
    # ma: moving average
    response = requests.get(url, headers = headers)
    res = json.loads(response.text)
    '''
    response: list with everday's data in a dictionary\n
    [{day(yyyy-dd-mm), open, high, low, close, volume}]\n
    [{str, str(float), str(float), str(float), str(float), str(int)}]\n
    volume: {volume}
    '''
    df = pd.DataFrame(res)
    df[['open', 'high', 'low', 'close']] = df[['open', 'close', 'high', 'low']]
    df.columns = ['date', 'open', 'close', 'high', 'low', 'volume']
    df['volume'] = round(df['volume'].astype('int64')/100)
    df['volume'] = df['volume'].astype('int64')
    return df


## SUMMARY
'''
get_stock_price_history_netease()     seems to stop service
get_stock_price_by_year_netease()     seems to stop service
get_stock_price_by_from_to_tencent()  GOOD
get_stock_price_by_year_tencent()     lack data of this & last year
get_stock_price_by_from_to_sohu()     lack data of some days for unknown reason
get_stock_price_by_past_days_sina()   GOOD
'''

def get_stock_price(stock_id):
    '''
    engine: get_stock_price_by_past_days_sina
    '''
    df = get_stock_price_by_past_days_sina(stock_id)
    return df


def update_stock_price(stock_id, to_date, days):
    '''
    engine: get_stock_price_by_from_to_tencent
    '''
    try:
        df = get_stock_price_by_from_to_tencent(stock_id, url_1 = True, to_date = to_date, days = days)
    except:
        df = get_stock_price_by_from_to_tencent(stock_id, url_1 = False, to_date = to_date, days = days)
    return df


def main():
    stock_id = 'sh600519'
    new = update_stock_price(stock_id, '', days = 10)
    print(new)


if __name__ == '__main__':
    main()