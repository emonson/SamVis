<?php

// create a stream context
$opts = array(
  'http'=>array(
    'method'=>"GET",
    'header'=>"Accept-Encoding: gzip, deflate"
  )
);

$context = stream_context_create($opts);
$data = file_get_contents("http://emo2.trinity.duke.edu:9000", FALSE, $context);
// $data = file_get_contents("http://localhost:9000", FALSE, $context);
header("Content-encoding: gzip");
print_r($data);
?>
