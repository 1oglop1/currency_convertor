#TODO Add open source license! (now it time to tidy my room)


Currency Converter, source file fom ECB

positional arguments:
  <amount>    Amount to be converted
  <from>      Input currency
  <to>        Output currency(ies), EUR, CZK...

optional arguments:
  -h, --help  show this help message and exit
  -json       generate json output


usage: currency_converter.py [-h] [-json] <amount> <from> [<to> [<to> ...]] 
{
    "input": {
        "amount": 10.92,
        "currency": "GBP"
    },
    "output": {
        "EUR": 14.95,
        "USD": 17.05,
        "CZK": 404.82,
        .
        .
        .
    }
}

