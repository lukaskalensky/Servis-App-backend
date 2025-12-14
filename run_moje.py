from app_moje import create_app, db
from app_moje.modely import User

app = create_app()

# Zde můžete přidat příkazy pro Flask CLI pomocí app.cli.command()
# Například pro vytvoření databáze nebo seedování dat

# if __name__ == '__main__':
# Spuštění vývojového serveru (pro produkci použijte WSGI server jako Gunicorn)
# app.run(host='0.0.0.0', port=5000)  # Naslouchání na všech rozhraních
