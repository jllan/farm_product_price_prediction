from flask import render_template, request, redirect, url_for, flash, jsonify
from app import app
from .spider import PriceSpider
from .model import Prices, PriceForm

@app.route('/')
def index():
    return render_template('select.html')
    # return render_template('test.html')


@app.route('/get')
@app.route('/get/<string:product>/<string:market>')
def get_data(product='西红柿', market='南京农副产品物流中心'):
    prices = Prices.objects(title=product, market=market).order_by('date')
    if prices:
        # print(dir(prices))
        flash('{} {}的数据已存在，工作有{}条'.format(market, product, prices.count))
        return redirect(url_for('index'))
    flash('开始采集{} {}的数据'.format(market, product))
    spider = PriceSpider(product, market)
    try:
        spider.run()
    except Exception as e:
        message = '数据采集失败:' + str(e)
    else:
        message = '数据采集成功'
    flash(message=message)
    return redirect(url_for('show_table'))


@app.route('/show_table')
@app.route('/show_table/<int:page>')
@app.route('/show_table/<string:product>/<string:market>')
@app.route('/show_table/<string:product>/<string:market>/<int:page>')
def show_table(product='西红柿', market='南京农副产品物流中心', page=1):
    # prices = Prices.objects.order_by('date')
    prices = Prices.objects(title=product, market=market).order_by('date').paginate(page=page, per_page=50)
    if not prices.total:
        flash('未找到{} {}的数据，请先点击启动爬虫按钮来爬取该数据'.format(market, product))
        return redirect(url_for('index'))
    return render_template('table.html', prices=prices)


@app.route('/show_chart/')
# @app.route('/show_chart/<int:page>')
# @app.route('/show_chart/<string:product>/<string:market>')
# @app.route('/show_chart/<string:product>/<string:market>/<int:page>')
def show_chart():
    market = request.args.get('market', '南京农副产品物流中心', type=str)
    product = request.args.get('product', '西红柿', type=str)
    print(market, product)
    # prices = Prices.objects().order_by('date')
    prices = Prices.objects(title=product, market=market).order_by('date')
    # prices = Prices.objects(title=product, market=market).order_by('date').paginate(page=page, per_page=50)
    print(prices)
    if not prices:
        flash('未找到{} {}的数据，请先点击启动爬虫按钮来爬取该数据'.format(market, product))
        return redirect(url_for('index'))
    date_list = [i['date'] for i in prices]
    price_list = [i['price'] for i in prices]
    d = {'product': product,
         'market': market,
         'prices': price_list,
         'dates': date_list
         }
    return jsonify(d)
    # return render_template('test.html', prices=prices)

