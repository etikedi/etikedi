from flask import Flask, render_template

app = Flask(__name__)
app.config.from_object('config.Config')
#  db.init_app(app)
#  api = Api(app)

with app.app_context():
    #  db.create_all()

    @app.route('/')
    def show_cv_list():
        return render_template('pages/show_cvs.html')

    @app.route('/cv/<int:cv_id>')
    def show_cv(cv_id):
        return render_template('pages/show_cv.html', cv_id=cv_id)
        #  return "display cv and the features next to each word" + str(cv_id)


if __name__ == '__main__':
    app.run()
