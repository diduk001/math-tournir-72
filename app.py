from flask import Flask, render_template

app = Flask(__name__)
app.config['SECRET_KEY'] = "0d645377e31ab6b5847ec817bac4aaf8"


# Вызов обработчика базового шаблона base.html
@app.route("/base")
@app.route("/base.html")
def base():
    return render_template("base.html", title="base.html", block="")


def main():
    app.run()


if __name__ == '__main__':
    main()
