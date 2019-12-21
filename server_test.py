from flask import Flask, request, make_response, redirect, url_for
from flask import render_template, session



app = Flask(__name__, template_folder='.')

@app.route('/test')
def test():
    html = render_template('track_test.html')
    response = make_response(html)
    return response

@app.route('/modify_item', methods=('GET', 'POST'))
def modify_item():
    image_path = 'https://cdn4.vectorstock.com/i/1000x1000/42/83/laptop-keyboard-letters-and-buttons-vector-19594283.jpg'
    e = ["e0", "price", "seller", "highes_bid", image_path, "e5", "title"]
    html = render_template('modify_item.html', entry=e, msg="none")
    response = make_response(html)
    return response






if __name__ == '__main__':
    app.run(host='0.0.0.0', port=12345, debug=True)