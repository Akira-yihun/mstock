import datetime
from flask import render_template, session, redirect, url_for, flash, request, jsonify
from . import main
from .forms import EditProfileForm, StockSearchForm
from .. import db
from ..models import User, Stock, Comment, Role, StockClose, StockSelection
from . import StockData, StockRisk
import pandas as pd
from flask_login import current_user, login_required
import math
import numpy as np
import json
from scipy.stats import gaussian_kde
from jinja2 import Template


def update_stock_price_table(stock):
    '''
    stock: instance of Stock
    '''
    prices = stock.closes
    plast = prices.order_by(StockClose.tradedate.desc()).first()
    plastdate = plast.tradedate
    datenow = datetime.datetime.now().date()
    daysafter = (datenow - plastdate).days
    dayone = datetime.timedelta(days = 1)
    needupdate = False
    for i in range(daysafter-1):
        d = plastdate + (i+1)*dayone
        if d.weekday() < 5:
            needupdate = True
            break
    if needupdate:
        precent = StockData.update_stock_price(stock.stockid, '', daysafter + 1)
        for row in precent.itertuples():
            date = [int(i) for i in getattr(row, 'date').split('-')]
            date = datetime.date(date[0], date[1], date[2])
            if date > plastdate:
                stockclose = StockClose(
                    stockid = stock.stockid,
                    tradedate = date,
                    open = getattr(row, 'open'),
                    close = getattr(row, 'close'),
                    high = getattr(row, 'high'),
                    low = getattr(row, 'low'),
                    volume = int(float(getattr(row, 'volume')))
                )
                db.session.add(stockclose)
        db.session.commit()


@main.route('/', methods = ['GET', 'POST'])
def index():
    form = StockSearchForm()
    if form.validate_on_submit():
        stockid = form.stockid.data
        stock = Stock.query.filter_by(stockid = stockid).first()
        if stock is not None:
            return redirect(url_for('main.stock_detail', stockid = stockid))
        else:
            basic = StockData.get_stock_basic_info(stockid)
            if not basic['good']:
                flash('沉舟侧畔千帆过，换一只股票试一试')
                return redirect(url_for('main.index'))
            else:
                newstock = Stock(
                    stockid = stockid,
                    stockname = basic['stockname'],
                    stocktype = basic['type']
                )
                db.session.add(newstock)
                # db.session.commit()
                history = StockData.get_stock_price(stockid)
                for row in history.itertuples():
                    date = [int(i) for i in getattr(row, 'date').split('-')]
                    date = datetime.date(date[0], date[1], date[2])
                    stockclose = StockClose(
                        stockid = stockid,
                        tradedate = date,
                        open = getattr(row, 'open'),
                        close = getattr(row, 'close'),
                        high = getattr(row, 'high'),
                        low = getattr(row, 'low'),
                        volume = int(float(getattr(row, 'volume')))
                    )
                    db.session.add(stockclose)
                db.session.commit()
                return redirect(url_for('main.stock_detail', stockid = stockid))
    stocks = Stock.query.all()
    return render_template('stock/index.html', stocks = stocks, form = form)


@main.route('/personal', methods = ['GET', 'POST'])
@login_required
def personal_index():
    form = StockSearchForm()
    if form.validate_on_submit():
        stockid = form.stockid.data
        stock = Stock.query.filter_by(stockid = stockid).first()
        if stock is not None:
            return redirect(url_for('main.stock_detail', stockid = stockid))
        else:
            basic = StockData.get_stock_basic_info(stockid)
            if not basic['good']:
                flash('沉舟侧畔千帆过，换一只股票试一试')
                return redirect(url_for('main.personal_index'))
            else:
                newstock = Stock(
                    stockid = stockid,
                    stockname = basic['stockname'],
                    stocktype = basic['type']
                )
                db.session.add(newstock)
                # db.session.commit()
                history = StockData.get_stock_price(stockid)
                for row in history.itertuples():
                    date = [int(i) for i in getattr(row, 'date').split('-')]
                    date = datetime.date(date[0], date[1], date[2])
                    stockclose = StockClose(
                        stockid = stockid,
                        tradedate = date,
                        open = getattr(row, 'open'),
                        close = getattr(row, 'close'),
                        high = getattr(row, 'high'),
                        low = getattr(row, 'low'),
                        volume = int(float(getattr(row, 'volume')))
                    )
                    db.session.add(stockclose)
                db.session.commit()
                return redirect(url_for('main.stock_detail', stockid = stockid))
    stockselections = StockSelection.query.filter_by(userid = current_user.userid).all()
    stocks = []
    for item in stockselections:
        stocks.append(Stock.query.filter_by(stockid = item.stockid).first())
    return render_template('stock/index.html', stocks = stocks, form = form)



@main.route('/stock/<stockid>', methods = ['GET', 'POST'])
def stock_detail(stockid):
    stock = Stock.query.filter_by(stockid = stockid).first()
    return render_template('stock/detail.html', stock = stock)


@main.route('/json/stockclose', methods = ['GET', 'POST'])
def get_stockclose_json():
    if request.method == 'POST':
        stockid = request.form.get('stockid')
        stock = Stock.query.filter_by(stockid = stockid).first()
        update_stock_price_table(stock)
        prices = stock.closes
        prices = [p.json_data() for p in prices.all()]
        return jsonify(prices)


@main.route('/stock/add/<stockid>')
@login_required
def stock_add(stockid):
    stock = StockSelection.query.filter_by(stockid = stockid).first()
    if stock is not None:
        flash('已闻清比圣，已得何必复求。')
    else:
        selectstock = StockSelection(
            userid = current_user.userid,
            stockid = stockid,
        )
        db.session.add(selectstock)
        db.session.commit()
    return redirect(url_for('main.personal_index'))


@main.route('/stock/delete/<stockid>')
@login_required
def stock_delete(stockid):
    stock = StockSelection.query.filter_by(stockid = stockid).first()
    if stock is not None:
        db.session.delete(stock)
        db.session.commit()
    else:
        flash('菩提本无树，本无何谈摆脱。')
    return redirect(url_for('main.personal_index'))


@main.route('/stock/riskanalysis', methods = ['GET', 'POST'])
@login_required
def stock_analysis():
    if request.method == 'POST':
        stockids = request.form.getlist('astock')
        if len(stockids) == 0:
            flash('请至少选择一只股票')
            return redirect(url_for('main.personal_index'))
        days = int(request.form.get('days'))
        stocks = Stock.query.filter(Stock.stockid.in_(stockids)).all()
        for stock in stocks:
            update_stock_price_table(stock)
            prices = stock.closes
            if prices.count() < days:
                flash('试玉要烧三日满，再等等看吧。')
                return redirect(url_for('main.personal_index'))
        columns = ['stockid', 'stockname', 'entropy', 'utility', 'variance', 'skewness', 's_entropy']
        riskitems = pd.DataFrame(columns = columns)
        ratesjson = {}
        kdejson = {}
        kdejson['x'] = list(np.linspace(-0.1, 0.1, 201))
        for stock in stocks:
            prices = stock.closes
            prices = prices.order_by(StockClose.tradedate.desc()).limit(days)
            ps = [[p.tradedate, p.close] for p in prices.all()]
            df = pd.DataFrame(data = ps, columns = ['date', 'close'])
            df = df.iloc[::-1]
            closes = df['close']
            rate = [math.log(closes[i]/closes[i-1]) for i in range(1, len(closes))]
            #rate = [closes[i]/closes[i-1]-1 for i in range(1, len(closes))]
            ratesjson[stock.stockid+ ' ' + stock.stockname] = rate.copy()
            kdefunc = gaussian_kde(rate)
            kdejson[stock.stockid+ ' ' + stock.stockname] = list(kdefunc(kdejson['x']))
            rate.insert(0, np.NaN)
            df['rate'] = rate
            risk = StockRisk.get_item_of_one(df, stock.stockid, stock.stockname)
            riskitems.loc[len(riskitems)] = risk
        riskitems = StockRisk.get_items(riskitems)
        return render_template('stock/analysis.html', riskitems = riskitems, ratesjson = ratesjson, kdejson = kdejson, days = days)
    return redirect(url_for('main.personal_index'))


@main.route('/stock/riskanalysis/portfolio', methods = ['GET', 'POST'])
@login_required
def stock_portfolio():
    if request.method == "POST":
        data = json.loads(request.get_data())
        stockrisks = data['stockrisks']
        sortedsr = sorted(stockrisks.items(), key = lambda x: x[1])
        days = int(data['days'])
        ratedf = pd.DataFrame()
        stocks = []
        for item in sortedsr[:int(data['stocknum'])]:
            stock = Stock.query.filter_by(stockid = item[0]).first()
            stocks.append(stock.stockid + ' ' + stock.stockname)
            prices = stock.closes
            prices = prices.order_by(StockClose.tradedate.desc()).limit(days)
            closes = [p.close for p in prices.all()]
            closes.reverse()
            rate = [math.log(closes[i]/closes[i-1]) for i in range(1, len(closes))]
            #rate = [closes[i]/closes[i-1]-1 for i in range(1, len(closes))]
            ratedf[item[0]] = rate
        res = StockRisk.efficient_frontier(ratedf)
        return [res['resstdlis'], stocks]
    return redirect(url_for('main.personal_index'))


@main.route('/stock/comment/<stockid>', methods = ['GET', 'POST'])
@login_required
def stock_comment(stockid):
    if request.method == "POST":
        data = json.loads(request.get_data())
        content = data['content']
        userid = current_user.userid
        response = {'status': True}
        if len(data) == 2:
            comment = Comment(
                userid = userid,
                content = content,
                stockid = stockid
            )
        else:
            if data['directreply'] == 'main':
                comment = Comment(
                    userid = userid,
                    content = content,
                    stockid = stockid,
                    reply = data['reply']
                )
            else:
                comment = Comment(
                    userid = userid,
                    content = content,
                    stockid = stockid,
                    reply = data['reply'],
                    directreply = data['directreply']
                )
        db.session.add(comment)
        db.session.commit()
        return response
    stock = Stock.query.filter_by(stockid = stockid).first()
    comments = stock.comments
    mcoms = comments.filter_by(reply = None).all()
    td = datetime.datetime.now() - datetime.datetime.utcnow()
    return render_template('/stock/comment.html', mcoms = mcoms, stock = stock, td = td)