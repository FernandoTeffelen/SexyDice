from app import create_app

# Cria a instância da aplicação usando a factory
app = create_app()

if __name__ == '__main__':
    # Roda a aplicação em modo de debug
    app.run(host='0.0.0.0', port=5000, debug=True)