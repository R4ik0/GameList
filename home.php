<?php
session_start();
if (!isset($_SESSION["user_id"])) {
  header("Location: index.php");
}
?>
<!DOCTYPE html>
<html>
<head>
  <title>GameList | Home</title>
  <link rel="stylesheet" href="css/style.css">
</head>
<body>

<header>
  <h2>GameList</h2>
  <div>
    <a href="profile.php">Profile</a>
    <a href="logout.php">Logout</a>
  </div>
</header>

<div class="container">
  <h2>Recommended for you</h2>
  <div id="reco-grid" class="grid"></div>
</div>

<script src="js/api.js"></script>
<script src="js/home.js"></script>
</body>
</html>
