<?php
$id = $_GET['id'];
$basis = $_GET['basis'];

// create a stream context
$opts = array(
  'http'=>array(
    'method'=>"GET",
    'header'=>"Accept-Encoding: gzip, deflate"
  )
);

$context = stream_context_create($opts);
$data = file_get_contents("http://emo2.trinity.duke.edu:9000/scaleellipses?id=" . $id . "&basis=" . $basis, FALSE, $context);
// print_r(file_get_contents("http://localhost:9000/scaleellipses?id=" . $id . "&basis=" . $basis));
header("Content-encoding: gzip");
print_r($data);
?>
