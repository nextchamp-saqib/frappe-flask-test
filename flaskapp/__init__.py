import os

from flask import Flask, render_template, request, flash, url_for, redirect

from flaskapp.db import connect_db, init_app, init_db

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
      p_name = request.form['p_name']
      p_qty = request.form['p_qty']

      error = None

      if db.execute('SELECT pname FROM products WHERE pname = ?', (p_name,)).fetchone() is not None:
        error = 'Product already registered.'
      else:
        db.execute('INSERT INTO products (pname, pqty) VALUES (?, ?)', (p_name, p_qty))
        db.commit()
        return redirect(url_for('products'))
      
      flash(error)

    return render_template('products.html', products = products, warehouses = warehouses)

  @app.route('/products/edit/', methods=['POST'])
  def editproducts():
    db = connect_db()

    if request.method == 'POST':
      p_name = request.form['p_name']
      p_qty = request.form['p_qty']

      db.execute('UPDATE products SET pqty = ? WHERE pname = ?', (p_qty, p_name))
      db.commit()
      return redirect(url_for('products'))

  @app.route('/warehouses/', methods=('GET', 'POST'))
  def warehouses():
    db = connect_db()
    warehouses = db.execute('SELECT * FROM warehouses')
    warehouses_details = db.execute('SELECT w.wid, wname, wloc, pname, pqty FROM warehouses w LEFT JOIN warehouse_details wd ON w.wid = wd.wid')

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

    return render_template('warehouses.html', warehouses_details = warehouses_details, warehouses = warehouses)

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
      p_name = request.form['p_name']
      t_qty = request.form['t_qty']
      t_to = request.form['t_to']
      t_from = request.form['t_from']

      if t_from == 'None':
        ex_qty = db.execute('SELECT pqty FROM products WHERE pname = ?', (p_name,)).fetchone()

        if ex_qty['pqty'] < t_qty or t_qty < 0:
          flash('Enter quantity less than or equal to available quantity.')
          return redirect(url_for('products'))
        else:
          db.execute('INSERT INTO transfers (tto, pname, tqty) VALUES (?, ?, ?)', (t_to, p_name, t_qty))
          db.execute('UPDATE products SET pqty = pqty - ? WHERE pname = ?', (t_qty, p_name))

          if db.execute('SELECT * FROM warehouse_details WHERE wid = ? AND pname = ?', (t_to, p_name)).fetchone() is None:
            db.execute('INSERT INTO warehouse_details (wid, pname, pqty) VALUES (?, ?, ?)', (t_to, p_name, t_qty))
          else:
            db.execute('UPDATE warehouse_details SET pqty = pqty + ? WHERE wid = ? AND pname = ?', (t_qty, t_to, p_name))
          
          db.commit()
          return redirect(url_for('products'))
      else:
        w_id = request.form['w_id']

        ex_qty = db.execute('SELECT pqty FROM warehouse_details WHERE wid = ?, pname = ?', (w_id, p_name)).fetchone()

        if ex_qty['pqty'] < t_qty or t_qty < 0:
          flash('Enter appropriate quantity.')
          return redirect(url_for('warehouses'))
        else:
          db.execute('INSERT INTO transfers (tfrom, tto, pname, tqty) VALUES (?, ?, ?, ?)', (w_id, t_to, p_name, t_qty))

          if db.execute('SELECT * FROM warehouse_details WHERE wid = ? AND pname = ?', (t_to, p_name)).fetchone() is None:
            db.execute('INSERT INTO warehouse_details (wid, pname, pqty) VALUES (?, ?, ?)', (t_to, p_name, t_qty))
            db.execute('UPDATE warehouse_details SET pqty = pqty - ? WHERE wid = ? AND pname = ?', (t_qty, w_id, p_name))
          else:
            db.execute('UPDATE warehouse_details SET pqty = pqty + ? WHERE wid = ? AND pname = ?', (t_qty, t_to, p_name))
            db.execute('UPDATE warehouse_details SET pqty = pqty - ? WHERE wid = ? AND pname = ?', (t_qty, w_id, p_name))

          db.commit()
          return redirect(url_for('warehouses'))
        
    return render_template('transfers.html', transfers = transfers)

  init_app(app)
  with app.app_context():
    init_db()
  
  return app