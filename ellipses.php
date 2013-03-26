<?php
$n_pts = $_GET['n'];
print_r(file_get_contents("http://emo2.trinity.duke.edu:9000/newdata?n=" . $n_pts));
?>
