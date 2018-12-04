import os

from flask import Flask, render_template, request, flash, g,  session, url_for, redirect

from flaskapp.db import connect_db

def create_app(test_config = None):

  app = Flask(__name__, instance_relative_config = True)
  app.config.from_mapping(
    SECRET_KEY = 'frappe',
    DATABASE = os.path.join(app.instance_path, 'frappe_inventory.sqlite'),
  )

  if test_config is None:
    app.config.from_pyfile('config.py', silent = True)
  else:
    app.config.from_mapping(test_config)

  try:
    os.makedirs(app.instance_path)
  except OSError:
    pass

  @app.route('/')
  def home():
    return render_template('dashboard.html')

  @app.route('/products/', methods=('GET', 'POST'))
  def products():
    db = connect_db()
    products = db.execute('SELECT * FROM products')
    warehouses = db.execute('SELECT * FROM warehouses')

    if request.method == 'POST':
      p_id = request.form['p_id']
      p_name = request.form['p_name']
      p_qty = request.form['p_qty']

      error = None

      if db.execute('SELECT pid FROM products WHERE pid = ?', (p_id,)).fetchone() is not None:
        error = 'Product already registered.'
      else:
        db.execute('INSERT INTO products (pid, pname, pqty) VALUES (?, ?, ?)', (p_id, p_name, p_qty))
        db.commit()
        return redirect(url_for('products'))
      
      flash(error)

    return render_template('products.html', products = products, warehouses = warehouses)

  @app.route('/products/edit/', methods=['POST'])
  def editproducts():
    db = connect_db()

    if request.method == 'POST':
      p_id = request.form['p_id']
      p_name = request.form['p_name']
      p_qty = request.form['p_qty']

      db.execute('UPDATE products SET pname = ?, pqty = ? WHERE pid = ?', (p_name, p_qty, p_id))
      db.commit()
      return redirect(url_for('products'))

  @app.route('/warehouses/', methods=('GET', 'POST'))
  def warehouses():
    db = connect_db()
    warehouses = db.execute('SELECT w.wid, wname, wloc, pid, pqty FROM warehouses w LEFT JOIN warehouse_details wd ON w.wid = wd.wid')

    if request.method == 'POST':
      w_id = request.form['w_id']
      w_name = request.form['w_name']
      w_loc = request.form['w_loc']

      error = None

      if db.execute('SELECT wid FROM warehouses WHERE wid = ?', (w_id,)).fetchone() is not None:
        error = 'Warehouse already registered.'
      else:
        db.execute('INSERT INTO warehouses (wid, wname, wloc) VALUES (?, ?, ?)', (w_id, w_name, w_loc))
        db.commit()
        return redirect(url_for('warehouses'))
      
      flash(error)

    return render_template('warehouses.html', warehouses = warehouses)

  @app.route('/warehouses/edit/', methods=['POST'])
  def editwarehouses():
    db = connect_db()

    if request.method == 'POST':
      w_id = request.form['w_id']
      w_name = request.form['w_name']
      w_loc = request.form['w_loc']

      db.execute('UPDATE warehouses SET wname = ?, wloc = ? WHERE wid = ?', (w_name, w_loc, w_id))
      db.commit()
      return redirect(url_for('warehouses'))



  @app.route('/transfers/', methods=('GET', 'POST'))
  def transfers():
    db = connect_db()
    transfers = db.execute('SELECT * FROM transfers')

    if request.method == 'POST':
      p_id = request.form['p_id']
      t_qty = request.form['t_qty']
      t_to = request.form['t_to']
      t_from = request.form['t_from']

      if t_from == 'None':
        db.execute('INSERT INTO transfers (tto, pid, tqty) VALUES (?, ?, ?)', (t_to, p_id, t_qty))
        db.execute('UPDATE products SET pqty = pqty - ? WHERE pid = ?', (t_qty, p_id))

        if db.execute('SELECT * FROM warehouse_details WHERE wid = ? AND pid = ?', (t_to, p_id)).fetchone() is None:
          db.execute('INSERT INTO warehouse_details (wid, pid, pqty) VALUES (?, ?, ?)', (t_to, p_id, t_qty))
        else:
          db.execute('UPDATE warehouse_details SET pqty = pqty + ? WHERE wid = ? AND pid = ?', (t_qty, t_to, p_id))
        
        db.commit()
      else:
        w_id = request.form['w_id']

        db.execute('INSERT INTO transfers (tfrom, tto, pid, tqty) VALUES (?, ?, ?)', (t_from, t_to, p_id, t_qty))

        if db.execute('SELECT * FROM warehouse_details WHERE wid = ? AND pid = ?', (t_to, p_id)).fetchone() is None:
          db.execute('INSERT INTO warehouse_details (wid, pid, pqty) VALUES (?, ?, ?)', (t_to, p_id, t_qty))
        else:
          db.execute('UPDATE warehouse_details SET pqty = pqty + ? WHERE wid = ? AND pid = ?', (t_qty, t_to, p_id))


        flash('2nd case')

      
    return render_template('transfers.html', transfers = transfers)

  from . import db
  db.init_app(app)
  
  return app