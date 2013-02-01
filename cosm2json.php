<?php
header('Content-Type: application/json');

date_default_timezone_set("America/Chicago");

$cosm_base = "http://api.cosm.com/v2/";
$cosm_key  = "";

$feed = 95557;

$allowed_args = array( "start", "end", "duration", "find_previous", "limit", "interval_type", "interval" );
$used_args = array();

foreach($allowed_args as $arg) {
   if(isset($_GET[$arg])) {
      array_push($used_args,$arg);
   }
}

$url = $cosm_base."feeds/$feed";

$set_streams = false;
$stream = "CurrentTemperature";
if(isset($_GET['stream'])) {
   $stream = $_GET['stream'];
}
$url .= "/datastreams/$stream";

$url .= ".csv?utm_source=pine";

foreach($used_args as $arg) {
    $url .= "&$arg=".$_GET[$arg];
}

$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
curl_setopt($ch, CURLOPT_HEADER, 0);
curl_setopt($ch, CURLOPT_HTTPHEADER, array("X-ApiKey: $cosm_key"));
$response = curl_exec($ch);
if(curl_errno($ch)) {
  print json_encode(array("error"=>"Unable to get data","message"=>curl_error($ch),"body"=>$response));
  exit(1);
}

if(strpos($response,",") < 2) {
  print json_encode(array("error"=>"Unable to get data","message"=>curl_error($ch),"body"=>$response));
  exit(1);
}

curl_close($ch);

$fh = fopen('php://temp', 'w+');
fwrite($fh, $response);
rewind($fh);

$data = array();

while (($point = fgetcsv($fh, 1000, ",")) !== FALSE) {
    if(is_numeric($point[1])) {
      settype($point[1],"float");
      $d = strtotime($point[0]);
      $du = (int)(date("U",$d))*1000;
      $row = array($du,$point[1]);
      array_push($data,$row);
    }
}
       
fclose($fh);

//print_r($data);
print json_encode($data);
?>
