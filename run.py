from backend import create_app

backend = create_app()

if __name__ == '__main__':
    backend.run(debug=backend.config['DEBUG'])

