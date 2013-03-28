<?php
$id = $_GET['id'];
$basis = $_GET['basis'];
print_r(file_get_contents("http://localhost:9000/scaleellipses?id=" . $id . "&basis=" . $basis));
// print_r(file_get_contents("http://emo2.trinity.duke.edu:9000/newdata?n=" . $n_pts));
?>
