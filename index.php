<?php session_start(); ?>
<!DOCTYPE html>
<html>
<head>
  <title>GameList</title>
  <link rel="stylesheet" href="css/style.css">
</head>
<body class="container">

<h1>GameList</h1>
<p>Track, rate and discover new games</p>

<input id="username" placeholder="Username">
<input id="password" type="password" placeholder="Password">

<br><br>
<button onclick="login()">Login</button>
<button onclick="register()">Register</button>

<p id="error"></p>

<script src="js/api.js"></script>
<script src="js/auth.js"></script>
</body>
</html>
