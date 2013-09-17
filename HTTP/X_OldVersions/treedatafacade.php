<?php

$server = "http://emo2.trinity.duke.edu:9000";
// $server = "http://localhost:9000";

// create a stream context
$opts = array(
  'http'=>array(
    'method'=>"GET",
    'header'=>"Accept-Encoding: gzip, deflate"
  )
);

$context = stream_context_create($opts);
$data = file_get_contents($server, FALSE, $context);
header("Content-encoding: gzip");
print_r($data);
?>
