from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError

from connect_db import connect_db, Error

app = Flask(__name__)
app.json.sort_keys = False 
ma = Marshmallow(app)


class CustomerSchema(ma.Schema):
    name = fields.String(required=True)
    email = fields.String(required=True)
    phone = fields.String(required=True)
   


    class Meta:  
        
        fields = ("name", "email", "phone")

@app.route('/')
def home():
    return "Welcome to my store management database"

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)

#retrive members from customer list
@app.route('/customers', methods=['GET'])
def get_customers(): 
    print("hello from the get")  
    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM Members"
        cursor.execute(query)
        customers = cursor.fetchall()
        return customers_schema.jsonify(customers)
    
    except Error as e:
        # error handling for connection/route issues
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        #checking again for connection object
        if conn and conn.is_connected():
            cursor.close()
            conn.close() 


# add customer 
@app.route('/customers', methods = ['POST']) 
def add_customer():
    try:
        customer_data = customer_schema.load(request.json)

    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    
    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()

        
        new_customer = (customer_data['name'], customer_data['email'], customer_data['phone'])
        query = "INSERT INTO Members (name, email, phone) VALUES (%s, %s, %s)"

        cursor.execute(query, new_customer)
        conn.commit()
        return jsonify({"message":"New customer added succesfully"}), 201
    
    except Error as e:
        print(f"error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close() 

# updating customer
@app.route('/customers/<int:id>', methods= ["PUT"])
def update_customer(id):
    try:
        customer_data = customer_schema.load(request.json)
        print(customer_data)

    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    
    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()

        updated_customer = (customer_data['name'], customer_data['email'], customer_data['phone'], id)

        query = "UPDATE Members SET name = %s, email = %s, phone = %s WHERE member_id = %s"
        cursor.execute(query, updated_customer)
        conn.commit()
        return jsonify({"message":"Customer details were succesfully updated!"}), 200
    
    except Error as e:
        print(f"error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

#delete customer 
@app.route('/customers/<int:id>', methods=["DELETE"])
def delete_customer(id):
    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()

        customer_to_remove = (id,)

        query = "SELECT * FROM Members WHERE member_id = %s"

        cursor.execute(query, customer_to_remove)
        customer = cursor.fetchone()
        if not customer:
            return jsonify({"error": "User does not exist"}), 404
        
        del_query = "DELETE FROM Members where member_id = %s"
        cursor.execute(del_query, customer_to_remove)
        conn.commit()

        return jsonify({"message":"Customer Removed succesfully"}), 200 
    except Error as e:
        print(f"error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        #checking again for connection object
        if conn and conn.is_connected():
            cursor.close()
            conn.close() 




class OrderSchema(ma.Schema):
    order_id = fields.Int()
    date = fields.Date()
    bottles = fields.Int()
    type = fields.String()
    members_id = fields.Int()
    class Meta:  
        
        fields = ("members_id", "date", "bottles", "type")

order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)

# make an order 
@app.route('/orders', methods=["POST"])
def place_order():
    try:
        order_data = order_schema.load(request.json) 

    except ValidationError as e:
        return jsonify(e.messages), 400
    
    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()

        query = "INSERT INTO orders (date, order_id) VALUES (%s, %s)"

        cursor.execute(query, (order_data['date'], order_data['customer_id']))
        conn.commit()
        return jsonify({"message": "Order was Placed, Thank you for your business!"}),201

    except Error as e:
        print(f"error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

    finally:
        if conn and conn.is_connected():
            cursor.close()
 
 
            conn.close() 
#to view my orders
@app.route("/orders", methods = ["GET"])
def get_orders():
    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM orders"
        cursor.execute(query)
        orders = cursor.fetchall()  

        return orders_schema.jsonify(orders)
    
    
    except Error as e:
        print(f"error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

        # update order
@app.route('/orders/<int:order_id>', methods= ["PUT"])
def update_order(order_id):
    try:
        order_data = order_schema.load(request.json)

    except ValidationError as e:
        return jsonify(e.messages), 400
    
    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()

        updated_order = (order_data["member_id"], order_data["date"], order_data["bottles"], order_data["type"], id)
        query = "UPDATE ORDERS SET date = %s, bottles = %s, type = %s, WHERE order_id = %s"
        cursor.execute (query, updated_order)
        conn.commit()
        return jsonify({"message": "order updated successfully"}), 200
    
    except Error as e:
        print(f"error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()



if __name__ == "__main__":
    app.run(debug=True)