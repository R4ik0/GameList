<?php
session_start();
if (!isset($_SESSION["user_id"])) {
  header("Location: index.php");
}
?>
<!DOCTYPE html>
<html>
<head>
  <title>GameList | Profile</title>
  <link rel="stylesheet" href="css/style.css">
</head>
<body>

<header>
  <h2>My Profile</h2>
  <div>
    <a href="home.php">Home</a>
    <a href="logout.php">Logout</a>
  </div>
</header>

<div class="container">
  <h2>My Games</h2>
  <div id="my-games"></div>
</div>

<script src="js/api.js"></script>
<script src="js/profile.js"></script>
</body>
</html>
