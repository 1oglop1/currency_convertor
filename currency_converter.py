import os, argparse, json, sys, requests
from lxml import etree as et
import datetime as dt


def update_local_rates():
    resp = requests.get('https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml')
    try:
        tree = et.fromstring(resp.text.encode('UTF-8')).getroottree()
    except et.XMLSyntaxError:
        print('unable to local rates, using old record', file=sys.stderr)
        return et.parse('local_rates.xml')
    tree.write('local_rates.xml')
    print('local rates updated')
    return tree


def non_eur_convert(amount, in_curr, currency_root, out_curr, path):
    in_curr = currency_root.find(path.format(c=in_curr)).attrib
    in_curr_rate = float(in_curr['rate'])
    in_curr_currency = in_curr['currency']

    for oc in out_curr:
        try:
            tmp_out_curr = currency_root.find(path.format(c=oc)).attrib
            #  print(tmp_out_curr)
            oc_rate = float(tmp_out_curr['rate'])
            oc_currency = tmp_out_curr['currency']
            wanted = (in_curr_rate / oc_rate) * amount
            # print("{am} {fr} = {res} {to}".format(am=amount, fr=in_curr_currency, res=wanted, to=oc_currency))
            yield oc_currency, wanted
        except (KeyError, AttributeError):
            if oc == 'EUR':
                r = in_curr
                wanted = amount / in_curr_rate
                # print("{am} {fr} = {res} {to}".format(am=amount, fr=in_curr_currency, res=wanted, to=oc))
                yield in_curr_currency, wanted
            else:
                print('Cannot convert from {fr} to {to}'.format(fr=in_curr_currency, to=oc), file=sys.stderr)
            continue


def from_eur_convert(amount, in_curr, currency_root, out_curr, path):
    for oc in out_curr:
        try:
            tmp_out_curr = currency_root.find(path.format(c=oc)).attrib
            #  print(tmp_out_curr)
            oc_rate = float(tmp_out_curr['rate'])
            oc_currency = tmp_out_curr['currency']
            wanted = oc_rate * amount
            # print("{am} {fr} = {res} {to}".format(am=amount, fr=in_curr_currency, res=wanted, to=oc_currency))
            yield oc_currency, wanted
        except (KeyError, AttributeError):
            if oc == 'EUR':
                # print("{am} {fr} = {res} {to}".format(am=amount, fr=in_curr_currency, res=wanted, to=oc))
                yield in_curr, amount
            else:
                print('Cannot convert from {fr} to {to}'.format(fr=in_curr, to=oc), file=sys.stderr)
            continue


def cmd_args():
    parser = argparse.ArgumentParser(description='Currency Converter, source file fom ECB')
    parser.add_argument('amount', metavar='<amount>', type=float,
                        help='Amount to be converted')
    parser.add_argument('fr', metavar='<from>',
                        help='Input currency')

    parser.add_argument('to', metavar='<to>', nargs='*',
                        default=['EUR', 'USD', 'JPY', 'BGN', 'CZK', 'DKK', 'GBP', 'HUF', 'PLN', 'RON', 'SEK', 'CHF',
                                 'NOK',
                                 'HRK', 'RUB', 'TRY', 'AUD', 'BRL', 'CAD', 'CNY', 'HKD', 'IDR', 'ILS', 'INR', 'KRW',
                                 'MXN',
                                 'MYR', 'NZD', 'PHP', 'SGD', 'THB', 'ZAR'],
                        help='Output currency(ies), EUR, CZK...')

    parser.add_argument('-json',
                        action='store_true',

                        help='generate json output')

    return parser.parse_args()


def main():
    args = cmd_args()
    args.to = list(map(lambda x: x.strip(',;'), args.to))

    # load currency file
    try:
        tree = et.parse('local_rates.xml')
    except OSError:  # can't parse file because it not exist
        tree = update_local_rates()

    root = tree.getroot()
    currency_time = root[2][0].attrib['time']

    now = dt.datetime.now()

    # update local XML in case of old info
    if (currency_time != now.date().isoformat()) and now.hour > 16 and now.weekday() not in (5, 6):
        print(currency_time)
        tree = update_local_rates()
        root = tree.getroot()

    cube = root[2][0]

    path = "{{http://www.ecb.int/vocabulary/2002-08-01/eurofxref}}Cube/.[@currency='{c}']"

    if args.fr == 'EUR':
        res_gen = from_eur_convert(args.amount, args.fr, cube, args.to, path)
    else:
        res_gen = non_eur_convert(args.amount, args.fr, cube, args.to, path)

    converted_dict = dict((k, v) for (k, v) in res_gen)

    output = {"input": {"amount": args.amount, "currency": args.fr},
              "output": converted_dict
              }

    if args.json:
        with open('currency.json', 'w') as oj:
            for chunk in json.JSONEncoder(sort_keys=True, indent=4).iterencode(output):
                oj.write(chunk)
    else:
        print(json.dumps(output, sort_keys=True, indent=4))


if __name__ == '__main__':
    main()
