from flask import Flask, request
import MetaTrader5 as mt5

app = Flask(__name__)

# MT5-Verbindung aufbauen
mt5.initialize()
mt5.login(7103526, password="Kendinegel54!", server="FPMarkets-Demo")  # <-- Hier deine echten Daten eintragen!

@app.route('/', methods=['POST'])
def webhook():
    data = request.json

    signal = data.get("signal")       # "buy" oder "sell"
    symbol = data.get("symbol", "EURUSD")
    lot = float(data.get("contracts", 0.1))  # aus "contracts"

    if not mt5.symbol_select(symbol, True):
        return f"Symbol {symbol} konnte nicht aktiviert werden", 500

    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        return f"Tick-Fehler für {symbol}", 500

    if signal == "buy":
        price = tick.ask
        order_type = mt5.ORDER_TYPE_BUY
    elif signal == "sell":
        price = tick.bid
        order_type = mt5.ORDER_TYPE_SELL
    else:
        return "Ungültiges Signal", 400

    request_data = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": order_type,
        "price": price,
        "deviation": 10,
        "magic": 234000,
        "comment": "TV-Strategy",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request_data)

    if result.retcode != mt5.TRADE_RETCODE_DONE:
        return f"Fehler: {result.comment}", 500

    return "✅ Order gesendet", 200

if __name__ == "__main__":
    app.run(port=5000)