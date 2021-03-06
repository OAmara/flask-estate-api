import models

from flask import Blueprint, request, jsonify
# enable encryption
from flask_bcrypt import generate_password_hash, check_password_hash
# enables cookies(session)
from flask_login import login_user, current_user, logout_user
from playhouse.shortcuts import model_to_dict


users = Blueprint('users', 'users')


## User routes

# user register route
@users.route('/register', methods=['POST'])
def register():
	payload = request.get_json()

	# make emails/ username case insensitive
	payload['email'] = payload['email'].lower()
	payload['username'] = payload['username'].lower()
	print(payload)

	try:
		# check DB if user exists
		models.User.get(models.User.email == payload['email'])

		### Find way to retrieve username with same query like below:
		# User.get(User.email == payload['email'], User.username == payload['username'])

		# if User.email == payload['email'] and User.username == payload['username']:
		# 	description = f"Account with Email {payload['email']} and Username {payload['username']} already exists",
		# elif User.username == payload['username']:
		# 	description = f"Account with Username {payload['username']} already exists",
		# else:
		# 	desctiption = f"Account with Email {payload['email']} already exists",

		return jsonify(
			data={},
			# description=description,
			description= f"Account with Email {payload['email']} already exists",
			status=401
		), 401
	#exinate models. , just DoesNotExist
	except models.DoesNotExist:

		created_user = models.User.create(
			email=payload['email'],
			username=payload['username'],
			firstname=payload['firstname'],
			lastname=payload['lastname'],
			hometown=payload['hometown'],
			secretquestion=payload['secretquestion'],
			secretanswer=payload['secretanswer'],
			password=generate_password_hash(payload['password'])
		)

		# login user
		login_user(created_user)

		# created user
		user_dict = model_to_dict(created_user)
		print(user_dict)

		user_dict.pop('password')
		user_dict.pop('secretanswer')
		user_dict.pop('secretquestion')

		return jsonify(
			data=user_dict,
			message=f"Successfully registered {user_dict['email']}",
			status=201,
		), 201


# user login route
@users.route('/login', methods=['POST'])
def login():
	payload = request.get_json()
	payload['email'] = payload['email'].lower()
	# payload['username'] = payload['username'].lower()
	try:
		# find by email
		user = models.User.get(models.User.email == payload['email'].lower())

		# if found, compare to password
		user_dict = model_to_dict(user)
		compare_password = check_password_hash(user_dict['password'], payload['password'])

		# if there is a match
		if compare_password:

			# cookie
			login_user(user)

			user_dict.pop('password')
			user_dict.pop('secretanswer')
			user_dict.pop('secretquestion')
			return jsonify(
				data=user_dict,
				message=f"Successfully logged in: {user_dict}",
				status=200
			), 200

		else:
			print('Password does not match user')

			return jsonify(
				data={},
				message='Email or Password is incorrect',
				status=401
			), 401

	# user not found
	except models.DoesNotExist:
		print('Username/ Email does not match')
		return jsonify(
			data={},
			message='Email or Password is incorrect',
			status=401
		), 401

# logout route to destroy cookie/ login_user
@users.route('/logout', methods=['GET'])
def logout():
	logout_user()
	return jsonify(
		data={},
		message="Successfully logged out of account.",
		status=200
	), 200



#### CREATE PUT route to edit user info ####


### CREATE DESTROY user route. (delete route would just delete user, destroy would destroy user and realtions i.e. searches)


