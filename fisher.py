from app import create_app

app = create_app()

if __name__ == '__main__':
    # app.run(app.run(host=app.config['HOST'], port=app.config['PORT'], debug=app.config['DEBUG'], threaded=False))
    app.run(app.run(port=app.config['PORT'], debug=app.config['DEBUG'], threaded=False))