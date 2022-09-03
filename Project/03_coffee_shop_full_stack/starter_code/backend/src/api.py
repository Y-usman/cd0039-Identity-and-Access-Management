import os
import sys
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@Completed uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''

db_drop_and_create_all()


# ROUTES
'''
@Completed implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks")
def get_drinks():
    drinks = Drink.query.all()

    if drinks is None:
        abort(404)

    return jsonify({
        'success': True,
        "drinks": [drink.short() for drink in drinks],
        "total_drinks": len(Drink.query.all())
    }), 200


'''
@Completed implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks-detail")
@requires_auth('get:drinks-detail')
def get_drinks_details(payload):
    drinks = Drink.query.filter(Drink.id).all()

    if drinks is None:
        abort(404)

    return jsonify({
        "success": True,
        'drinks': [drink.long() for drink in drinks]

    }), 200


'''
@Completed implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks", methods=['POST'])
@requires_auth('post:drinks')
def create_drinks(payload):
    data = request.get_json()
    title = data.get("title")
    recipe = data.get(str("recipe"))

    if title is None and recipe is None:
        abort(422)

    try:
        new_drink = Drink(title=title, recipe=json.dumps(recipe))
        new_drink.insert()

        return jsonify({
            'success': True,
            'drinks': [new_drink.long()]
        })

    except:
        abort(422)


'''
@Completed implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks/<int:drink_id>", methods=['PATCH'])
@requires_auth("patch:drinks")
def update_drinks(payload, drink_id):
    drink = Drink.query.get(drink_id)
    print(drink_id)
    if drink == None:
        abort(404, 'Drink not found')

    data = request.get_json()
    print(data)
    try:
        if 'title' not in data and 'recipe' not in data:
            abort(404)

        if 'title' in data: 
            drink.title = data['title']

        if 'recipe' in data:
            drink.recipe = json.dumps(data.get('recipe'))

        drink = drink.update()
    except:
        print(sys.exc_info())
        abort(500)

    return jsonify({
        'success': True,
        'drinks': [Drink.query.get(drink_id).long()]
    }), 200


'''
@Completed implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks/<int:drink_id>", methods=['DELETE'])
@requires_auth("delete:drinks")
def delete_drinks(payload, drink_id):
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
    if drink is None:
        abort(404)
            
    try:
        drink.delete()

        return jsonify({
            'success': True,
            'drink_id': drink_id
        }), 200
    except:
        print(sys.exc_info())
        abort(422)


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@Completed implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with appropriate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404
'''


@app.errorhandler(400)
def bad_request(error):
    return (
        jsonify({
            'success': False,
            'error': 400,
            'message': 'Error: bad request'
        }), 400
    )


@app.errorhandler(500)
def server_error(error):
    return (
        jsonify({
            'success': False,
            'error': 500,
            'message': 'Error: server error'
        }), 500
    )


@app.errorhandler(405)
def method_error(error):
    return (
        jsonify({
            'success': False,
            'error': 405,
            'message': 'Error: method error'
        }), 405
    )


'''
@Completed implement error handler for 404
    error handler should conform to general task above
'''


@app.errorhandler(404)
def not_found(error):
    return (
        jsonify({
            'success': False,
            'error': 404,
            'message': error.description
        }), 404
    )


@app.errorhandler(401)
def unauthorized(error):
    return (
        jsonify({
            'success': False,
            'error': 401,
            'message': error.description
        }), 401
    )

@app.errorhandler(403)
def forbidden(error):
    return (
        jsonify({
            'success': False,
            'error': 403,
            'message': 'Error: Forbidden'
        }), 403
    )


'''
@Completed implement error handler for AuthError
    error handler should conform to general task above
'''


@app.errorhandler(AuthError)
def handle_auth_error(error):
    return (
        jsonify({
            'success': False,
            'error': error.status_code,
            'message': error.error
        }),
        error.status_code
    )