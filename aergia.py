from flask import Flask, render_template

app = Flask(__name__)
app.config.from_object('config.Config')
#  db.init_app(app)
#  api = Api(app)

with app.app_context():
    #  db.create_all()

    @app.route('/')
    def show_resumee_list():
        return render_template('pages/show_resumees.html')

    @app.route('/resumee/<int:resumee_id>')
    def show_resumee(resumee_id):
        # resumee_content = db.query
        resumee_content = "lorem ipsum etc."
        return render_template('pages/show_resumee.html',
                               resumee_id=resumee_id,
                               resumee_content=resumee_content)
        #  return "display resumee and the features next to each word" + str(resumee_id)


if __name__ == '__main__':
    app.run()
