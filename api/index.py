from flask import Flask, render_template_string
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

app = Flask(__name__)

def get_fractal_resistance(df):
    if len(df) < 6: return None
    for i in range(len(df) - 4, 2, -1):
        if (df['High'].iloc[i] > df['High'].iloc[i-1] and 
            df['High'].iloc[i] > df['High'].iloc[i-2] and 
            df['High'].iloc[i] > df['High'].iloc[i+1] and 
            df['High'].iloc[i] > df['High'].iloc[i+2]):
            return df['High'].iloc[i]
    return None

def cek_breakout(simbol):
    try:
        ticker = yf.Ticker(simbol)
        # Ambil data lebih sedikit untuk efisiensi (1mo cukup)
        df = ticker.history(period="1mo", interval="1d")
        if df.empty or len(df) < 6: return None
        
        resistance = get_fractal_resistance(df)
        if resistance is None: return None
        
        high_hari_ini = df['High'].iloc[-1]
        close_hari_ini = df['Close'].iloc[-1]
        close_kemarin = df['Close'].iloc[-2]
        volume_hari_ini = df['Volume'].iloc[-1]
        high_kemarin = df['High'].iloc[-2]

        # Hitung % Perubahan Harga vs Closing Kemarin
        change_pct = ((close_hari_ini - close_kemarin) / close_kemarin) * 100

        if high_hari_ini > resistance and high_kemarin <= resistance:
            if volume_hari_ini > 5000000:
                status = "CLOSE ABOVE" if close_hari_ini > resistance else "HIGH ONLY"
                return {
                    "simbol": simbol.replace('.JK', ''), 
                    "status": status, 
                    "price": close_hari_ini,
                    "change": change_pct,
                    "vol": volume_hari_ini, 
                    "res": resistance
                }
        return None
    except Exception as e:
        return None

@app.route('/')
def home():
    # Contoh list diperpendek (Gunakan list lengkap Anda di sini)
saham_pilihan = [
     'MBMA.JK', 'DOOH.JK', 'DEWA.JK', 'ARCI.JK', 'EMAS.JK', 'CUAN.JK', 'TPIA.JK', 'DSSA.JK', 'BIPI.JK', 'CDIA.JK', 'HRTA.JK', 'COIN.JK', 'EMTK.JK', 'NICL.JK', 'BUVA.JK', 'BELL.JK', 'JGLE.JK', 'OASA.JK', 'RAJA.JK', 'AKRA.JK'] 
    
    results = []
    for s in saham_pilihan:
        res = cek_breakout(s)
        if res: results.append(res)

    # Tentukan timezone Jakarta (WIB)
    timezone = pytz.timezone('Asia/Jakarta')
    # Ambil waktu sekarang sesuai timezone tersebut
    now = datetime.now(timezone).strftime("%Y-%m-%d %H:%M:%S WIB")

    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Stock Breakout Scanner</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
            body { font-family: 'Inter', sans-serif; background-color: #f3f4f6; }
        </style>
    </head>
    <body class="p-4 md:p-10">
        <div class="max-w-5xl mx-auto">
            <div id="capture-area" class="bg-white p-8 rounded-xl shadow-lg border border-gray-200">
                <div class="flex justify-between items-start mb-6">
                    <div>
                        <h1 class="text-3xl font-bold text-gray-800">🚀 Fractal Breakout Watchlist</h1>
                        <p class="text-gray-500 mt-1">Bursa Efek Indonesia (IDX)</p>
                    </div>
                    <div class="text-right">
                        <p class="text-sm font-semibold text-gray-400 uppercase tracking-wider">Waktu Screening</p>
                        <p class="text-lg font-mono text-blue-600">{{ timestamp }}</p>
                    </div>
                </div>

                <div class="overflow-hidden rounded-lg border border-gray-200">
                    <table class="w-full text-left border-collapse">
                        <thead class="bg-gray-50">
                            <tr>
                                <th class="px-6 py-4 text-sm font-semibold text-gray-700 uppercase">Ticker</th>
                                <th class="px-6 py-4 text-sm font-semibold text-gray-700 uppercase">Status</th>
                                <th class="px-6 py-4 text-sm font-semibold text-gray-700 uppercase text-right">Price</th>
                                <th class="px-6 py-4 text-sm font-semibold text-gray-700 uppercase text-right">Change (%)</th>
                                <th class="px-6 py-4 text-sm font-semibold text-gray-700 uppercase text-right">Up Fractal</th>
                                <th class="px-6 py-4 text-sm font-semibold text-gray-700 uppercase text-right">Volume</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-gray-200">
                            {% for r in results %}
                            <tr class="hover:bg-gray-50 transition-colors">
                                <td class="px-6 py-4 font-bold text-gray-900">
                                    <div class="flex items-center gap-2">
                                        <span class="text-gray-900">{{ r.simbol }}</span>
                                        <div class="flex gap-1 text-xs">
                                            <a href="https://www.tradingview.com/chart/?symbol=IDX%3A{{ r.simbol }}"
                                               target="_blank" rel="noopener noreferrer"
                                               class="bg-blue-50 text-blue-600 hover:bg-blue-100 px-2 py-0.5 rounded border border-blue-200 font-semibold"
                                               title="Buka di TradingView">
                                                TV
                                            </a>
                                            <a href="https://stockbit.com/symbol/{{ r.simbol }}/chartbit"
                                               target="_blank" rel="noopener noreferrer"
                                               class="bg-emerald-50 text-emerald-600 hover:bg-emerald-100 px-2 py-0.5 rounded border border-emerald-200 font-semibold"
                                               title="Buka di Stockbit Chartbit">
                                                SB
                                            </a>
                                        </div>
                                    </div>
                                </td>
                                <td class="px-6 py-4">
                                    <span class="px-3 py-1 rounded-full text-xs font-bold {{ 'bg-green-100 text-green-700' if r.status == 'CLOSE ABOVE' else 'bg-yellow-100 text-yellow-700' }}">
                                        {{ r.status }}
                                    </span>
                                </td>
                                <td class="px-6 py-4 text-right font-mono">{{ "{:,.0f}".format(r.price) }}</td>
                                <td class="px-6 py-4 text-right font-bold {{ 'text-green-600' if r.change > 0 else 'text-red-600' }}">
                                    {{ "+" if r.change > 0 }}{{ "%.2f"|format(r.change) }}%
                                </td>
                                <td class="px-6 py-4 text-right text-gray-600 font-mono">{{ "{:,.0f}".format(r.res) }}</td>
                                <td class="px-6 py-4 text-right text-gray-600 font-mono">{{ "{:,.0f}".format(r.vol) }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                
                {% if not results %}
                <div class="text-center py-12">
                    <p class="text-gray-400 italic">Tidak ada saham yang memenuhi kriteria breakout saat ini.</p>
                </div>
                {% endif %}

                <div class="mt-6 pt-6 border-t border-gray-100 text-xs text-gray-400 flex justify-between">
                    <span>Screener by MOSYA (https://stockbit.com/mohsyaifudin93)</span>
                    <span>Data provided by Yahoo Finance</span>
                </div>
            </div>

            <div class="mt-8 flex justify-center">
                <button onclick="downloadImage()" class="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-full font-bold shadow-lg transition-all transform hover:scale-105 flex items-center gap-2">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd" />
                    </svg>
                    Simpan Hasil (JPEG)
                </button>
            </div>
        </div>

        <script>
            function downloadImage() {
                const element = document.getElementById('capture-area');
                html2canvas(element, {
                    scale: 2, // Kualitas lebih tinggi
                    backgroundColor: "#f3f4f6"
                }).then(canvas => {
                    const link = document.createElement('a');
                    link.download = 'Screening-Saham-' + new Date().getTime() + '.jpg';
                    link.href = canvas.toDataURL('image/jpeg', 0.9);
                    link.click();
                });
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html, results=results, timestamp=now)

if __name__ == '__main__':
    app.run(debug=True)
