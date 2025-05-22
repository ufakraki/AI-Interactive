# Ana dosya (örnek, Flask API başlatır)
# Geliştirme/test için kullanılabilir.
from api import app

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
